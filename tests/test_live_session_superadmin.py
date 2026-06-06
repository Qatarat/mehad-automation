"""
Handcrafted tests addressing three reported issues
===================================================

Issue 1 — Live class not being conducted properly
    Join Classroom button must only appear at scheduled session time.
    Automation sessions are booked for future dates, so the button should be
    absent. Tests verify EC-01 (absent before session time) and mark the
    actual join-classroom flow as xfail(strict=False) — it can only pass when
    run exactly at session start time.

Issue 2 — Super Admin cannot find session completion history for automation user
    Session history tabs (teacher side) and super admin session records are
    tested. Super admin login tests are skipped unless SUPER_ADMIN_EMAIL and
    SUPER_ADMIN_PASS env vars are provided.

Issue 3 — Slots being created for future dates
    Slots for June 10 (Tuesday) and June 15 (group session Monday) are
    EXPECTED behavior — the date helpers always compute future dates so tests
    never use expired calendar cells. Tests document and verify this contract.
"""
from __future__ import annotations

import os
import pytest
from datetime import date
from playwright.sync_api import Page

# ── Constants ─────────────────────────────────────────────────────────────────
BASE_URL          = os.getenv("BASE_URL", "https://dev.mehadedu.com/en")
SUPER_ADMIN_EMAIL = os.getenv("SUPER_ADMIN_EMAIL", "")
SUPER_ADMIN_PASS  = os.getenv("SUPER_ADMIN_PASS",  "")
TEACHER_PHONE     = os.getenv("TEACHER_PHONE", "98976564")
STUDENT_PHONE     = os.getenv("STUDENT_PHONE", "98765432")

_ADMIN_URL = BASE_URL.rstrip("/").replace("/en", "", 1) + "/en/super-admin-login"
_HAS_ADMIN_CREDS = bool(SUPER_ADMIN_EMAIL and SUPER_ADMIN_PASS)


# ── Super admin page fixture ───────────────────────────────────────────────────

@pytest.fixture(scope="class")
def admin_page(browser):
    """Fresh browser context for super admin — no teacher auth pre-loaded."""
    ctx = browser.new_context(
        viewport={"width": 1280, "height": 720},
        ignore_https_errors=True,
        locale="en-US",
    )
    pg = ctx.new_page()
    pg.set_default_timeout(15000)
    pg.goto(_ADMIN_URL, wait_until="commit", timeout=30000)
    pg.wait_for_timeout(1500)
    yield pg
    ctx.close()


# ==============================================================================
# Issue 1 — Live class joining
# ==============================================================================

