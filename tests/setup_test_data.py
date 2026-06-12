"""
Pre-test data setup — ensures tutor has available slots and a booking exists.
Run BEFORE test_data_flow_e2e.py and test_realtime_data_flow.py.

Steps:
  1. Login as tutor → navigate availability calendar → create slots for next 7 days
  2. Login as student → book a slot on tutor 89 → navigate to payment page
  3. Print booking ID for downstream test consumption

Usage (CI):
  python3 tests/setup_test_data.py
  # Output: BOOKING_ID=DBK-20260611-XXXXXX
"""
from __future__ import annotations
import os, re, sys, time
from playwright.sync_api import sync_playwright, Page

BASE_URL      = os.getenv("BASE_URL",       "https://dev.mehadedu.com/en")
TUTOR_ID      = int(os.getenv("TUTOR_ID",   "89"))
TEACHER_PHONE = os.getenv("TEACHER_PHONE",  os.getenv("TEST_PHONE", "98976564"))
TEACHER_OTP   = os.getenv("TEACHER_OTP",    os.getenv("TEST_OTP",   "123456"))
STUDENT_PHONE = os.getenv("STUDENT_PHONE",  "98765432")
STUDENT_OTP   = os.getenv("STUDENT_OTP",    os.getenv("TEST_OTP",   "123456"))
COUNTRY_NAME  = "Bangladesh"
BID_RE        = re.compile(r"[D]?BK-\d{8}-[A-Z0-9]{4,8}", re.IGNORECASE)


def _base() -> str:
    return BASE_URL.rstrip("/").rsplit("/en", 1)[0]


def _url(path: str) -> str:
    return f"{_base()}/en{path}"


def _otp_login(pg: Page, phone: str, otp: str) -> None:
    """Proven OTP login — matches test_specs_all.py CI-confirmed pattern."""
    pg.goto(BASE_URL, wait_until="commit", timeout=25000)
    pg.wait_for_timeout(2000)
    login_btn = pg.locator(
        'button:not([aria-label="Login"]):has-text("Log In"), '
        'button:not([aria-label="Login"]):has-text("Login")'
    ).last
    login_btn.wait_for(state='visible', timeout=10000)
    login_btn.scroll_into_view_if_needed()
    login_btn.click(force=True)
    pg.wait_for_selector('[role="dialog"]', state='visible', timeout=10000)
    pg.wait_for_timeout(1000)
    container = pg.locator('[role="dialog"]')
    cc_btn = container.locator('button[aria-label="Country code"], button:has-text("Country code")').first
    cc_btn.wait_for(state='visible', timeout=8000)
    cc_btn.click()
    pg.wait_for_timeout(700)
    search_input = pg.locator('[role="listbox"] input[placeholder*="Search"], input[placeholder="Search..."]').first
    search_input.wait_for(state='visible', timeout=5000)
    search_input.fill(COUNTRY_NAME)
    pg.wait_for_timeout(600)
    pg.locator(f'[role="option"]:has-text("{COUNTRY_NAME}")').first.click()
    pg.wait_for_timeout(500)
    phone_input = container.locator('input[type="tel"], input[placeholder*="123"]').first
    phone_input.wait_for(state='visible', timeout=8000)
    phone_input.fill(phone)
    pg.wait_for_timeout(400)
    container.locator('button:has-text("Send Code")').first.click()
    pg.wait_for_timeout(2000)
    otp_input = container.locator('input[placeholder="000000"]').first
    otp_input.wait_for(state='visible', timeout=15000)
    for _ in range(30):
        pg.wait_for_timeout(1000)
        if not otp_input.is_disabled():
            break
    otp_input.fill(otp)
    pg.wait_for_timeout(800)
    container.locator('button:has-text("Continue")').first.click()
    pg.wait_for_timeout(4000)
    print(f"[SETUP] Login done — {pg.url}", flush=True)


