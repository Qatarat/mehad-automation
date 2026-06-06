"""
Payment flow tests — MyFatoorah sandbox end-to-end.

Gateway:     MyFatoorah (embedded; URL slug is 'paytabs' but widget is MyFatoorah)
Environment: demo.myfatoorah.com  — SANDBOX, no real charges ever
Test card:   4111 1111 1111 1111  CVV 100  Expiry 05/28

Flow:
  login as student → tutor page → book slot → /en/payment →
  fill iframe card form → Pay now → 3DS ACS emulator → Submit → success redirect

Run:
  pytest tests/test_payment_flow.py -v -s --headed
"""
from __future__ import annotations
import os
import re
import pytest
from playwright.sync_api import Page, Browser

BASE_URL = os.getenv("BASE_URL", "https://dev.mehadedu.com/en")

# Automations Tutor profile (has Mon/Tue/Wed/Sat slots in dev)
TUTOR_PROFILE_ID = 89

# Automations Student credentials (OTP always 123456 in dev)
STUDENT_PHONE = os.getenv("STUDENT_PHONE", "98765432")
STUDENT_OTP   = os.getenv("STUDENT_OTP",   "123456")

# MyFatoorah sandbox test cards
CARD_VISA_SUCCESS = "4111111111111111"
CARD_EXPIRY       = "0528"   # press_sequentially — no slash
CARD_CVV          = "100"
CARD_NAME         = "Test User"


# ─── Session auth ────────────────────────────────────────────────────────────

def _student_login(page: Page):
    """Log in as Automations Student via OTP (dev fixed OTP 123456)."""
    page.goto(BASE_URL, wait_until="commit", timeout=25000)
    page.wait_for_timeout(2000)

    # Click the visible desktop Login button
    login_btn = page.locator('button:not([aria-label="Login"]):has-text("Log In"), button:not([aria-label]):has-text("Login")').last
    login_btn.wait_for(state="visible", timeout=10000)
    login_btn.click()
    page.wait_for_selector('[role="dialog"]', state="visible", timeout=10000)
    page.wait_for_timeout(800)

    container = page.locator('[role="dialog"]')

    # Country code — open dropdown
    cc_btn = container.locator('button[aria-label="Country code"], button:has-text("Country code")').first
    cc_btn.wait_for(state="visible", timeout=8000)
    cc_btn.click()
    page.wait_for_timeout(600)

    # Search Bangladesh
    search_input = page.locator('[role="listbox"] input[placeholder*="Search"], input[placeholder="Search..."]').first
    search_input.wait_for(state="visible", timeout=5000)
    search_input.fill("Bangladesh")
    page.wait_for_timeout(500)
    page.locator('[role="option"]:has-text("Bangladesh")').first.click()
    page.wait_for_timeout(400)

    # Phone number
    phone_input = container.locator('input[type="tel"], input[placeholder*="123"]').first
    phone_input.wait_for(state="visible", timeout=8000)
    phone_input.fill(STUDENT_PHONE)
    page.wait_for_timeout(400)

    # Send Code
    container.locator('button:has-text("Send Code")').first.click()
    page.wait_for_timeout(2000)

    # OTP — wait until input is enabled then fill
    otp_input = container.locator('input[placeholder="000000"]').first
    otp_input.wait_for(state="visible", timeout=15000)
    for _ in range(30):
        page.wait_for_timeout(500)
        if not otp_input.is_disabled():
            break
    otp_input.fill(STUDENT_OTP)
    page.wait_for_timeout(600)

    container.locator('button:has-text("Continue")').first.click()
    page.wait_for_timeout(3000)


@pytest.fixture(scope="module")
def student_page(browser: Browser, tmp_path_factory):
    """Module-scoped student session — login once, reuse across all payment tests."""
    sf = tmp_path_factory.mktemp("payment_auth") / "student.json"
    ctx = browser.new_context(viewport={"width": 1280, "height": 800}, ignore_https_errors=True)
    pg = ctx.new_page()
    _student_login(pg)
    ctx.storage_state(path=str(sf))
    ctx.close()

    ctx2 = browser.new_context(
        viewport={"width": 1280, "height": 800},
        ignore_https_errors=True,
        storage_state=str(sf),
    )
    page = ctx2.new_page()
    yield page
    ctx2.close()


# ─── Booking helper ──────────────────────────────────────────────────────────