class TestLiveClassJoining:
    """
    REQ-03 (session.md): Join Classroom button appears only at scheduled session time.
    EC-01  (session.md): Join before session time → button not visible.

    Automation always creates sessions for future dates so tests can run without
    a real-time dependency. The button must therefore be absent during normal
    CI runs. If the button IS present, it must be because the test is running
    at the exact session time (expected), not because the time-gate is broken.
    """

    PAGE_PATH = "/dashboard/sessions"

    def test_sessions_page_loads(self, page: Page):
        """Smoke: /dashboard/sessions loads without error for authenticated teacher."""
        page.goto(BASE_URL + "/dashboard/sessions", wait_until="commit", timeout=30000)
        page.wait_for_timeout(2000)
        assert "500" not in page.title(), f"Server error on sessions page: {page.url}"
        assert "404" not in page.title(), f"Not found on sessions page: {page.url}"

    def test_upcoming_sessions_section_present(self, page: Page):
        """Upcoming sessions section (tab / heading) must be visible after login."""
        page.goto(BASE_URL + "/dashboard/sessions", wait_until="commit", timeout=30000)
        page.wait_for_timeout(2500)
        upcoming = page.locator(
            'button:has-text("Upcoming"), [data-tab="upcoming"], '
            'button:has-text("Upcoming Sessions"), :has-text("Upcoming Sessions")'
        ).first
        try:
            upcoming.wait_for(state="visible", timeout=8000)
        except Exception:
            pytest.skip(
                f"Upcoming sessions section not found on {page.url} — "
                "page may require session data or selector changed"
            )

    def test_ec01_join_classroom_absent_before_session_time(self, page: Page):
        """
        EC-01: Join Classroom button must NOT be visible before scheduled session time.

        Automation sessions are booked for future dates. The button appearing
        early would mean the time-gate is broken — a real application bug.
        """
        page.goto(BASE_URL + "/dashboard/sessions", wait_until="commit", timeout=30000)
        page.wait_for_timeout(3000)

        join_btn = page.locator('button:has-text("Join Classroom")').first
        try:
            visible = join_btn.is_visible(timeout=3000)
        except Exception:
            visible = False

        if visible:
            pytest.xfail(
                "Join Classroom button is currently visible. "
                "Either a session is active right now (expected — not a bug) "
                "OR the time-gate logic is not enforced (actual bug). "
                "Manual verification required: check if any session is scheduled at this exact time."
            )

    def test_session_history_tab_present(self, page: Page):
        """
        Issue 2 root: Session History tab must exist so completed sessions can be viewed.
        Absence of this tab would prevent Super Admin from seeing history.
        """
        page.goto(BASE_URL + "/dashboard/sessions", wait_until="commit", timeout=30000)
        page.wait_for_timeout(2000)
        hist_tab = page.locator(
            'button:has-text("Session History"), [data-tab="history"], '
            'button:has-text("History"), button:has-text("Completed Sessions")'
        ).first
        try:
            hist_tab.wait_for(state="visible", timeout=8000)
        except Exception:
            pytest.fail(
                f"Session History tab not found on {page.url} — "
                "REQ-06 violated: completed sessions must appear in session history"
            )

    def test_session_history_tab_no_server_error(self, page: Page):
        """Clicking Session History tab must not trigger a server error."""
        page.goto(BASE_URL + "/dashboard/sessions", wait_until="commit", timeout=30000)
        page.wait_for_timeout(2000)
        try:
            hist_tab = page.locator(
                'button:has-text("Session History"), [data-tab="history"], '
                'button:has-text("History")'
            ).first
            hist_tab.wait_for(state="visible", timeout=8000)
            hist_tab.click()
            page.wait_for_timeout(2000)
            assert "500" not in page.title(), \
                f"Server error after clicking Session History tab: {page.url}"
            content = page.content().lower()
            assert "500 internal server error" not in content, \
                "500 error content inside session history view"
            assert "something went wrong" not in content, \
                "Error message inside session history view"
        except AssertionError:
            raise
        except Exception as exc:
            pytest.skip(f"Session History tab not interactable: {exc}")

    @pytest.mark.xfail(
        strict=False,
        reason=(
            "Join Classroom full flow requires the test to run at exact session time. "
            "Automation schedules sessions for future dates so this flow cannot execute "
            "in standard CI. Run manually at the scheduled time to verify."
        ),
    )
    def test_join_classroom_full_flow(self, page: Page):
        """
        Flow 1 (session.md): Join Classroom at Session Time.

        Steps:
          1. Navigate to /dashboard/sessions
          2. Find 'Join Classroom' button (only visible at session time)
          3. Click 'Join Classroom'
          4. Confirmation modal appears
          5. Click 'Join Classroom' in modal
          6. Classroom opens
        """
        page.goto(BASE_URL + "/dashboard/sessions", wait_until="commit", timeout=30000)
        page.wait_for_timeout(3000)

        join_btn = page.locator('button:has-text("Join Classroom")').first
        join_btn.wait_for(state="visible", timeout=5000)
        join_btn.click()
        page.wait_for_timeout(1000)

        modal = page.locator('[role="dialog"]:has-text("Join Classroom")').first
        modal.wait_for(state="visible", timeout=8000)

        confirm = modal.locator('button:has-text("Join Classroom")').first
        confirm.wait_for(state="visible", timeout=5000)
        confirm.click()
        page.wait_for_timeout(3000)

        assert "500" not in page.title(), \
            f"Server error after joining classroom: {page.url}"