def create_tutor_slots(pg: Page) -> bool:
    """Navigate to availability calendar and create slots for this week + next week."""
    print("[SETUP] Creating tutor availability slots...", flush=True)
    pg.goto(_url("/dashboard/availability"), wait_until="commit", timeout=25000)
    pg.wait_for_timeout(3000)

    if "/dashboard" not in pg.url and "/availability" not in pg.url:
        print(f"[SETUP] WARNING: Not on availability page — {pg.url}", flush=True)
        return False

    # Look for "Add Slot" / "+" / "Create" / "New Availability" button
    add_btn = pg.locator(
        'button:has-text("Add"), button:has-text("+ Add"), '
        'button[title*="Add"], button:has-text("New"), '
        'button:has-text("Create"), button[aria-label*="add"]'
    ).first
    if not add_btn.is_visible(timeout=5000):
        print("[SETUP] No add-slot button found — slots may exist or UI changed", flush=True)
        return True  # might already have slots

    # Try to add slots for multiple days
    slots_created = 0
    for attempt in range(3):
        try:
            add_btn.click()
            pg.wait_for_timeout(2000)
            # Fill any time dialog that appears
            time_inputs = pg.locator('input[type="time"], input[placeholder*="time"], [class*="time-input"]')
            if time_inputs.count() > 0:
                time_inputs.first.fill("10:00")
                pg.wait_for_timeout(500)
            # Confirm
            confirm = pg.locator('button:has-text("Save"), button:has-text("Confirm"), button:has-text("Add")').last
            if confirm.is_visible(timeout=3000):
                confirm.click()
                pg.wait_for_timeout(1500)
                slots_created += 1
        except Exception as e:
            print(f"[SETUP] Slot creation attempt {attempt+1} failed: {e}", flush=True)
            break

    print(f"[SETUP] Created {slots_created} slot(s)", flush=True)
    return True


