"""
Pre-test data setup — creates real tutor slots, a group session, and a student booking.
Run BEFORE test_data_flow_e2e.py and test_realtime_data_flow.py.

Steps:
  1. Tutor login → create 1-on-1 availability slots (Mon/Tue/Wed)
  2. Tutor          → create group session (Math, 3-step wizard)
  3. Student login  → book the Monday 1-on-1 slot → capture exact time chosen
  4. Print full data summary: subject, session name, slot time, tutor, booking ID

Usage:
  python3 tests/setup_test_data.py
  # Writes reports/setup_data_summary.json + prints human-readable table
"""
from __future__ import annotations
import json, os, re, sys, time, urllib.request
from datetime import date, timedelta
from pathlib import Path
from playwright.sync_api import sync_playwright, Page

# ── Config ─────────────────────────────────────────────────────────────────────
BASE_URL      = os.getenv("BASE_URL",       "https://dev.mehadedu.com/en")
TUTOR_ID      = int(os.getenv("TUTOR_ID",   "89"))
TEACHER_PHONE = os.getenv("TEACHER_PHONE",  os.getenv("TEST_PHONE", "98976564"))
TEACHER_OTP   = os.getenv("TEACHER_OTP",    os.getenv("TEST_OTP",   "123456"))
STUDENT_PHONE = os.getenv("STUDENT_PHONE",  "98765432")
STUDENT_OTP   = os.getenv("STUDENT_OTP",    os.getenv("TEST_OTP",   "123456"))
COUNTRY_NAME  = "Bangladesh"
BID_RE        = re.compile(r"[D]?BK-\d{8}-[A-Z0-9]{4,8}", re.IGNORECASE)

_ROOT    = Path(__file__).parent.parent
_REPORTS = _ROOT / "reports"
_REPORTS.mkdir(exist_ok=True)

# ── Data summary (real values captured during setup) ───────────────────────────
_SUMMARY: dict = {
    "run_at":         time.strftime("%Y-%m-%d %H:%M:%S"),
    "base_url":       BASE_URL,
    "accounts": {
        "tutor_phone":   TEACHER_PHONE,
        "student_phone": STUDENT_PHONE,
        "otp":           "123456",
        "country":       "Bangladesh (+880)",
    },
    "tutor_id": TUTOR_ID,

    # Filled by create_tutor_slots()
    "availability_slots": [],          # [{date, day, start_time, end_time, status}]

    # Filled by create_group_session()
    "group_session": {
        "created":      False,
        "name":         "",
        "subject":      "",
        "level":        "",
        "date":         "",
        "start_time":   "",
        "end_time":     "",
        "max_students": "",
        "price_sar":    "",
        "url":          "",
    },

    # Filled by book_slot_as_student()
    "student_booking": {
        "booking_id":   "",
        "tutor_name":   "",
        "tutor_id":     TUTOR_ID,
        "date":         "",
        "time_slot":    "",      # e.g. "10:00 AM"
        "subject":      "",
        "price_sar":    "",
        "status":       "",
        "payment_url":  "",
    },

    # Visit URLs (for manual verification)
    "visit_urls": {
        "tutor_calendar":        "",
        "tutor_booked_sessions": "",
        "tutor_group_sessions":  "",
        "tutor_earnings":        "",
        "student_bookings":      "",
        "student_wallet":        "",
    },

    "errors": [],
}


# ── Date helpers ────────────────────────────────────────────────────────────────

def _next_weekday(weekday: int, min_days_ahead: int = 2) -> date:
    today = date.today()
    days_ahead = (weekday - today.weekday()) % 7
    if days_ahead < min_days_ahead:
        days_ahead += 7
    return today + timedelta(days=days_ahead)


def _fmt(d: date) -> str:
    return d.strftime("%Y-%m-%d")


def _fmt_display(d: date) -> str:
    return d.strftime("%A, %B %-d, %Y")


MON, TUE, WED = 0, 1, 2

# 1-on-1 slots: (weekday, day_index_in_SMTWTFS, start, end, label)
_SLOTS_1ON1 = [
    (MON, 1, "10:00 AM", "12:00 PM", "Monday 10:00–12:00"),
    (TUE, 2, "2:00 PM",  "4:00 PM",  "Tuesday 14:00–16:00"),
    (WED, 3, "6:00 PM",  "8:00 PM",  "Wednesday 18:00–20:00"),
]

# Group session: next Monday ≥ 8 days ahead (won't clash with 1-on-1 slot)
_GROUP_SUBJECT   = "Math"
_GROUP_NAME      = "QA Automation Math Group Session"
_GROUP_LEVEL     = "Middle School"
_GROUP_DESC      = "Automated QA test group session — real data, no mock"
_GROUP_START     = "10:00 AM"
_GROUP_END       = "12:00 PM"
_GROUP_STUDENTS  = "10"
_GROUP_PRICE     = "50"


# ── URL helpers ─────────────────────────────────────────────────────────────────

def _base() -> str:
    return BASE_URL.rstrip("/").rsplit("/en", 1)[0]


def _url(path: str) -> str:
    return f"{_base()}/en{path}"


# ── Site health check ────────────────────────────────────────────────────────────