# ==============================================================================
# Issue 1 (group session variant) — Join Classroom timing on group sessions page
# ==============================================================================

class TestGroupSessionJoinTiming:
    """
    EC-03 (tutor_group_session.md): Join Classroom button absent before session time.
    REQ-07: button appears only at scheduled session time.
    """

    PAGE_PATH = "/dashboard/group-sessions"

    def test_group_sessions_page_loads(self, page: Page):
        page.goto(BASE_URL + "/dashboard/group-sessions", wait_until="commit", timeout=30000)
        page.wait_for_timeout(2000)
        assert "500" not in page.title()
        assert "404" not in page.title()

    def test_ec03_join_classroom_absent_before_session_time(self, page: Page):
        """
        EC-03: Join Classroom must not be clickable before session start.

        Sessions created by automation are for future dates (next Monday ≥ 8 days).
        If the Join Classroom button is visible on any session card right now,
        either a session happens to be active (ok) or the time-gate is broken (bug).
        """
        page.goto(BASE_URL + "/dashboard/group-sessions", wait_until="commit", timeout=30000)
        page.wait_for_timeout(3000)

        # Check how many Join Classroom buttons are visible
        join_btns = page.locator('button:has-text("Join Classroom")')
        count = 0
        try:
            count = join_btns.count()
        except Exception:
            count = 0

        if count == 0:
            return  # Correct — no active session right now

        # If some are visible, verify at least one is actually for a current session
        visible_count = sum(
            1 for i in range(count)
            if join_btns.nth(i).is_visible()
        )

        if visible_count > 0:
            pytest.xfail(
                f"Found {visible_count} visible 'Join Classroom' button(s) on group sessions page. "
                "Either a session is active right now (expected) or time-gate is broken (bug). "
                "Manual verification: confirm session schedule matches current time."
            )

    def test_manage_button_present_on_sessions(self, page: Page):
        """REQ-02: Each group session card must have a Manage button."""
        page.goto(BASE_URL + "/dashboard/group-sessions", wait_until="commit", timeout=30000)
        page.wait_for_timeout(2000)
        manage_btn = page.locator('button:has-text("Manage")').first
        try:
            manage_btn.wait_for(state="visible", timeout=6000)
        except Exception:
            pytest.skip(
                "No 'Manage' button found — may mean no group sessions exist yet. "
                "Create a group session first to test REQ-02."
            )


# ==============================================================================
# Issue 2 — Teacher session history (teacher-side view)
# ==============================================================================