def get_or_create_booking(pg: Page) -> str:
    """Try to book tutor 89. Return booking ID or existing booking ID."""
    print(f"[SETUP] Checking/creating booking on tutor {TUTOR_ID}...", flush=True)

    # First check if booking already exists in My Bookings
    pg.goto(_url("/dashboard/bookings"), wait_until="commit", timeout=25000)
    pg.wait_for_timeout(4000)
    existing = BID_RE.findall(pg.content())
    if existing:
        print(f"[SETUP] Existing booking found: {existing[0]}", flush=True)
        return existing[0]

    # Navigate to tutor profile and book
    tutor_url = _url(f"/tutor/{TUTOR_ID}")
    pg.goto(tutor_url, wait_until="commit", timeout=25000)
    pg.wait_for_timeout(3000)

    # Get tutor name
    try:
        tutor_name = pg.locator("h1, h2").first.inner_text(timeout=3000).strip().splitlines()[0]
        print(f"[SETUP] Tutor: {tutor_name}", flush=True)
    except Exception:
        pass

    # Click any Book button
    book_btn = pg.locator('button:has-text("Book"), button:has-text("Trial"), button:has-text("Lesson")').first
    if not book_btn.is_visible(timeout=8000):
        print(f"[SETUP] No Book button on tutor {TUTOR_ID} — all slots taken or no availability", flush=True)
        return ""

    book_btn.click()

    try:
        pg.wait_for_selector('[role="dialog"]', state="visible", timeout=15000)
    except Exception:
        if "/payment" in pg.url:
            m = BID_RE.search(pg.url)
            return m.group(0) if m else ""
        print("[SETUP] Booking dialog did not open", flush=True)
        return ""

    pg.wait_for_timeout(1500)
    dlg = pg.locator('[role="dialog"]')

    try:
        title = dlg.locator("h2, h3").first.inner_text(timeout=4000)
    except Exception:
        title = ""

    if "Package" in title or "Hour" in title.lower():
        # Package dialog
        pg.wait_for_timeout(800)
        card = pg.locator('[role="dialog"] .cursor-pointer:has(h3)').last
        if card.count() > 0:
            card.scroll_into_view_if_needed()
            card.click()
            pg.wait_for_timeout(800)
        cont = pg.locator('[role="dialog"] button:has-text("Continue")').first
        for _ in range(20):
            if cont.is_enabled():
                break
            pg.wait_for_timeout(300)
        cont.click()
        pg.wait_for_timeout(1500)
        try:
            with pg.expect_navigation(timeout=20000):
                pg.locator('[role="dialog"] button').filter(
                    has_text=re.compile(r"Confirm|Pay", re.I)
                ).first.click()
        except Exception:
            pass
    else:
        # Trial/calendar dialog — find a time slot
        slot_re = re.compile(r"\d+:\d+\s*(AM|PM)", re.I)
        dur = dlg.locator('button:has-text("1 hour")')
        if dur.count() > 0:
            dur.first.click()
            pg.wait_for_timeout(500)
        found = False
        for _ in range(8):
            slots = dlg.locator("button").filter(has_text=slot_re)
            if slots.count() > 0 and slots.first.is_visible():
                slots.first.click()
                found = True
                break
            days = dlg.locator("button").filter(has_text=re.compile(r"^\d{1,2}$"))
            clicked = False
            for i in range(days.count()):
                d = days.nth(i)
                try:
                    if not d.is_disabled() and d.is_visible():
                        d.click()
                        pg.wait_for_timeout(800)
                        clicked = True
                        break
                except Exception:
                    continue
            if not clicked:
                try:
                    pg.locator('[role="dialog"] button:has-text("Next week")').first.click()
                    pg.wait_for_timeout(600)
                except Exception:
                    break
        if not found:
            print("[SETUP] No available time slots", flush=True)
            return ""
        cont = dlg.locator('button:has-text("Continue")').first
        for _ in range(20):
            if cont.is_enabled():
                break
            pg.wait_for_timeout(300)
        cont.click()
        pg.wait_for_timeout(1500)
        try:
            with pg.expect_navigation(timeout=20000):
                dlg.locator("button").filter(
                    has_text=re.compile(r"Confirm|Pay", re.I)
                ).first.click()
        except Exception:
            pass

    pg.wait_for_timeout(2000)
    m = BID_RE.search(pg.url)
    bid = m.group(0) if m else ""
    if bid:
        print(f"[SETUP] Booking created: {bid}", flush=True)
    else:
        print(f"[SETUP] No booking ID in URL after booking — {pg.url}", flush=True)
    return bid


def main() -> str:
    booking_id = ""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # Step 1: Tutor login → create slots
        tutor_ctx = browser.new_context(
            viewport={"width": 1280, "height": 720},
            ignore_https_errors=True, locale="en-US"
        )
        tutor_pg = tutor_ctx.new_page()
        try:
            _otp_login(tutor_pg, TEACHER_PHONE, TEACHER_OTP)
            create_tutor_slots(tutor_pg)
        except Exception as e:
            print(f"[SETUP] Tutor setup error: {e}", flush=True)
        finally:
            tutor_ctx.close()

        # Step 2: Student login → create booking
        student_ctx = browser.new_context(
            viewport={"width": 1280, "height": 720},
            ignore_https_errors=True, locale="en-US"
        )
        student_pg = student_ctx.new_page()
        try:
            _otp_login(student_pg, STUDENT_PHONE, STUDENT_OTP)
            booking_id = get_or_create_booking(student_pg)
        except Exception as e:
            print(f"[SETUP] Student setup error: {e}", flush=True)
        finally:
            student_ctx.close()

        browser.close()

    if booking_id:
        print(f"BOOKING_ID={booking_id}", flush=True)
        # Write to file for test consumption
        with open("reports/setup_booking_id.txt", "w") as f:
            f.write(booking_id)
    else:
        print("[SETUP] No booking ID — tests will run with existing data", flush=True)

    return booking_id


if __name__ == "__main__":
    main()