def _check_site_up(url: str) -> bool:
    """Return True if the URL responds with HTTP 200. Fast-fail on 5xx/timeout."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        r = urllib.request.urlopen(req, timeout=10)
        return r.status == 200
    except Exception as e:
        return False


# ── OTP login ───────────────────────────────────────────────────────────────────

def _otp_login(pg: Page, phone: str, otp: str, label: str = "") -> None:
    """
    OTP login. Tries mh-login-btn class (desktop header) first,
    then falls back to text-based selector.
    force=True on click skips viewport check — safe at 1280px.
    """
    who = label or phone
    pg.goto(BASE_URL, wait_until="commit", timeout=30000)
    pg.wait_for_timeout(3000)

    # Detect Cloudflare/connection error — bail early with clear message
    title = pg.title()
    if "522" in title or "521" in title or "524" in title or "Connection timed out" in title:
        raise RuntimeError(
            f"Site unreachable ({title}). "
            f"Check BASE_URL={BASE_URL} — is the server up?"
        )
    if "404" in title or "Not Found" in title:
        raise RuntimeError(f"404 on {BASE_URL} — wrong BASE_URL?")

    # Try desktop login button by class first (most reliable), then by text
    login_btn = pg.locator("button.mh-login-btn").first
    if not login_btn.is_visible(timeout=3000):
        login_btn = pg.locator(
            'button:not([aria-label="Login"]):has-text("Log In"), '
            'button:not([aria-label="Login"]):has-text("Login")'
        ).last
    login_btn.wait_for(state="visible", timeout=12000)
    login_btn.scroll_into_view_if_needed()
    login_btn.click(force=True)

    pg.wait_for_selector('[role="dialog"]', state="visible", timeout=12000)
    pg.wait_for_timeout(1000)
    container = pg.locator('[role="dialog"]')

    # Country code
    cc_btn = container.locator(
        'button[aria-label="Country code"], button:has-text("Country code")'
    ).first
    cc_btn.wait_for(state="visible", timeout=8000)
    cc_btn.click()
    pg.wait_for_timeout(700)
    search = pg.locator(
        '[role="listbox"] input[placeholder*="Search"], input[placeholder="Search..."]'
    ).first
    search.wait_for(state="visible", timeout=5000)
    search.fill(COUNTRY_NAME)
    pg.wait_for_timeout(600)
    pg.locator(f'[role="option"]:has-text("{COUNTRY_NAME}")').first.click()
    pg.wait_for_timeout(500)

    # Phone number
    phone_input = container.locator('input[type="tel"], input[placeholder*="123"]').first
    phone_input.wait_for(state="visible", timeout=8000)
    phone_input.fill(phone)
    pg.wait_for_timeout(400)
    container.locator('button:has-text("Send Code")').first.click()
    pg.wait_for_timeout(2000)

    # OTP
    otp_input = container.locator('input[placeholder="000000"]').first
    otp_input.wait_for(state="visible", timeout=20000)
    for _ in range(40):
        pg.wait_for_timeout(1000)
        if not otp_input.is_disabled():
            break
    otp_input.fill(otp)
    pg.wait_for_timeout(800)
    container.locator('button:has-text("Continue")').first.click()
    pg.wait_for_timeout(4000)
    print(f"[SETUP] Login OK ({who}) → {pg.url}", flush=True)


# ── Combobox / day-button helpers ────────────────────────────────────────────────

def _pick_combobox(pg: Page, dlg_locator, index: int, value: str) -> bool:
    """Select *value* from the Nth combobox within *dlg_locator* (0=first, 1=second)."""
    try:
        # Native <select>
        selects = dlg_locator.locator("select")
        if selects.count() > index:
            selects.nth(index).select_option(label=value)
            pg.wait_for_timeout(400)
            return True
        # React/custom combobox
        cbs = dlg_locator.locator('[role="combobox"]')
        if cbs.count() > index:
            cbs.nth(index).click()
            pg.wait_for_timeout(600)
            opt = pg.locator(f'[role="option"]:has-text("{value}")').first
            if opt.count() > 0:
                opt.click()
                pg.wait_for_timeout(400)
                return True
    except Exception as e:
        print(f"[SETUP] combobox[{index}]={value} error: {e}", flush=True)
    return False


def _click_day_button(pg: Page, dlg_locator, day_index: int, day_letter: str) -> bool:
    """Click the Nth day toggle button (S M T W T F S — index 0–6)."""
    try:
        # Single-letter buttons in the dialog row
        row = dlg_locator.locator("button").filter(
            has_text=re.compile(r"^[SMTWFsmtwf]$")
        )
        if row.count() >= day_index + 1:
            row.nth(day_index).click()
            pg.wait_for_timeout(400)
            return True
        # aria-label fallback
        btn = dlg_locator.locator(
            f'[aria-label="{day_letter}"], [data-day="{day_letter}"]'
        ).first
        if btn.count() > 0:
            btn.click()
            pg.wait_for_timeout(400)
            return True
    except Exception as e:
        print(f"[SETUP] day-button[{day_index}] error: {e}", flush=True)
    return False


def _fill_date_input(dlg_locator, nth: int, date_str: str) -> bool:
    """Fill the Nth date input in the dialog with YYYY-MM-DD."""
    try:
        inp = dlg_locator.locator('input[type="date"]').nth(nth)
        if inp.count() > 0:
            inp.fill(date_str)
            return True
        # Placeholder-based
        labels = ["From", "To"]
        lbl = labels[nth] if nth < len(labels) else ""
        if lbl:
            inp2 = dlg_locator.locator(
                f'input[placeholder*="{lbl}"], input[aria-label*="{lbl}"]'
            ).first
            if inp2.count() > 0:
                inp2.fill(date_str)
                return True
    except Exception as e:
        print(f"[SETUP] date-input[{nth}]={date_str} error: {e}", flush=True)
    return False


# ══════════════════════════════════════════════════════════════════════════════════
# STEP 1 — Tutor creates 1-on-1 availability slots
# ══════════════════════════════════════════════════════════════════════════════════

def _create_one_availability_slot(
    pg: Page, weekday: int, day_idx: int, start: str, end: str, label: str
) -> bool:
    """Open 'Add Availability Time' modal and create one slot. Returns True on success."""
    slot_date = _next_weekday(weekday, min_days_ahead=2)
    date_str  = _fmt(slot_date)
    print(f"[SETUP]   Slot: {label} on {date_str}", flush=True)

    add_btn = pg.locator(
        'button:has-text("Add Availability Time"), '
        'button:has-text("Add Availability"), '
        'button:has-text("Add Time")'
    ).first
    if not add_btn.is_visible(timeout=6000):
        print("[SETUP]   'Add Availability Time' button not visible", flush=True)
        return False

    add_btn.click()
    pg.wait_for_timeout(1500)
    try:
        pg.wait_for_selector('[role="dialog"]', state="visible", timeout=8000)
    except Exception:
        print("[SETUP]   Availability dialog did not open", flush=True)
        return False

    dlg = pg.locator('[role="dialog"]')
    pg.wait_for_timeout(800)

    _fill_date_input(dlg, 0, date_str)   # From
    pg.wait_for_timeout(300)
    _fill_date_input(dlg, 1, date_str)   # To (same — single day slot)
    pg.wait_for_timeout(300)
    _click_day_button(pg, dlg, day_idx, ["S","M","T","W","T","F","S"][day_idx])
    pg.wait_for_timeout(300)
    _pick_combobox(pg, dlg, 0, start)    # Start Time
    pg.wait_for_timeout(300)
    _pick_combobox(pg, dlg, 1, end)      # End Time
    pg.wait_for_timeout(400)

    apply = dlg.locator(
        'button:has-text("Apply"), button:has-text("Save"), button:has-text("Confirm")'
    ).first
    try:
        apply.wait_for(state="enabled", timeout=6000)
        apply.click()
        pg.wait_for_timeout(2000)
        # Consider success if dialog closed or a toast appeared
        toast = pg.locator('[role="alert"], .toast, [class*="toast"], [class*="success"]')
        closed = pg.locator('[role="dialog"]').count() == 0
        ok = closed or toast.count() > 0
        if ok:
            _SUMMARY["availability_slots"].append({
                "date":       date_str,
                "display":    _fmt_display(slot_date),
                "day":        ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"][day_idx],
                "start_time": start,
                "end_time":   end,
                "label":      label,
                "status":     "created",
            })
            print(f"[SETUP]   ✓ Slot created: {label} {date_str} {start}–{end}", flush=True)
            return True
        else:
            print(f"[SETUP]   ! Apply clicked but dialog still open — may have failed", flush=True)
    except Exception as e:
        print(f"[SETUP]   Apply failed: {e}", flush=True)

    # Cancel to clean up
    try:
        dlg.locator('button:has-text("Cancel")').first.click()
        pg.wait_for_timeout(800)
    except Exception:
        pass
    return False


def create_tutor_slots(pg: Page) -> None:
    print("[SETUP] === Creating 1-on-1 availability slots ===", flush=True)
    pg.goto(_url("/dashboard/availability"), wait_until="commit", timeout=25000)
    pg.wait_for_timeout(3000)
    _SUMMARY["visit_urls"]["tutor_calendar"] = _url("/dashboard/availability")

    if "/dashboard" not in pg.url:
        _SUMMARY["errors"].append(f"Tutor not on dashboard after login — {pg.url}")
        return

    for weekday, day_idx, start, end, label in _SLOTS_1ON1:
        try:
            _create_one_availability_slot(pg, weekday, day_idx, start, end, label)
        except Exception as e:
            err = f"Slot creation failed ({label}): {e}"
            print(f"[SETUP]   ✗ {err}", flush=True)
            _SUMMARY["errors"].append(err)
        # Return to availability page between slots
        pg.goto(_url("/dashboard/availability"), wait_until="commit", timeout=20000)
        pg.wait_for_timeout(2000)


# ══════════════════════════════════════════════════════════════════════════════════
# STEP 2 — Tutor creates group session (3-step wizard)
# ══════════════════════════════════════════════════════════════════════════════════

def create_group_session(pg: Page) -> bool:
    """
    3-step wizard from /dashboard/availability → 'Group sessions' button.
    Step 1: Session Name + Level + Description
    Step 2: Date range + day + Start/End time + Max Students
    Step 3: Price → Create
    """
    print("[SETUP] === Creating group session ===", flush=True)
    pg.goto(_url("/dashboard/availability"), wait_until="commit", timeout=25000)
    pg.wait_for_timeout(3000)
    _SUMMARY["visit_urls"]["tutor_group_sessions"] = _url("/dashboard/group-sessions")

    # Entry point: 'Group sessions' button in page header
    grp_btn = pg.locator(
        'button:has-text("Group sessions"), button:has-text("Group Sessions")'
    ).first
    if not grp_btn.is_visible(timeout=6000):
        err = "'Group sessions' button not found on availability page"
        print(f"[SETUP]   ✗ {err}", flush=True)
        _SUMMARY["errors"].append(err)
        return False

    grp_btn.click()
    pg.wait_for_timeout(1500)
    try:
        pg.wait_for_selector('[role="dialog"]', state="visible", timeout=10000)
    except Exception:
        err = "Group session wizard dialog did not open"
        print(f"[SETUP]   ✗ {err}", flush=True)
        _SUMMARY["errors"].append(err)
        return False

    dlg = pg.locator('[role="dialog"]')
    pg.wait_for_timeout(1000)

    # ── Step 1: Session Info ──────────────────────────────────────────────────
    print("[SETUP]   Step 1: Session Info", flush=True)

    # Session Name
    name_input = dlg.locator(
        'input[placeholder*="Session Name"], input[name*="name"], '
        '[aria-label*="Session Name"], textbox'
    ).first
    try:
        name_input.wait_for(state="visible", timeout=5000)
        name_input.fill(_GROUP_NAME)
        pg.wait_for_timeout(400)
        print(f"[SETUP]     Session Name: {_GROUP_NAME}", flush=True)
    except Exception as e:
        print(f"[SETUP]     Session Name fill failed: {e}", flush=True)

    # Subject is read-only — capture auto-filled value
    subject_val = ""
    try:
        subj_input = dlg.locator(
            'input[readonly][placeholder*="Subject"], input[readonly][name*="subject"], '
            'input[readonly]'
        ).first
        if subj_input.count() > 0:
            subject_val = subj_input.input_value(timeout=3000)
        if not subject_val:
            # Try reading the field value text
            subj_field = dlg.locator(':has-text("Subject")').first
            if subj_field.count() > 0:
                txt = subj_field.inner_text()
                m = re.search(r"Subject[:\s]+(\w[\w\s]*)", txt)
                if m:
                    subject_val = m.group(1).strip()
        subject_val = subject_val or _GROUP_SUBJECT
        print(f"[SETUP]     Subject: {subject_val} (auto-filled, read-only)", flush=True)
    except Exception:
        subject_val = _GROUP_SUBJECT

    # Level
    level_set = False
    try:
        level_cb = dlg.locator(
            'select[aria-label*="Level"], [role="combobox"][aria-label*="Level"], '
            '[placeholder*="Level"], input[name*="level"]'
        ).first
        if level_cb.count() > 0:
            tag = level_cb.evaluate("el => el.tagName.toLowerCase()")
            if tag == "select":
                level_cb.select_option(label=_GROUP_LEVEL)
            else:
                level_cb.click()
                pg.wait_for_timeout(400)
                opt = pg.locator(f'[role="option"]:has-text("{_GROUP_LEVEL}")').first
                if opt.count() > 0:
                    opt.click()
            level_set = True
            print(f"[SETUP]     Level: {_GROUP_LEVEL}", flush=True)
        pg.wait_for_timeout(300)
    except Exception as e:
        print(f"[SETUP]     Level field: {e}", flush=True)

    # Description (optional)
    try:
        desc = dlg.locator("textarea").first
        if desc.count() > 0:
            desc.fill(_GROUP_DESC)
            pg.wait_for_timeout(300)
    except Exception:
        pass

    # Click Next → Step 2
    next_btn = dlg.locator(
        'button:has-text("Next"), button:has-text("Continue"), button:has-text("Next Step")'
    ).first
    try:
        next_btn.wait_for(state="enabled", timeout=6000)
        next_btn.click()
        pg.wait_for_timeout(1500)
        print("[SETUP]     → Step 2", flush=True)
    except Exception as e:
        err = f"Group session Step1 Next failed: {e}"
        print(f"[SETUP]   ✗ {err}", flush=True)
        _SUMMARY["errors"].append(err)
        try:
            dlg.locator('button:has-text("Cancel")').first.click()
        except Exception:
            pass
        return False

    # ── Step 2: Schedule ──────────────────────────────────────────────────────
    print("[SETUP]   Step 2: Schedule", flush=True)
    pg.wait_for_timeout(800)

    grp_date   = _next_weekday(MON, min_days_ahead=8)
    grp_ds     = _fmt(grp_date)
    grp_disp   = _fmt_display(grp_date)

    _fill_date_input(dlg, 0, grp_ds)   # From
    pg.wait_for_timeout(300)
    _fill_date_input(dlg, 1, grp_ds)   # To
    pg.wait_for_timeout(300)
    _click_day_button(pg, dlg, 1, "M") # Monday = index 1 in S M T W T F S
    pg.wait_for_timeout(300)
    _pick_combobox(pg, dlg, 0, _GROUP_START)  # Start Time
    pg.wait_for_timeout(300)
    _pick_combobox(pg, dlg, 1, _GROUP_END)    # End Time
    pg.wait_for_timeout(300)

    # Max Students
    try:
        max_inp = dlg.locator(
            'input[placeholder*="Max"], input[name*="max"], '
            'input[type="number"][aria-label*="Student"]'
        ).first
        if max_inp.count() > 0:
            max_inp.fill(_GROUP_STUDENTS)
            pg.wait_for_timeout(300)
            print(f"[SETUP]     Max Students: {_GROUP_STUDENTS}", flush=True)
    except Exception as e:
        print(f"[SETUP]     Max Students field: {e}", flush=True)

    print(f"[SETUP]     Date: {grp_disp} | {_GROUP_START}–{_GROUP_END}", flush=True)

    next_btn2 = dlg.locator(
        'button:has-text("Next"), button:has-text("Continue"), button:has-text("Next Step")'
    ).first
    try:
        next_btn2.wait_for(state="enabled", timeout=6000)
        next_btn2.click()
        pg.wait_for_timeout(1500)
        print("[SETUP]     → Step 3", flush=True)
    except Exception as e:
        err = f"Group session Step2 Next failed: {e}"
        print(f"[SETUP]   ✗ {err}", flush=True)
        _SUMMARY["errors"].append(err)
        try:
            dlg.locator('button:has-text("Cancel")').first.click()
        except Exception:
            pass
        return False

    # ── Step 3: Pricing ───────────────────────────────────────────────────────
    print("[SETUP]   Step 3: Pricing", flush=True)
    pg.wait_for_timeout(800)

    try:
        price_inp = dlg.locator(
            'input[placeholder*="Price"], input[name*="price"], '
            'input[type="number"][aria-label*="Price"], input[type="number"]'
        ).first
        if price_inp.count() > 0:
            price_inp.fill(_GROUP_PRICE)
            pg.wait_for_timeout(300)
            print(f"[SETUP]     Price: {_GROUP_PRICE} SAR per student", flush=True)
    except Exception as e:
        print(f"[SETUP]     Price field: {e}", flush=True)

    create_btn = dlg.locator(
        'button:has-text("Create"), button:has-text("Submit"), button:has-text("Publish")'
    ).first
    try:
        create_btn.wait_for(state="enabled", timeout=6000)
        create_btn.click()
        pg.wait_for_timeout(3000)
        # Check success: dialog closed OR toast appeared
        closed = pg.locator('[role="dialog"]').count() == 0
        toast  = pg.locator('[role="alert"], .toast, [class*="success"]').count() > 0
        ok = closed or toast
        if ok:
            _SUMMARY["group_session"] = {
                "created":      True,
                "name":         _GROUP_NAME,
                "subject":      subject_val,
                "level":        _GROUP_LEVEL if level_set else "not set",
                "date":         grp_ds,
                "display_date": grp_disp,
                "start_time":   _GROUP_START,
                "end_time":     _GROUP_END,
                "max_students": _GROUP_STUDENTS,
                "price_sar":    _GROUP_PRICE,
                "url":          _url("/dashboard/group-sessions"),
            }
            print(f"[SETUP]   ✓ Group session created: {_GROUP_NAME}", flush=True)
            return True
        else:
            err = "Create clicked but dialog still open — group session may not have saved"
            print(f"[SETUP]   ! {err}", flush=True)
            _SUMMARY["errors"].append(err)
    except Exception as e:
        err = f"Group session Create button failed: {e}"
        print(f"[SETUP]   ✗ {err}", flush=True)
        _SUMMARY["errors"].append(err)

    return False


# ══════════════════════════════════════════════════════════════════════════════════
# STEP 3 — Student books a 1-on-1 slot
# ══════════════════════════════════════════════════════════════════════════════════

def book_slot_as_student(pg: Page) -> str:
    """
    Student books tutor 89's Monday 10:00 AM slot.
    Returns booking ID.
    Captures: tutor name, date, exact time slot, subject, price.
    """
    print("[SETUP] === Student booking ===", flush=True)
    _SUMMARY["visit_urls"]["student_bookings"] = _url("/dashboard/bookings")
    _SUMMARY["visit_urls"]["student_wallet"]   = _url("/dashboard/wallet")

    # First: check if a booking already exists
    pg.goto(_url("/dashboard/bookings"), wait_until="commit", timeout=25000)
    pg.wait_for_timeout(4000)
    existing = BID_RE.findall(pg.content())
    if existing:
        bid = existing[0]
        print(f"[SETUP]   Existing booking found: {bid}", flush=True)
        # Capture tutor name from the booking card if possible
        tutor_name_existing = ""
        try:
            tutor_name_existing = pg.locator('[class*="tutor"], [class*="teacher"]').first.inner_text(timeout=2000).strip().splitlines()[0]
        except Exception:
            pass
        _SUMMARY["student_booking"].update({
            "booking_id":  bid,
            "tutor_name":  tutor_name_existing or f"Tutor {TUTOR_ID}",
            "status":      "existing_booking",
        })
        # Always write the file so RT test can use this ID
        (_REPORTS / "setup_booking_id.txt").write_text(bid)
        print(f"[SETUP]   ✓ setup_booking_id.txt written: {bid}", flush=True)
        return bid

    # Navigate to tutor profile
    tutor_url = _url(f"/tutor/{TUTOR_ID}")
    pg.goto(tutor_url, wait_until="commit", timeout=25000)
    pg.wait_for_timeout(3000)

    # Capture tutor name and subject from profile
    tutor_name, subject, price_sar = "", "", ""
    try:
        tutor_name = pg.locator("h1, h2").first.inner_text(timeout=3000).strip().splitlines()[0]
        print(f"[SETUP]   Tutor: {tutor_name}", flush=True)
    except Exception:
        tutor_name = f"Tutor {TUTOR_ID}"

    try:
        # Subject from profile (e.g. "Math")
        subj_el = pg.locator(':has-text("Math"), :has-text("Subject")').first
        txt = subj_el.inner_text(timeout=2000)
        m = re.search(r"\b(Math|English|Science|Arabic|Physics|Chemistry|Biology)\b", txt, re.I)
        if m:
            subject = m.group(1)
    except Exception:
        pass

    try:
        # Price from profile
        price_el = pg.locator(':has-text("SAR"), :has-text("per hour")').first
        ptxt = price_el.inner_text(timeout=2000)
        pm = re.search(r"(\d+(?:\.\d+)?)\s*SAR", ptxt)
        if pm:
            price_sar = pm.group(1)
    except Exception:
        pass

    _SUMMARY["student_booking"].update({
        "tutor_name": tutor_name,
        "subject":    subject or "",          # empty if not found — don't assume group subject
        "price_sar":  price_sar,
    })

    # Click "Book Trial Lesson" (specific button from spec)
    # Retry reload up to 3 times — slots may take a moment to appear after tutor creation
    book_btn = pg.locator(
        'button:has-text("Book Trial Lesson"), '
        'button:has-text("Book Trial"), '
        'button:has-text("Book")'
    ).first
    for _attempt in range(3):
        if book_btn.is_visible(timeout=8000):
            break
        print(f"[SETUP]   Book button not visible (attempt {_attempt+1}/3) — reloading tutor profile", flush=True)
        pg.reload(wait_until="commit", timeout=20000)
        pg.wait_for_timeout(3000)
    else:
        err = f"No booking button on tutor {TUTOR_ID} profile — no available slots (3 attempts)"
        print(f"[SETUP]   ✗ {err}", flush=True)
        _SUMMARY["errors"].append(err)
        _SUMMARY["student_booking"]["status"] = "no_book_button"
        return ""

    book_btn.click()
    pg.wait_for_timeout(1500)

    # Handle "Book a Session" dialog
    try:
        pg.wait_for_selector('[role="dialog"]', state="visible", timeout=15000)
    except Exception:
        if "/payment" in pg.url:
            m = BID_RE.search(pg.url)
            return m.group(0) if m else ""
        err = "Booking dialog did not open"
        print(f"[SETUP]   ✗ {err}", flush=True)
        _SUMMARY["errors"].append(err)
        _SUMMARY["student_booking"]["status"] = "dialog_not_opened"
        return ""

    pg.wait_for_timeout(1500)
    dlg = pg.locator('[role="dialog"]')

    try:
        dlg_title = dlg.locator("h2, h3").first.inner_text(timeout=4000)
    except Exception:
        dlg_title = ""

    chosen_date, chosen_time = "", ""

    if "Package" in dlg_title or "hour" in dlg_title.lower():
        # Package booking dialog
        chosen_date, chosen_time = _book_package(pg, dlg)
    else:
        # Trial/calendar slot picker
        chosen_date, chosen_time = _book_trial_with_capture(pg, dlg)

    if not chosen_time:
        err = "No available time slot found in booking dialog"
        print(f"[SETUP]   ✗ {err}", flush=True)
        _SUMMARY["errors"].append(err)
        _SUMMARY["student_booking"]["status"] = "no_slots_available"
        return ""

    print(f"[SETUP]   Selected: {chosen_date} at {chosen_time}", flush=True)
    pg.wait_for_timeout(2500)

    # Extract booking ID from URL
    m = BID_RE.search(pg.url)
    bid = m.group(0) if m else ""
    purl = pg.url if "/payment" in pg.url else ""

    # Fallback: check page HTML for booking ID
    if not bid:
        bids = BID_RE.findall(pg.content())
        bid = bids[0] if bids else ""

    _SUMMARY["student_booking"].update({
        "booking_id":  bid,
        "date":        chosen_date,
        "time_slot":   chosen_time,
        "status":      "created_pending_payment" if bid else "payment_page_no_id",
        "payment_url": purl,
    })

    if bid:
        (_REPORTS / "setup_booking_id.txt").write_text(bid)
        print(f"[SETUP]   ✓ Booking ID: {bid}", flush=True)
    else:
        print(f"[SETUP]   ! No booking ID captured — URL: {pg.url}", flush=True)

    return bid


def _book_package(pg: Page, dlg) -> tuple[str, str]:
    """Handle package-type booking dialog. Returns (date_str, time_str)."""
    pg.wait_for_timeout(1000)
    card = pg.locator('[role="dialog"] .cursor-pointer:has(h3:has-text("1 hr"))')
    if card.count() == 0:
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
        with pg.expect_navigation(timeout=25000):
            pg.locator('[role="dialog"] button').filter(
                has_text=re.compile(r"Confirm|Pay", re.I)
            ).first.click()
    except Exception:
        pass

    # Capture actual booking date+time from payment page URL or page text
    pkg_date, pkg_time = "", ""
    try:
        pg.wait_for_timeout(2000)
        url_txt = pg.url + " " + pg.inner_text("body")
        # Try to extract a date (YYYY-MM-DD or Month Day) and time (HH:MM AM/PM)
        dm = re.search(r"\d{4}-\d{2}-\d{2}", url_txt)
        if dm:
            pkg_date = dm.group(0)
        tm = re.search(r"\d{1,2}:\d{2}\s*(?:AM|PM)", url_txt, re.I)
        if tm:
            pkg_time = tm.group(0).strip()
    except Exception:
        pass
    return (pkg_date or "package", pkg_time or "package")


def _resolve_clicked_date(dlg, day_num_str: str) -> str:
    """
    Given the day-number text that was clicked (e.g. "7" or "14"),
    read the month/year from the calendar header and compute a YYYY-MM-DD string.
    Falls back to target_date-based calculation if the header can't be parsed.
    """
    try:
        # Calendar header typically reads "June 2026" or "Jun 2026"
        header = dlg.locator(
            '[class*="month"], [class*="header"], h2, h3, '
            '[aria-label*="2026"], [aria-label*="2025"]'
        ).first
        hdr_txt = header.inner_text(timeout=2000).strip()
        # Parse "June 2026" or "Jun 2026"
        m = re.search(
            r"(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|"
            r"Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|"
            r"Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+(\d{4})",
            hdr_txt, re.I
        )
        if m:
            month_str = m.group(1)[:3].capitalize()
            year      = int(m.group(2))
            day       = int(day_num_str)
            from datetime import datetime
            parsed = datetime.strptime(f"{day} {month_str} {year}", "%d %b %Y")
            return parsed.strftime("%Y-%m-%d")
    except Exception:
        pass
    return ""   # caller will use fallback


def _book_trial_with_capture(pg: Page, dlg) -> tuple[str, str]:
    """
    Navigate booking calendar to Monday slot. Click day → pick time slot → Continue → Pay.
    Returns (date_chosen, time_chosen) — both are REAL values from what was actually clicked.
    """
    slot_re  = re.compile(r"\d+:\d+\s*(AM|PM)", re.I)
    chosen_date, chosen_time = "", ""

    # Select "1 hour" duration if present
    dur = dlg.locator('button:has-text("1 hour"), button:has-text("1 Hour")')
    if dur.count() > 0:
        dur.first.click()
        pg.wait_for_timeout(500)

    # Primary target: next Monday ≥ 2 days from today
    target_date = _next_weekday(MON, min_days_ahead=2)
    target_day  = target_date.strftime("%-d")   # e.g. "7" or "14"

    # Navigate weeks until target Monday is visible, or time slots already show
    for _nav_attempt in range(8):
        slots = dlg.locator("button").filter(has_text=slot_re)
        vis_slots = [slots.nth(i) for i in range(slots.count())
                     if slots.nth(i).is_visible() and not slots.nth(i).is_disabled()]

        if vis_slots:
            # Time slots already visible — capture and click
            chosen_time = vis_slots[0].inner_text().strip()
            vis_slots[0].click()
            pg.wait_for_timeout(600)
            chosen_date = _resolve_clicked_date(dlg, target_day) or _fmt(target_date)
            break

        day_btn = dlg.locator(
            f'button:has-text("{target_day}"):not([disabled]), '
            f'[role="button"]:has-text("{target_day}"):not([aria-disabled="true"])'
        ).first
        if day_btn.count() > 0 and day_btn.is_visible():
            day_btn.first.click()
            pg.wait_for_timeout(1000)
            slots2 = dlg.locator("button").filter(has_text=slot_re)
            vis2   = [slots2.nth(i) for i in range(slots2.count())
                      if slots2.nth(i).is_visible() and not slots2.nth(i).is_disabled()]
            if vis2:
                chosen_time = vis2[0].inner_text().strip()
                vis2[0].click()
                pg.wait_for_timeout(600)
                chosen_date = _resolve_clicked_date(dlg, target_day) or _fmt(target_date)
                break

        # Navigate forward one week to find slots
        try:
            nw = dlg.locator(
                'button:has-text("Next week"), button:has-text("Next Week"), '
                'button[aria-label*="next"], button[aria-label*="Next"]'
            ).first
            if nw.is_visible(timeout=2000):
                nw.click()
                pg.wait_for_timeout(1000)
            else:
                break
        except Exception:
            break

    if not chosen_time:
        # Fallback: click ANY enabled day, capture that day's actual date from header
        for _ in range(5):
            all_days = dlg.locator("button").filter(has_text=re.compile(r"^\d{1,2}$"))
            for i in range(all_days.count()):
                d = all_days.nth(i)
                try:
                    if not d.is_disabled() and d.is_visible():
                        actual_day_num = d.inner_text().strip()
                        d.click()
                        pg.wait_for_timeout(1000)
                        slots3 = dlg.locator("button").filter(has_text=slot_re)
                        vis3   = [slots3.nth(j) for j in range(slots3.count())
                                  if slots3.nth(j).is_visible() and not slots3.nth(j).is_disabled()]
                        if vis3:
                            chosen_time = vis3[0].inner_text().strip()
                            vis3[0].click()
                            pg.wait_for_timeout(600)
                            # Resolve ACTUAL clicked date — not the pre-computed target_date
                            chosen_date = (
                                _resolve_clicked_date(dlg, actual_day_num)
                                or _fmt(target_date)   # last-resort fallback only
                            )
                            break
                except Exception:
                    continue
            if chosen_time:
                break
            try:
                nw2 = dlg.locator('button:has-text("Next week")').first
                if nw2.is_visible(timeout=2000):
                    nw2.click()
                    pg.wait_for_timeout(1000)
                else:
                    break
            except Exception:
                break

    if not chosen_time:
        return ("", "")

    # Step 1 → Continue
    cont = dlg.locator('button:has-text("Continue")').first
    for _ in range(25):
        if cont.is_enabled():
            break
        pg.wait_for_timeout(300)
    try:
        cont.click()
        pg.wait_for_timeout(1500)
    except Exception as e:
        print(f"[SETUP]   Continue failed: {e}", flush=True)

    # Step 2: Confirm/Pay → navigate to payment page
    confirm = dlg.locator("button").filter(has_text=re.compile(r"Confirm|Pay", re.I)).first
    try:
        with pg.expect_navigation(timeout=25000):
            confirm.click()
    except Exception:
        pass

    return (chosen_date, chosen_time)


# ══════════════════════════════════════════════════════════════════════════════════
# Verification checks (read-only, tutor side)
# ══════════════════════════════════════════════════════════════════════════════════

def verify_tutor_data(pg: Page) -> None:
    """Check booked sessions and earnings — capture current state."""
    print("[SETUP] === Verifying tutor dashboard data ===", flush=True)

    # Booked sessions
    bs_url = _url("/dashboard/booked-sessions")
    _SUMMARY["visit_urls"]["tutor_booked_sessions"] = bs_url
    pg.goto(bs_url, wait_until="commit", timeout=25000)
    pg.wait_for_timeout(3000)
    bids = BID_RE.findall(pg.content())
    body = pg.inner_text("body")
    _SUMMARY["tutor_booked_sessions"] = {
        "url":              pg.url,
        "booking_ids":      bids[:5],
        "has_upcoming":     "upcoming" in body.lower() or "Upcoming" in body,
        "sessions_visible": len(bids) > 0,
    }
    print(f"[SETUP]   Booked sessions — BIDs visible: {bids[:3]}", flush=True)

    # Earnings
    earn_url = _url("/dashboard/earnings")
    _SUMMARY["visit_urls"]["tutor_earnings"] = earn_url
    pg.goto(earn_url, wait_until="commit", timeout=25000)
    pg.wait_for_timeout(3000)
    body2 = pg.inner_text("body")
    amounts = re.findall(r"(\d+(?:\.\d{2})?)\s*SAR", body2, re.I)
    nonzero = [a for a in amounts if float(a.replace(",", "")) > 0]
    _SUMMARY["tutor_earnings"] = {
        "url":          pg.url,
        "has_earnings": "No earnings yet." not in body2,
        "amounts_sar":  amounts[:5],
        "nonzero_sar":  nonzero[:3],
        "note":         "Earnings populate only after admin marks session complete",
    }
    print(
        f"[SETUP]   Earnings — "
        f"{'EXISTS: ' + str(nonzero[:3]) if nonzero else 'EMPTY (no completed sessions yet)'}",
        flush=True
    )


# ══════════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════════

def main() -> str:
    booking_id = ""

    # Fast-fail if site is unreachable — avoids 10s× timeouts per login attempt
    print(f"[SETUP] Checking site reachability: {BASE_URL} ...", flush=True)
    if not _check_site_up(BASE_URL):
        msg = (
            f"[SETUP] ABORT: {BASE_URL} is unreachable (connection timeout / 5xx).\n"
            f"[SETUP] Fix: set BASE_URL env var to a live server, e.g.\n"
            f"[SETUP]   export BASE_URL=https://mehadedu.com/en\n"
            f"[SETUP] Then re-run: python3 tests/setup_test_data.py"
        )
        print(msg, flush=True)
        _SUMMARY["errors"].append(f"Site unreachable: {BASE_URL}")
        (_REPORTS / "setup_data_summary.json").write_text(
            json.dumps(_SUMMARY, indent=2, default=str)
        )
        sys.exit(1)
    print(f"[SETUP] Site OK — starting setup\n", flush=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # ── Tutor: create slots + group session ─────────────────────────────────
        tutor_ctx = browser.new_context(
            viewport={"width": 1280, "height": 720},
            ignore_https_errors=True, locale="en-US",
        )
        tutor_pg = tutor_ctx.new_page()
        try:
            _otp_login(tutor_pg, TEACHER_PHONE, TEACHER_OTP, "tutor")
            create_tutor_slots(tutor_pg)
            create_group_session(tutor_pg)
        except Exception as e:
            err = f"Tutor setup error: {e}"
            print(f"[SETUP] {err}", flush=True)
            _SUMMARY["errors"].append(err)
        finally:
            tutor_ctx.close()

        # ── Student: book a 1-on-1 slot ─────────────────────────────────────────
        student_ctx = browser.new_context(
            viewport={"width": 1280, "height": 720},
            ignore_https_errors=True, locale="en-US",
        )
        student_pg = student_ctx.new_page()
        try:
            _otp_login(student_pg, STUDENT_PHONE, STUDENT_OTP, "student")
            booking_id = book_slot_as_student(student_pg)
        except Exception as e:
            err = f"Student booking error: {e}"
            print(f"[SETUP] {err}", flush=True)
            _SUMMARY["errors"].append(err)
        finally:
            student_ctx.close()

        # ── Tutor: verify dashboard shows the booking + check earnings ───────────
        tutor_ctx2 = browser.new_context(
            viewport={"width": 1280, "height": 720},
            ignore_https_errors=True, locale="en-US",
        )
        tutor_pg2 = tutor_ctx2.new_page()
        try:
            _otp_login(tutor_pg2, TEACHER_PHONE, TEACHER_OTP, "tutor-verify")
            verify_tutor_data(tutor_pg2)
        except Exception as e:
            err = f"Tutor verify error: {e}"
            print(f"[SETUP] {err}", flush=True)
            _SUMMARY["errors"].append(err)
        finally:
            tutor_ctx2.close()

        browser.close()

    # ── Save JSON report ──────────────────────────────────────────────────────────
    report_path = _REPORTS / "setup_data_summary.json"
    report_path.write_text(json.dumps(_SUMMARY, indent=2, default=str))

    # ── Human-readable console report ────────────────────────────────────────────
    sb  = _SUMMARY["student_booking"]
    gs  = _SUMMARY["group_session"]
    av  = _SUMMARY["availability_slots"]
    tbs = _SUMMARY.get("tutor_booked_sessions", {})
    te  = _SUMMARY.get("tutor_earnings", {})
    vu  = _SUMMARY["visit_urls"]

    print("\n" + "═" * 65, flush=True)
    print("  SETUP DATA REPORT", flush=True)
    print("═" * 65, flush=True)
    print(f"  Run at      : {_SUMMARY['run_at']}", flush=True)
    print(f"  Platform    : {BASE_URL}", flush=True)
    print(f"  Tutor phone : {TEACHER_PHONE}  (OTP 123456)", flush=True)
    print(f"  Student phone:{STUDENT_PHONE}  (OTP 123456)", flush=True)
    print(flush=True)

    print("  ┌─ 1-ON-1 AVAILABILITY SLOTS CREATED ─────────────────────┐", flush=True)
    if av:
        for s in av:
            print(f"  │  ✓ {s['display']:<30} {s['start_time']}–{s['end_time']}", flush=True)
    else:
        print("  │  (none created — slots may already exist or modal failed)", flush=True)
    print("  └──────────────────────────────────────────────────────────┘", flush=True)
    print(flush=True)

    print("  ┌─ GROUP SESSION CREATED ──────────────────────────────────┐", flush=True)
    if gs.get("created"):
        print(f"  │  Name       : {gs['name']}", flush=True)
        print(f"  │  Subject    : {gs['subject']}", flush=True)
        print(f"  │  Level      : {gs['level']}", flush=True)
        print(f"  │  Date       : {gs.get('display_date', gs['date'])}", flush=True)
        print(f"  │  Time       : {gs['start_time']} – {gs['end_time']}", flush=True)
        print(f"  │  Max students: {gs['max_students']}", flush=True)
        print(f"  │  Price      : {gs['price_sar']} SAR per student", flush=True)
        print(f"  │  View at    : {gs['url']}", flush=True)
    else:
        print("  │  (not created — wizard may have failed; see errors below)", flush=True)
    print("  └──────────────────────────────────────────────────────────┘", flush=True)
    print(flush=True)

    print("  ┌─ STUDENT BOOKING ───────────────────────────────────────┐", flush=True)
    print(f"  │  Tutor      : {sb.get('tutor_name', '—')}", flush=True)
    print(f"  │  Subject    : {sb.get('subject', '—')}", flush=True)
    print(f"  │  Date       : {sb.get('date', '—')}", flush=True)
    print(f"  │  Time slot  : {sb.get('time_slot', '—')}", flush=True)
    print(f"  │  Price      : {sb.get('price_sar', '—')} SAR", flush=True)
    print(f"  │  Booking ID : {sb.get('booking_id', 'NOT CAPTURED')}", flush=True)
    print(f"  │  Status     : {sb.get('status', '—')}", flush=True)
    print("  └──────────────────────────────────────────────────────────┘", flush=True)
    print(flush=True)

    print("  ┌─ TUTOR DASHBOARD AFTER BOOKING ─────────────────────────┐", flush=True)
    print(f"  │  Booked session IDs visible : {tbs.get('booking_ids', [])[:3]}", flush=True)
    print(f"  │  Earnings (SAR)             : {te.get('nonzero_sar', []) or 'empty'}", flush=True)
    print(f"  │  Earnings note              : {te.get('note', '')}", flush=True)
    print("  └──────────────────────────────────────────────────────────┘", flush=True)
    print(flush=True)

    print("  ┌─ VISIT THESE URLS TO SEE THE DATA ─────────────────────┐", flush=True)
    labels = {
        "tutor_calendar":        "Tutor calendar (slots)",
        "tutor_booked_sessions": "Tutor booked sessions",
        "tutor_group_sessions":  "Tutor group sessions",
        "tutor_earnings":        "Tutor earnings",
        "student_bookings":      "Student my bookings",
        "student_wallet":        "Student wallet",
    }
    for key, label in labels.items():
        u = vu.get(key, "")
        if u:
            print(f"  │  {label:<28}: {u}", flush=True)
    print("  └──────────────────────────────────────────────────────────┘", flush=True)

    if _SUMMARY["errors"]:
        print(flush=True)
        print(f"  ⚠ ERRORS ({len(_SUMMARY['errors'])}):", flush=True)
        for e in _SUMMARY["errors"]:
            print(f"    ✗ {e}", flush=True)

    print(flush=True)
    print(f"  Full JSON report: {report_path}", flush=True)
    print("═" * 65, flush=True)

    if booking_id:
        print(f"BOOKING_ID={booking_id}", flush=True)

    return booking_id


if __name__ == "__main__":
    main()