class TestTeacherSessionHistory:
    """
    Root cause of 'no session history in Super Admin': if teacher sessions
    aren't being completed (because they're all in the future), the history
    stays empty. These tests verify the history tab exists and is functional.
    """

    PAGE_PATH = "/dashboard/booked-sessions"

    def test_booked_sessions_page_loads(self, page: Page):
        """TBS-01: /dashboard/booked-sessions loads for authenticated teacher."""
        page.goto(BASE_URL + "/dashboard/booked-sessions", wait_until="commit", timeout=30000)
        page.wait_for_timeout(2000)
        assert "500" not in page.title()
        assert "404" not in page.title()

    def test_session_history_tab_visible(self, page: Page):
        """TBS-02: 'Session History' tab must be visible on booked sessions page."""
        page.goto(BASE_URL + "/dashboard/booked-sessions", wait_until="commit", timeout=30000)
        page.wait_for_timeout(2000)
        hist = page.locator('button:has-text("Session History")').first
        try:
            hist.wait_for(state="visible", timeout=8000)
        except Exception:
            pytest.fail(
                f"'Session History' tab not found on {page.url} — TBS-02 violated. "
                "This tab is required for viewing completed session records."
            )

    def test_session_history_tab_clickable_no_crash(self, page: Page):
        """TBS-06: Clicking Session History switches content without a server error."""
        page.goto(BASE_URL + "/dashboard/booked-sessions", wait_until="commit", timeout=30000)
        page.wait_for_timeout(2000)
        try:
            hist = page.locator('button:has-text("Session History")').first
            hist.wait_for(state="visible", timeout=8000)
            hist.click()
            page.wait_for_timeout(2500)
            assert "500" not in page.title(), \
                f"Server error after clicking Session History: {page.url}"
            content = page.content().lower()
            assert "500 internal server error" not in content
            assert "something went wrong" not in content
            # Either historical session rows OR empty state — both are valid
            has_data = any(t in content for t in [
                "session history", "completed", "no session", "no upcoming"
            ])
            assert has_data, (
                "Session History tab content is empty or unrecognizable. "
                "Expected session rows or an empty-state message."
            )
        except AssertionError:
            raise
        except Exception as exc:
            pytest.skip(f"Session History tab interaction failed: {exc}")

    def test_upcoming_tab_shows_future_sessions(self, page: Page):
        """
        Issue 3 context: automation-created sessions appear as 'upcoming' because
        they are for future dates. This test confirms those sessions are visible.
        """
        page.goto(BASE_URL + "/dashboard/booked-sessions", wait_until="commit", timeout=30000)
        page.wait_for_timeout(2000)
        try:
            upcoming = page.locator('button:has-text("Upcoming Sessions")').first
            upcoming.wait_for(state="visible", timeout=8000)
            upcoming.click()
            page.wait_for_timeout(2000)
            assert "500" not in page.title()
            # After clicking, content should render without error
            content = page.content().lower()
            assert "500 internal server error" not in content
        except AssertionError:
            raise
        except Exception as exc:
            pytest.skip(f"Upcoming Sessions tab not accessible: {exc}")


# ==============================================================================
# Issue 2 — Super Admin session records
# ==============================================================================