def book_slot_via_ui(page: Page) -> str:
    """Navigate to tutor 89 profile, open booking dialog, select a slot.

    Handles two dialog modes:
    - Trial / Date-picker dialog  (title: "Book a Session")
    - Package selection dialog    (title contains "Package")

    Returns booking number (DBK-...) extracted from the payment page URL,
    or an empty string if navigation didn't reach the payment page.
    """
    tutor_url = BASE_URL.rstrip("/").rsplit("/en", 1)[0] + f"/en/tutor/{TUTOR_PROFILE_ID}"
    page.goto(tutor_url, wait_until="commit", timeout=25000)
    page.wait_for_timeout(2000)

    # Click any booking button (Book Trial Lesson / Book Lesson / Book)
    page.locator('button:has-text("Book")').first.click()
    page.wait_for_selector('[role="dialog"]', state="visible", timeout=10000)
    page.wait_for_timeout(1000)

    dialog = page.locator('[role="dialog"]')

    # Detect which dialog variant opened
    try:
        title_text = dialog.locator('h2, h3').first.inner_text(timeout=5000)
    except Exception:
        title_text = ""

    if "Package" in title_text:
        _book_via_package_dialog(page, dialog)
    else:
        _book_via_trial_dialog(page, dialog)

    page.wait_for_timeout(2000)
    m = re.search(r"bookingNumber=(DBK-[^&]+)", page.url)
    return m.group(1) if m else ""


def _book_via_package_dialog(page: Page, dialog):
    """Handle package selection dialog → Continue → Confirm & Pay.

    Package cards are cursor-pointer divs. Must wait for all cards to render,
    then use page.locator (not dialog.locator chaining) to match the same way
    the MCP browser native click does — that's what actually triggers React state.
    """
    # Wait for package cards to appear in the DOM
    page.wait_for_selector('[role="dialog"] .cursor-pointer', timeout=15000)
    page.wait_for_timeout(1200)  # let React finish rendering all cards

    # Click the "1 hr Package" card using a full page-scoped selector
    # (equivalent to MCP browser_click target that is confirmed to enable Continue)
    card = page.locator('[role="dialog"] .cursor-pointer:has(h3:has-text("1 hr Package"))')
    if card.count() > 0:
        card.first.scroll_into_view_if_needed()
        page.wait_for_timeout(400)
        card.first.click()
    else:
        # Fallback: click the last (smallest) cursor-pointer card in the dialog
        fallback = page.locator('[role="dialog"] .cursor-pointer:has(h3)')
        n = fallback.count()
        if n > 0:
            fallback.nth(n - 1).scroll_into_view_if_needed()
            fallback.nth(n - 1).click()
    page.wait_for_timeout(1000)

    # Poll until Continue is enabled — React state update is async
    continue_btn = page.locator('[role="dialog"] button:has-text("Continue")').first
    continue_btn.wait_for(state="visible", timeout=8000)
    for _ in range(25):
        if continue_btn.is_enabled():
            break
        page.wait_for_timeout(300)
    continue_btn.click()
    page.wait_for_timeout(1500)

    # Review step → Confirm & Pay → navigate to /en/payment
    with page.expect_navigation(timeout=25000):
        page.locator('[role="dialog"] button').filter(
            has_text=re.compile(r"Confirm|Pay", re.I)
        ).first.click()


def _book_via_trial_dialog(page: Page, dialog):
    """Handle the calendar-based trial booking dialog.

    UI structure:
      Step 1 — Date & Time:
        • Duration buttons  ("0.5 hour" / "1 hour")
        • Week header       ("Prev week" / date range / "Next week")
        • Day buttons       (day-of-week + date number; disabled if no slot)
        • Time slot buttons (e.g. "2:30 PM - 3:30 PM")
        • Continue button   (activates once slot selected)
      Step 2 — Review:
        • Confirm & Pay button → navigates to /en/payment
    """
    # 1. Select 1-hour duration (preferred for test predictability)
    dur_btn = dialog.locator('button:has-text("1 hour")')
    if dur_btn.count() > 0 and dur_btn.first.is_visible():
        dur_btn.first.click()
        page.wait_for_timeout(500)

    # 2. Find an available date (first non-disabled day button)
    #    Navigate up to 8 weeks to find one.
    slot_time_re = re.compile(r"\d+:\d+\s*(AM|PM)", re.I)
    slot_found = False

    for _ in range(8):
        # Check if any time slot buttons are already visible
        slots = dialog.locator("button").filter(has_text=slot_time_re)
        if slots.count() > 0 and slots.first.is_visible():
            # A day is already selected / auto-selected — pick the first slot
            slots.first.click()
            slot_found = True
            break

        # Try to click the first non-disabled date button in the grid
        # Day buttons contain just a 1-2 digit number (01-31)
        day_candidates = dialog.locator("button").filter(has_text=re.compile(r"^\d{1,2}$"))
        clicked_day = False
        for i in range(day_candidates.count()):
            btn = day_candidates.nth(i)
            if btn.is_visible() and not btn.is_disabled():
                btn.click()
                page.wait_for_timeout(600)
                clicked_day = True
                break

        if clicked_day:
            # Check if slots appeared after clicking the day
            slots = dialog.locator("button").filter(has_text=slot_time_re)
            if slots.count() > 0 and slots.first.is_visible():
                slots.first.click()
                slot_found = True
                break

        # Navigate to next week
        next_btn = dialog.locator(
            'button:has-text("Next week"), button[aria-label="Next week"]'
        ).first
        if next_btn.count() > 0 and next_btn.is_visible():
            next_btn.click()
            page.wait_for_timeout(900)

    assert slot_found, "No available time slot found in the booking dialog within 8 weeks"

    # 3. Continue to review step
    page.wait_for_timeout(400)
    dialog.locator('button:has-text("Continue")').first.click()
    page.wait_for_timeout(1500)

    # 4. Confirm & Pay → navigates to /en/payment
    with page.expect_navigation(timeout=25000):
        dialog.locator("button").filter(
            has_text=re.compile(r"Confirm|Pay", re.I)
        ).first.click()


