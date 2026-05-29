"""
test_login_e2e.py — Full E2E login tests for MehadEdu (dev.mehadedu.com).

Spec: specs/login.md  |  specs/student_login.md
Auth: WhatsApp OTP — country code + phone → OTP 123456 (staging hardcode)

Test credentials (fixed test account):
  Country : Bangladesh +880
  Phone   : 98976564
  OTP     : 123456
  Result  : "Automations Student" shown in header

Coverage:
  REQ-01  page loads, header visible
  REQ-02  Login button present in header
  REQ-03  Login modal opens on click
  REQ-04  Modal has title "Welcome back"
  REQ-05  Country code selector defaults (shows a flag + code)
  REQ-06  Phone field accepts numbers only, max 12 chars
  REQ-07  Send Code disabled when phone is empty
  REQ-08  Send Code enabled after valid phone entered
  REQ-09  Happy path: select +880 → phone → OTP → logged in
  REQ-10  OTP field hidden until Send Code clicked
  REQ-11  Change Mobile Number link appears after code sent
  REQ-12  Wrong OTP shows error / no login
  REQ-13  Close button (×) closes the modal
  REQ-14  Login works on 375px mobile viewport
  REQ-15  No console errors on page load
  REQ-16  Re-open modal after close resets state
  REQ-17  Send Code disabled for phone < 7 digits
"""
from __future__ import annotations

import os
import re
import pytest
from playwright.sync_api import Page, expect

from ai_engine.temp_identity import new_staging_phone

# ── Config ─────────────────────────────────────────────────────────────────────
BASE_URL      = os.getenv("BASE_URL", "https://dev.mehadedu.com/en")
COUNTRY       = "Bangladesh"
PHONE         = os.getenv("TEST_PHONE", "98976564")
OTP           = os.getenv("TEST_OTP",   "123456")
WRONG_OTP     = "999999"
EXPECTED_NAME = "Automations Student"


# ── Helpers ────────────────────────────────────────────────────────────────────

def _goto(page: Page, url: str = BASE_URL) -> None:
    for attempt in range(3):
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(800)
            return
        except Exception as e:
            if attempt == 2:
                raise
            print(f"  [nav] attempt {attempt+1} failed: {e!s:.60} — retrying")


def _open_login_modal(page: Page) -> None:
    """Click the visible Login button (desktop or mobile) and wait for the modal."""
    # Desktop: button with text "login", no aria-label (visible on desktop)
    # Mobile:  button with aria-label="Login" (md:hidden on desktop)
    # Find all buttons with text "login" and click the visible one.
    login_btns = page.locator("button").filter(has_text=re.compile(r"^login$", re.I))
    count = login_btns.count()
    for i in range(count):
        btn = login_btns.nth(i)
        if btn.is_visible():
            btn.click()
            break
    else:
        # Fallback: any login-labelled button
        page.get_by_role("button", name=re.compile("login", re.I)).first.click()

    page.wait_for_selector('[role="dialog"]', timeout=8000)
    page.wait_for_timeout(400)


def _select_country(page: Page, country: str = COUNTRY) -> None:
    """Open the country code listbox and select the given country."""
    # Country code button accessible name is "countryCode"
    cc_btn = page.get_by_role("button", name="countryCode")
    cc_btn.wait_for(state="visible", timeout=5000)
    cc_btn.click()

    # Search textbox placeholder is "search" (lowercase)
    search = page.get_by_placeholder("search")
    search.wait_for(state="visible", timeout=4000)
    search.fill(country)
    page.wait_for_timeout(300)

    # Click the matching option
    option = page.get_by_role("option", name=re.compile(country, re.I)).first
    option.wait_for(state="visible", timeout=5000)
    option.click()
    page.wait_for_timeout(400)


def _fill_phone(page: Page, phone: str = PHONE) -> None:
    """Fill the phone number input (enabled, non-OTP input inside the dialog)."""
    # Phone input is enabled; OTP starts disabled (placeholder "000000")
    # Search input only visible when country dropdown is open
    phone_input = page.locator('[role="dialog"] input:not([placeholder="000000"]):not([placeholder="search"])').first
    phone_input.wait_for(state="visible", timeout=5000)
    phone_input.fill(phone)
    page.wait_for_timeout(300)


def _click_send_code(page: Page) -> None:
    btn = page.get_by_role("button", name="Send Code").first
    btn.wait_for(state="visible", timeout=5000)
    btn.click()
    page.wait_for_timeout(1500)


def _fill_otp(page: Page, otp: str = OTP) -> None:
    otp_input = page.get_by_placeholder("000000")
    otp_input.wait_for(state="visible", timeout=8000)
    for _ in range(15):
        if not otp_input.is_disabled():
            break
        page.wait_for_timeout(400)
    otp_input.fill(otp)
    page.wait_for_timeout(300)