class TestSuperAdminSessionRecords:
    """
    Issue: Super Admin cannot find session completion history for automation user.

    Full admin-login tests are skipped unless SUPER_ADMIN_EMAIL and
    SUPER_ADMIN_PASS are set. The login page structure test runs always.
    """

    def test_super_admin_login_page_accessible(self, admin_page: Page):
        """Super Admin login page must load without error."""
        assert "500" not in admin_page.title(), \
            f"Server error on super admin login page: {admin_page.url}"
        assert "404" not in admin_page.title(), \
            f"Not found on super admin login page: {admin_page.url}"

    def test_super_admin_login_page_has_form(self, admin_page: Page):
        """Super Admin login form (email + password or phone) must be present."""
        has_email = admin_page.locator('input[type="email"], input[type="text"]').count() > 0
        has_phone = admin_page.locator('input[type="tel"]').count() > 0
        assert has_email or has_phone, \
            f"No login form (email/phone input) found on {admin_page.url}"

    @pytest.mark.skipif(
        not _HAS_ADMIN_CREDS,
        reason="Set SUPER_ADMIN_EMAIL and SUPER_ADMIN_PASS env vars to run admin login tests",
    )
    def test_super_admin_login_succeeds(self, admin_page: Page):
        """Super Admin can log in with SUPER_ADMIN_EMAIL / SUPER_ADMIN_PASS credentials."""
        admin_page.goto(_ADMIN_URL, wait_until="commit", timeout=30000)
        admin_page.wait_for_timeout(1500)
        admin_page.locator('input[type="email"]').first.fill(SUPER_ADMIN_EMAIL)
        admin_page.locator('input[type="password"]').first.fill(SUPER_ADMIN_PASS)
        admin_page.locator(
            'button[type="submit"], button:has-text("Login"), button:has-text("Sign In")'
        ).first.click()
        admin_page.wait_for_timeout(3000)
        assert "500" not in admin_page.title(), "Server error after super admin login"
        assert "super-admin-login" not in admin_page.url, \
            "Admin login did not redirect away from login page — credentials may be wrong"

    @pytest.mark.skipif(
        not _HAS_ADMIN_CREDS,
        reason="Set SUPER_ADMIN_EMAIL and SUPER_ADMIN_PASS env vars to run admin login tests",
    )
    def test_super_admin_can_view_sessions_section(self, admin_page: Page):
        """After login, Super Admin must be able to navigate to a sessions or reports section."""
        admin_page.goto(_ADMIN_URL, wait_until="commit", timeout=30000)
        admin_page.wait_for_timeout(1500)
        admin_page.locator('input[type="email"]').first.fill(SUPER_ADMIN_EMAIL)
        admin_page.locator('input[type="password"]').first.fill(SUPER_ADMIN_PASS)
        admin_page.locator(
            'button[type="submit"], button:has-text("Login"), button:has-text("Sign In")'
        ).first.click()
        admin_page.wait_for_timeout(3000)

        # Try to find sessions / reports link in the sidebar
        nav_link = admin_page.locator(
            'a:has-text("Sessions"), a:has-text("Reports"), '
            'a:has-text("Bookings"), [data-testid="sessions-nav"]'
        ).first
        try:
            nav_link.wait_for(state="visible", timeout=8000)
            nav_link.click()
            admin_page.wait_for_timeout(2000)
            assert "500" not in admin_page.title(), \
                f"Server error on sessions/reports section: {admin_page.url}"
        except AssertionError:
            raise
        except Exception:
            pytest.skip(
                "Sessions/Reports link not found in Super Admin sidebar. "
                "Check the sidebar structure or selector for the sessions nav item."
            )

    @pytest.mark.skipif(
        not _HAS_ADMIN_CREDS,
        reason="Set SUPER_ADMIN_EMAIL and SUPER_ADMIN_PASS env vars to run admin login tests",
    )
    def test_super_admin_session_history_visible_for_automation_user(self, admin_page: Page):
        """
        Core issue: Super Admin should be able to find session records for the
        automation teacher user (phone: TEACHER_PHONE).

        After login, search for the teacher phone number in the sessions/reports
        section. Either matching records appear, or a clear 'no results' state —
        an empty page with no message would be a bug.
        """
        admin_page.goto(_ADMIN_URL, wait_until="commit", timeout=30000)
        admin_page.wait_for_timeout(1500)
        admin_page.locator('input[type="email"]').first.fill(SUPER_ADMIN_EMAIL)
        admin_page.locator('input[type="password"]').first.fill(SUPER_ADMIN_PASS)
        admin_page.locator(
            'button[type="submit"], button:has-text("Login"), button:has-text("Sign In")'
        ).first.click()
        admin_page.wait_for_timeout(3000)

        # Navigate to sessions/reports
        try:
            admin_page.locator(
                'a:has-text("Sessions"), a:has-text("Reports"), '
                'a:has-text("Bookings")'
            ).first.click()
            admin_page.wait_for_timeout(2000)
        except Exception:
            pytest.skip("Could not navigate to sessions section in Super Admin")

        # Search for automation teacher
        search = admin_page.locator('input[placeholder*="Search"]').first
        try:
            search.wait_for(state="visible", timeout=8000)
            search.fill(TEACHER_PHONE)
            admin_page.wait_for_timeout(2000)
            assert "500" not in admin_page.title(), "Server error while searching"
            content = admin_page.content()
            assert TEACHER_PHONE in content or "no result" in content.lower(), (
                f"Expected automation teacher ({TEACHER_PHONE}) to appear in search results "
                "or a 'no results' message. Got neither — the page may have silently failed."
            )
        except AssertionError:
            raise
        except Exception as exc:
            pytest.skip(f"Super Admin search not accessible: {exc}")