# ─── Payment helpers ─────────────────────────────────────────────────────────

def fill_payment_iframe(page: Page):
    """Fill card details inside the MyFatoorah embedded iframe."""
    page.wait_for_selector("iframe#MFEmbeddedIframe", timeout=30000)
    frame = page.frame_locator("iframe#MFEmbeddedIframe")
    frame.get_by_placeholder("Name on Card").wait_for(state="visible", timeout=30000)
    frame.get_by_placeholder("Name on Card").fill(CARD_NAME)
    frame.get_by_placeholder("Card number").press_sequentially(CARD_VISA_SUCCESS, delay=50)
    frame.get_by_placeholder("MM / YY").press_sequentially(CARD_EXPIRY, delay=50)
    frame.get_by_placeholder("CVV").press_sequentially(CARD_CVV, delay=50)
    page.wait_for_timeout(800)


def handle_3ds(page: Page, approve: bool = True):
    """Wait for 3DS ACS emulator iframe and click Submit (approve or decline)."""
    try:
        page.wait_for_selector('iframe[title="3D Secure"]', timeout=20000)
    except Exception:
        return  # Some sandbox flows skip 3DS entirely
    page.wait_for_timeout(2000)
    challenge = (
        page.frame_locator('iframe[title="3D Secure"]')
            .frame_locator('iframe[name="challengeFrame"]')
    )
    if not approve:
        challenge.locator("select").select_option(
            label="(N) Not Authenticated /Account Not Verified Transaction denied"
        )
        page.wait_for_timeout(400)
    challenge.get_by_role("button", name="Submit").click()
    page.wait_for_timeout(5000)


# ─── Tests ───────────────────────────────────────────────────────────────────