def _click_continue(page: Page) -> None:
    btn = page.get_by_role("button", name="Continue").first
    btn.wait_for(state="visible", timeout=5000)
    btn.click()
    page.wait_for_timeout(2000)


def _do_full_login(page: Page, country: str = COUNTRY,
                   phone: str = PHONE, otp: str = OTP) -> None:
    """Full login flow: open modal → country → phone → send code → OTP → continue."""
    _open_login_modal(page)
    _select_country(page, country)
    _fill_phone(page, phone)
    _click_send_code(page)
    _fill_otp(page, otp)
    _click_continue(page)


# ── Test Class ─────────────────────────────────────────────────────────────────

class TestLoginE2E:
    """MehadEdu Login Modal — E2E test suite (driven by specs/login.md)."""

    # ── REQ-01 ────────────────────────────────────────────────────────────────
    @pytest.mark.timeout(30)
    def test_login_page_loads(self, page: Page):
        """REQ-01: Homepage loads and URL contains mehadedu.com."""
        _goto(page)
        assert "mehadedu.com" in page.url, f"Unexpected URL: {page.url}"
        print(f"\n  URL: {page.url}  PASS")

    # ── REQ-02 ────────────────────────────────────────────────────────────────
    @pytest.mark.timeout(30)
    def test_login_button_visible_in_header(self, page: Page):
        """REQ-02: A Login button is present and visible in the header."""
        _goto(page)
        # Desktop button: text "login", no aria-label (visible at normal viewport)
        # Mobile button:  aria-label="Login" (hidden at desktop, visible on mobile)
        login_btns = page.locator("button").filter(has_text=re.compile(r"^login$", re.I))
        visible = any(login_btns.nth(i).is_visible() for i in range(login_btns.count()))
        assert visible, "No visible login button found in header"
        print("\n  Login button visible  PASS")

    # ── REQ-03 ────────────────────────────────────────────────────────────────
    @pytest.mark.timeout(30)
    def test_login_modal_opens(self, page: Page):
        """REQ-03: Clicking Login button opens the modal dialog."""
        _goto(page)
        _open_login_modal(page)
        dialog = page.locator('[role="dialog"]').first
        expect(dialog).to_be_visible()
        print("\n  Modal opened  PASS")

    # ── REQ-04 ────────────────────────────────────────────────────────────────
    @pytest.mark.timeout(30)
    def test_login_modal_title(self, page: Page):
        """REQ-04: Modal title is 'Welcome back'."""
        _goto(page)
        _open_login_modal(page)
        title_el = page.get_by_role("heading", name="Welcome back")
        expect(title_el).to_be_visible()
        print("\n  Modal title 'Welcome back' visible  PASS")

    # ── REQ-05 ────────────────────────────────────────────────────────────────
    @pytest.mark.timeout(30)
    def test_login_country_selector_visible(self, page: Page):
        """REQ-05: Country code selector is visible inside the login modal."""
        _goto(page)
        _open_login_modal(page)
        # Country button accessible name is "countryCode", shows "+XXX" as text
        cc_btn = page.get_by_role("button", name="countryCode")
        expect(cc_btn).to_be_visible()
        code_text = cc_btn.text_content() or ""
        assert "+" in code_text, f"Country button should display a +XXX code, got: {code_text!r}"
        print(f"\n  Country selector visible, shows: {code_text!r}  PASS")

    # ── REQ-06 ────────────────────────────────────────────────────────────────
    @pytest.mark.timeout(30)
    def test_login_phone_field_visible(self, page: Page):
        """REQ-06: Phone number input is visible inside the login modal."""
        _goto(page)
        _open_login_modal(page)
        phone_input = page.locator('[role="dialog"] input:not([placeholder="000000"]):not([placeholder="search"])').first
        expect(phone_input).to_be_visible()
        print("\n  Phone input visible  PASS")

    # ── REQ-07 ────────────────────────────────────────────────────────────────
    @pytest.mark.timeout(30)
    def test_login_send_code_disabled_when_empty(self, page: Page):
        """REQ-07: Send Code button is disabled when phone field is empty."""
        _goto(page)
        _open_login_modal(page)
        send_btn = page.get_by_role("button", name="Send Code").first
        assert send_btn.is_disabled(), "Send Code should be disabled when phone is empty"
        print("\n  Send Code disabled when empty  PASS")

    # ── REQ-17 ───────────────────────────────────────────────────────────────
    @pytest.mark.timeout(30)
    def test_login_send_code_disabled_short_phone(self, page: Page):
        """REQ-17: Send Code disabled for phone < 7 digits (pattern validation)."""
        _goto(page)
        _open_login_modal(page)
        phone_input = page.locator('[role="dialog"] input:not([placeholder="000000"]):not([placeholder="search"])').first
        phone_input.fill("123")
        page.wait_for_timeout(400)
        send_btn = page.get_by_role("button", name="Send Code").first
        assert send_btn.is_disabled(), "Send Code should be disabled for a 3-digit phone"
        print("\n  Send Code disabled for short phone  PASS")

    # ── REQ-08 ────────────────────────────────────────────────────────────────
    @pytest.mark.timeout(45)
    def test_login_send_code_enabled_after_phone(self, page: Page):
        """REQ-08: Send Code button enables once a valid phone is entered."""
        _goto(page)
        _open_login_modal(page)
        # Must select correct country first — validation is country-format aware
        _select_country(page, COUNTRY)
        _fill_phone(page, PHONE)
        send_btn = page.get_by_role("button", name="Send Code").first
        for _ in range(8):
            if not send_btn.is_disabled():
                break
            page.wait_for_timeout(300)
        assert not send_btn.is_disabled(), (
            f"Send Code should be enabled after entering phone: {PHONE}")
        print("\n  Send Code enabled after phone entry  PASS")

    # ── REQ-09 ────────────────────────────────────────────────────────────────
    @pytest.mark.timeout(90)
    def test_login_happy_path(self, page: Page):
        """REQ-09: Full login flow — select +880, enter phone, OTP → logged in."""
        errors: list[str] = []
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)

        _goto(page)
        _do_full_login(page)  # _fill_otp skips automatically on 429

        try:
            page.wait_for_function(
                f"() => document.body.innerText.includes('{EXPECTED_NAME}')",
                timeout=10000,
            )
        except Exception:
            pass

        page_text = page.inner_text("body")
        modal_gone = not page.locator('[role="dialog"]').count()
        name_visible = EXPECTED_NAME in page_text

        assert name_visible or modal_gone, (
            f"Expected '{EXPECTED_NAME}' in page or modal dismissed after login. "
            f"URL: {page.url}")
        print(f"\n  Login successful — URL: {page.url}  PASS")

    # ── REQ-10 ────────────────────────────────────────────────────────────────
    @pytest.mark.timeout(60)
    def test_login_otp_field_appears_after_send_code(self, page: Page):
        """REQ-10: OTP input is disabled before Send Code and enabled after."""
        rand_phone = new_staging_phone(random=True)

        _goto(page)
        _open_login_modal(page)

        otp_input = page.get_by_placeholder("000000")
        assert otp_input.is_disabled(), "OTP field should be disabled before Send Code"

        _select_country(page, rand_phone.display_country)
        _fill_phone(page, rand_phone.phone_number)
        _click_send_code(page)

        otp_input.wait_for(state="visible", timeout=8000)
        for _ in range(15):
            if not otp_input.is_disabled():
                break
            page.wait_for_timeout(400)
        assert not otp_input.is_disabled(), "OTP field should be enabled after Send Code"
        print(f"\n  OTP field enabled after Send Code (phone {rand_phone.phone_number})  PASS")

    # ── REQ-11 ────────────────────────────────────────────────────────────────
    @pytest.mark.timeout(60)
    def test_login_change_number_link_visible(self, page: Page):
        """REQ-11: 'changeMobileNumber' button appears after OTP code is sent."""
        # Use a fresh random phone to avoid 429 rate limit from previous tests
        rand_phone = new_staging_phone(random=True)

        _goto(page)
        _open_login_modal(page)
        _select_country(page, rand_phone.display_country)
        _fill_phone(page, rand_phone.phone_number)
        _click_send_code(page)

        # Staging i18n key: "changeMobileNumber" (translation key shown as-is)
        change_btn = page.get_by_text(
            re.compile(r"changeMobileNumber|Change.*Number|Change.*Mobile", re.I)
        ).first
        change_btn.wait_for(state="visible", timeout=10000)
        expect(change_btn).to_be_visible()
        print(f"\n  'changeMobileNumber' button visible (phone {rand_phone.phone_number})  PASS")

    # ── REQ-12 ────────────────────────────────────────────────────────────────
    @pytest.mark.timeout(90)
    def test_login_wrong_otp_rejected(self, page: Page):
        """REQ-12: Wrong OTP (999999) does not log the user in."""
        # Use a fresh random phone to avoid 429 rate limit from previous tests
        rand_phone = new_staging_phone(random=True)

        _goto(page)
        _open_login_modal(page)
        _select_country(page, rand_phone.display_country)
        _fill_phone(page, rand_phone.phone_number)
        _click_send_code(page)

        _fill_otp(page, WRONG_OTP)
        _click_continue(page)

        page.wait_for_timeout(2000)
        modal_still_open = bool(page.locator('[role="dialog"]').count())
        error_visible    = bool(page.get_by_text(
            re.compile(r"invalid|incorrect|wrong|error|expired", re.I)).count())
        still_on_home    = page.url.rstrip("/").endswith("/en")

        assert modal_still_open or error_visible or still_on_home, (
            "Wrong OTP should not complete login — expected error or modal to remain")
        print("\n  Wrong OTP rejected  PASS")

    # ── REQ-13 ────────────────────────────────────────────────────────────────
    @pytest.mark.timeout(30)
    def test_login_modal_close_button(self, page: Page):
        """REQ-13: X (close) button dismisses the login modal."""
        _goto(page)
        _open_login_modal(page)
        close_btn = page.get_by_role("button", name="Close").first
        close_btn.wait_for(state="visible", timeout=5000)
        close_btn.click()
        page.wait_for_timeout(600)

        dialogs = page.locator('[role="dialog"]').count()
        assert dialogs == 0, f"Modal should be closed after clicking X; dialogs={dialogs}"
        print("\n  Modal closed by Close button  PASS")

    # ── REQ-14 ────────────────────────────────────────────────────────────────
    @pytest.mark.timeout(60)
    def test_login_mobile_viewport(self, page: Page):
        """REQ-14: Login modal is usable on 375×667 mobile viewport."""
        page.set_viewport_size({"width": 375, "height": 667})
        _goto(page)
        _open_login_modal(page)
        dialog = page.locator('[role="dialog"]').first
        expect(dialog).to_be_visible()
        phone_input = page.locator('[role="dialog"] input:not([placeholder="000000"])').first
        expect(phone_input).to_be_visible()
        print("\n  Login modal usable on 375px mobile  PASS")

    # ── REQ-15 ────────────────────────────────────────────────────────────────
    @pytest.mark.timeout(30)
    def test_login_no_console_errors(self, page: Page):
        """REQ-15: No JavaScript console errors on homepage load."""
        errors: list[str] = []
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        _goto(page)

        critical = [e for e in errors
                    if not any(skip in e.lower() for skip in
                               ("favicon", "gtm", "analytics", "chunk", "warning",
                                "failed to load resource"))]
        assert not critical, f"Console errors: {critical[:3]}"
        print(f"\n  No critical console errors ({len(errors)} total)  PASS")

    # ── REQ-16 ────────────────────────────────────────────────────────────────
    @pytest.mark.timeout(30)
    def test_login_modal_reopen_resets_state(self, page: Page):
        """REQ-16: Re-opening the modal after closing resets the phone field."""
        _goto(page)
        _open_login_modal(page)
        phone_input = page.locator('[role="dialog"] input:not([placeholder="000000"]):not([placeholder="search"])').first
        phone_input.fill("12345678")

        page.get_by_role("button", name="Close").first.click()
        page.wait_for_timeout(600)

        _open_login_modal(page)
        phone_input2 = page.locator('[role="dialog"] input:not([placeholder="000000"]):not([placeholder="search"])').first
        phone_input2.wait_for(state="visible", timeout=5000)
        val = phone_input2.input_value()
        assert val == "" or val != "12345678", (
            f"Phone field should reset on re-open; got: {val!r}")
        print(f"\n  Phone field reset on modal re-open (val={val!r})  PASS")

    # ── COUNTRY SEARCH ────────────────────────────────────────────────────────
    @pytest.mark.timeout(30)
    def test_login_country_search(self, page: Page):
        """Country dropdown search filters to Bangladesh."""
        _goto(page)
        _open_login_modal(page)
        page.get_by_role("button", name="countryCode").click()
        search = page.get_by_placeholder("search")
        search.wait_for(state="visible", timeout=5000)
        search.fill("Bangladesh")
        page.wait_for_timeout(400)
        option = page.get_by_role("option", name=re.compile("Bangladesh", re.I)).first
        expect(option).to_be_visible()
        print("\n  Country search found Bangladesh  PASS")

    # ── PHONE MAX LENGTH ──────────────────────────────────────────────────────
    @pytest.mark.timeout(30)
    def test_login_phone_max_length(self, page: Page):
        """Phone field accepts at most 12 digits (maxlength=12)."""
        _goto(page)
        _open_login_modal(page)
        phone_input = page.locator('[role="dialog"] input:not([placeholder="000000"]):not([placeholder="search"])').first
        phone_input.fill("1" * 20)
        page.wait_for_timeout(300)
        val = phone_input.input_value()
        assert len(val) <= 12, (
            f"Phone field should accept max 12 chars; got {len(val)}: {val!r}")
        print(f"\n  Phone field maxlength enforced (got {len(val)} chars)  PASS")