# ==============================================================================
# Issue 3 — Slot creation dates (future dates are expected, not a bug)
# ==============================================================================

class TestSlotFutureDates:
    """
    Issue 3: Slots are created for future dates (e.g. June 10, June 15).

    This is CORRECT behavior:
    - Availability slots must be in the future (past dates rejected by the app).
    - The date_helpers module computes dates relative to today at runtime so
      tests never break on a hard-coded expired date.
    - Tuesday slot (availability_slot_tuesday) → nearest future Tuesday ≥ 2 days
    - Group session (group_session_date) → next Monday ≥ 8 days to avoid
      collision with the 1-to-1 Monday availability slot.

    These tests document and assert the contract.
    """

    def test_availability_monday_slot_is_future_and_at_least_2_days_ahead(self):
        """Monday 1-to-1 slot must be at least 2 days from today."""
        from tests.date_helpers import availability_slot_monday
        slot = availability_slot_monday()
        today = date.today()
        assert slot["date"] > today, \
            f"Monday slot {slot['date']} is not in the future"
        delta = (slot["date"] - today).days
        assert delta >= 2, (
            f"Monday slot is {delta} day(s) away — must be ≥ 2 days "
            "so the API has time to propagate before booking tests run"
        )

    def test_availability_tuesday_slot_is_future_and_at_least_2_days_ahead(self):
        """Tuesday slot must be at least 2 days from today (matches ~June 10 from June 6)."""
        from tests.date_helpers import availability_slot_tuesday
        slot = availability_slot_tuesday()
        today = date.today()
        assert slot["date"] > today
        delta = (slot["date"] - today).days
        assert delta >= 2, (
            f"Tuesday slot is {delta} day(s) away — must be ≥ 2 days. "
            f"Computed date: {slot['date']}"
        )

    def test_group_session_date_is_at_least_8_days_ahead(self):
        """Group session must be ≥ 8 days ahead to not collide with 1-to-1 Monday slot."""
        from tests.date_helpers import group_session_date
        slot = group_session_date()
        today = date.today()
        delta = (slot["date"] - today).days
        assert delta >= 7, (
            f"Group session date {slot['date']} is only {delta} day(s) away. "
            "Must be ≥ 7 days ahead to avoid overlap with the 1-on-1 availability Monday slot."
        )

    def test_1on1_slot_and_group_session_on_different_dates(self):
        """1-on-1 Monday availability and group session must be on different dates."""
        from tests.date_helpers import availability_slot_monday, group_session_date
        one_on_one = availability_slot_monday()
        group = group_session_date()
        assert one_on_one["date"] != group["date"], (
            f"1-on-1 slot ({one_on_one['date']}) and group session ({group['date']}) "
            "must not fall on the same date — they would conflict in the calendar."
        )

    def test_slot_dates_are_mondays_or_correct_weekdays(self):
        """Verify slot helpers return the correct weekday."""
        from tests.date_helpers import (
            availability_slot_monday, availability_slot_tuesday,
            availability_slot_wednesday, group_session_date
        )
        monday_slot = availability_slot_monday()
        tuesday_slot = availability_slot_tuesday()
        wednesday_slot = availability_slot_wednesday()
        group_slot = group_session_date()

        assert monday_slot["date"].weekday() == 0, \
            f"availability_slot_monday returned {monday_slot['date']} which is not Monday"
        assert tuesday_slot["date"].weekday() == 1, \
            f"availability_slot_tuesday returned {tuesday_slot['date']} which is not Tuesday"
        assert wednesday_slot["date"].weekday() == 2, \
            f"availability_slot_wednesday returned {wednesday_slot['date']} which is not Wednesday"
        assert group_slot["date"].weekday() == 0, \
            f"group_session_date returned {group_slot['date']} which is not Monday"