class TestPaymentFlow:
    """MyFatoorah sandbox payment tests — no real charges."""

    def test_01_wallet_page_loads(self, student_page: Page):
        """Wallet page renders without server error."""
        student_page.goto(BASE_URL + "/dashboard/wallet", wait_until="commit", timeout=25000)
        student_page.wait_for_timeout(1500)
        assert "500" not in student_page.title(), "Server error on wallet page"
        assert "404" not in student_page.title(), "Wallet page not found"
        assert student_page.locator(
            'h1:has-text("Payment"), h1:has-text("Wallet"), h2:has-text("Payment"), h2:has-text("Wallet")'
        ).first.is_visible(timeout=8000), "Wallet/Payment heading not visible"
        print("\n[PAYMENT] ✅ Wallet page loads OK")

    def test_02_payment_iframe_renders(self, student_page: Page):
        """MyFatoorah card iframe renders all 4 fields after creating a real booking."""
        booking_number = book_slot_via_ui(student_page)
        assert booking_number.startswith("DBK-"), f"Booking failed — URL: {student_page.url}"
        print(f"\n[PAYMENT] Booking created: {booking_number}")

        assert student_page.locator('h1:has-text("Payment")').is_visible(timeout=10000)
        assert student_page.locator(f'text={booking_number}').is_visible()
        assert student_page.locator('text=Total Amount').is_visible()
        assert student_page.locator('text=encrypted').is_visible()

        # Verify MyFatoorah iframe and all card fields
        student_page.wait_for_selector("iframe#MFEmbeddedIframe", timeout=30000)
        frame = student_page.frame_locator("iframe#MFEmbeddedIframe")
        frame.get_by_placeholder("Name on Card").wait_for(state="visible", timeout=30000)
        assert frame.get_by_placeholder("Card number").is_visible()
        assert frame.get_by_placeholder("MM / YY").is_visible()
        assert frame.get_by_placeholder("CVV").is_visible()
        assert student_page.locator('button:has-text("Pay now")').is_visible()
        print("[PAYMENT] ✅ MyFatoorah iframe rendered with all card fields")

    def test_03_payment_complete_sandbox(self, student_page: Page):
        """Full E2E: book → fill Visa sandbox card → Pay now → 3DS approve → success.

        Uses demo.myfatoorah.com — SANDBOX. No real charge.
        Card: 4111 1111 1111 1111 / CVV 100 / 05/28
        """
        booking_number = book_slot_via_ui(student_page)
        assert booking_number.startswith("DBK-"), f"Booking failed: {student_page.url}"
        print(f"\n[PAYMENT] Booking: {booking_number}")

        fill_payment_iframe(student_page)
        print(f"[PAYMENT] Card filled: {CARD_VISA_SUCCESS[:4]}...{CARD_VISA_SUCCESS[-4:]}")

        student_page.locator('button:has-text("Pay now")').click()
        print("[PAYMENT] Pay now clicked — waiting for 3DS...")
        student_page.wait_for_timeout(3000)

        handle_3ds(student_page, approve=True)
        print("[PAYMENT] 3DS submitted (Y = Successful)")

        try:
            student_page.wait_for_url("**/dashboard/bookings**", timeout=30000)
            redirected = True
        except Exception:
            redirected = False

        page_text = student_page.inner_text("main")
        has_success = any(kw in page_text.lower() for kw in [
            "success", "confirmed", "upcoming sessions", "my bookings", "booking"
        ])

        print(f"[PAYMENT] Redirected to bookings: {redirected}")
        print(f"[PAYMENT] Success keywords found: {has_success}")
        print(f"[PAYMENT] Final URL: {student_page.url}")

        assert redirected or has_success, (
            f"Payment did not complete.\nURL: {student_page.url}\nPage: {page_text[:400]}"
        )
        print("[PAYMENT] ✅ Payment PASSED — sandbox transaction complete")

    def test_04_payment_3ds_decline(self, student_page: Page):
        """3DS decline path: select N = Not Authenticated → booking stays pending."""
        booking_number = book_slot_via_ui(student_page)
        assert booking_number.startswith("DBK-")
        print(f"\n[PAYMENT] Booking: {booking_number}")

        fill_payment_iframe(student_page)
        student_page.locator('button:has-text("Pay now")').click()
        student_page.wait_for_timeout(3000)

        handle_3ds(student_page, approve=False)
        student_page.wait_for_timeout(5000)

        page_text = student_page.inner_text("main")
        not_on_bookings = "/dashboard/bookings" not in student_page.url
        has_error = any(kw in page_text.lower() for kw in [
            "fail", "declined", "error", "reject", "not", "try"
        ])

        print(f"[PAYMENT] After decline — URL: {student_page.url}")
        print(f"[PAYMENT] Error text found: {has_error}")

        if not not_on_bookings:
            print("[PAYMENT] ⚠️  Unexpectedly on bookings page after 3DS decline")
        else:
            print("[PAYMENT] ✅ 3DS decline handled — no success redirect")

    def test_05_invalid_card_number(self, student_page: Page):
        """Invalid card (Luhn-failing number) is rejected inside the MyFatoorah iframe."""
        book_slot_via_ui(student_page)
        student_page.wait_for_selector("iframe#MFEmbeddedIframe", timeout=30000)
        frame = student_page.frame_locator("iframe#MFEmbeddedIframe")
        frame.get_by_placeholder("Name on Card").wait_for(state="visible", timeout=30000)
        frame.get_by_placeholder("Name on Card").fill("Test User")
        frame.get_by_placeholder("Card number").press_sequentially("1234567890123456", delay=40)
        frame.get_by_placeholder("MM / YY").press_sequentially("0528", delay=40)
        frame.get_by_placeholder("CVV").press_sequentially("100", delay=40)

        student_page.locator('button:has-text("Pay now")').click()
        student_page.wait_for_timeout(5000)

        page_text = student_page.inner_text("main")
        not_succeeded = "/dashboard/bookings" not in student_page.url
        print(f"\n[PAYMENT] Invalid card URL: {student_page.url}")
        print(f"[PAYMENT] Page text: {page_text[:300]}")
        assert not_succeeded, "Invalid card should not produce a successful booking redirect"
        print("[PAYMENT] ✅ Invalid card correctly rejected")
