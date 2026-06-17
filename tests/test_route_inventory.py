from __future__ import annotations

import os
from urllib.parse import urlparse

import pytest
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError


BASE_URL = os.getenv("BASE_URL", "https://dev.mehadedu.com/en").rstrip("/")
TEACHER_PHONE = os.getenv("TEACHER_PHONE", os.getenv("TEST_PHONE", "98976564"))
TEACHER_OTP = os.getenv("TEACHER_OTP", os.getenv("TEST_OTP", "123456"))
TEACHER_COUNTRY = os.getenv("TEACHER_COUNTRY", os.getenv("TEST_COUNTRY", "+880"))


PUBLIC_ROUTES = [
    ("/", ("Saudi Arabia", "Find")),
    ("/find-tutors", ("Tutor", "Subject")),
    ("/group-sessions", ("Group", "Session")),
    ("/become-tutor", ("Tutor", "Apply")),
    ("/how-mehad-works", ("How", "Works")),
    ("/about-us", ("Mehad",)),
    ("/subjects", ("Subject",)),
    ("/pricing", ("Pricing",)),
    ("/contact-us", ("Contact",)),
    ("/faqs", ("FAQ", "Question")),
    ("/blog", ("Blog",)),
    ("/careers", ("Career",)),
    ("/privacy-policy", ("Privacy",)),
    ("/terms-conditions", ("Terms",)),
    ("/refund-policy", ("Refund",)),
    ("/cookie-policy", ("Cookie",)),
    ("/tutor-login", ("Teacher Login", "WhatsApp")),
    ("/super-admin-login", ("Super Admin", "Login")),
]

TUTOR_DASHBOARD_ROUTES = [
    ("/dashboard/availability", "Availability Calendar"),
    ("/dashboard/booked-sessions", "All Sessions"),
    ("/dashboard/group-sessions", "Group Sessions"),
    ("/dashboard/messages", "Messages"),
    ("/dashboard/earnings", "Earnings & Payouts"),
    ("/dashboard/reviews", "Reviews"),
    ("/dashboard/notifications", "Notifications"),
    ("/dashboard/instructor-profile", "Instructor Profile"),
    ("/dashboard/help-center", "Help Center"),
    ("/dashboard/profile", "My Profile"),
    ("/dashboard/settings", "Toggle Sidebar"),
]

TUTOR_SIDEBAR_ROUTES = {
    "/dashboard/availability",
    "/dashboard/booked-sessions",
    "/dashboard/group-sessions",
    "/dashboard/messages",
    "/dashboard/earnings",
    "/dashboard/reviews",
    "/dashboard/notifications",
    "/dashboard/instructor-profile",
    "/dashboard/help-center",
}

REMOVED_DASHBOARD_ROUTES = {
    "/dashboard/packages",
    "/dashboard/account-settings",
    "/dashboard/payout",
    "/dashboard/promo-codes",
    "/dashboard/sessions",
    "/dashboard/subject-categories",
    "/dashboard/subjects",
    "/dashboard/translations",
}


def _country_name(code: str) -> str:
    if code.startswith("+880"):
        return "Bangladesh"
    if code.startswith("+966"):
        return "Saudi Arabia"
    if code.startswith("+971"):
        return "United Arab Emirates"
    return code


def _page_text(page: Page) -> str:
    try:
        return page.locator("body").inner_text(timeout=5000)
    except Exception:
        return ""


def _app_path(href: str) -> str:
    path = urlparse(href).path
    if path == "/en" or path == "/ar":
        return "/"
    if path.startswith("/en/") or path.startswith("/ar/"):
        return path[3:]
    return path


def _assert_healthy_page(page: Page, path: str, expected_terms: tuple[str, ...] = ()) -> None:
    page.goto(BASE_URL + path, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(1200)
    body = _page_text(page)
    for _ in range(6):
        if len(body.strip()) > 20:
            break
        page.wait_for_timeout(500)
        body = _page_text(page)
    title = page.title()
    lowered = body.lower()

    assert "404" not in title, f"{path} title contains 404: {title!r}"
    assert "500" not in title, f"{path} title contains 500: {title!r}"
    assert "page not found" not in lowered, f"{path} shows Page Not Found"
    assert "internal server error" not in lowered, f"{path} shows server error"
    assert "application error" not in lowered, f"{path} shows application error"
    assert len(body.strip()) > 20, f"{path} rendered empty body"

    if expected_terms:
        missing = [term for term in expected_terms if term.lower() not in lowered]
        assert not missing, f"{path} missing expected text: {missing}; sample={body[:300]!r}"


def _login_tutor(page: Page) -> None:
    page.goto(BASE_URL.rsplit("/en", 1)[0] + "/en/tutor-login", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(2000)

    page.locator('button[aria-label="Country code"], button:has-text("Country code")').first.click(timeout=10000)
    search = page.locator('[role="listbox"] input[placeholder*="Search"], input[placeholder="Search..."]').first
    search.fill(_country_name(TEACHER_COUNTRY))
    page.wait_for_timeout(500)
    page.locator(f'[role="option"]:has-text("{_country_name(TEACHER_COUNTRY)}")').first.click()

    page.locator('input[type="tel"], input[placeholder*="123"]').first.fill(TEACHER_PHONE)
    page.locator('button:has-text("Send Code")').first.click()
    page.wait_for_timeout(2000)

    otp = page.locator('input[placeholder="000000"]').first
    otp.wait_for(state="visible", timeout=15000)
    for _ in range(40):
        if not otp.is_disabled():
            break
        page.wait_for_timeout(500)
    if otp.is_disabled():
        raise PlaywrightTimeoutError("Tutor OTP input stayed disabled")

    otp.fill(TEACHER_OTP)
    page.locator('button:has-text("Continue")').first.click()
    page.wait_for_timeout(5000)

    body = _page_text(page)
    if "Tutor" not in body and "Availability Calendar" not in body:
        raise AssertionError(f"Tutor login did not reach tutor dashboard. url={page.url} body={body[:300]!r}")


@pytest.fixture(scope="session")
def tutor_storage(browser, tmp_path_factory):
    if not TEACHER_PHONE or not TEACHER_OTP:
        pytest.skip("Tutor credentials not configured")

    storage_path = tmp_path_factory.mktemp("route_inventory") / "tutor.json"
    ctx = browser.new_context(viewport={"width": 1280, "height": 720}, ignore_https_errors=True, locale="en-US")
    page = ctx.new_page()
    try:
        _login_tutor(page)
        ctx.storage_state(path=str(storage_path))
    finally:
        ctx.close()
    return str(storage_path)


@pytest.fixture()
def tutor_page(browser, tutor_storage):
    ctx = browser.new_context(
        viewport={"width": 1280, "height": 720},
        ignore_https_errors=True,
        locale="en-US",
        storage_state=tutor_storage,
    )
    page = ctx.new_page()
    page.set_default_timeout(12000)
    yield page
    ctx.close()


@pytest.mark.parametrize(("path", "expected_terms"), PUBLIC_ROUTES)
def test_qa23_public_route_loads_without_404_or_empty_content(page: Page, path: str, expected_terms: tuple[str, ...]):
    """Public nav/footer route exists and renders expected real content."""
    _assert_healthy_page(page, path, expected_terms)


def test_qa23_homepage_exposes_all_public_inventory_links(page: Page):
    """Homepage nav/footer must link all public pages automation covers."""
    page.goto(BASE_URL, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(2000)
    hrefs = page.locator("a").evaluate_all("els => els.map(a => a.href).filter(Boolean)")
    paths = {_app_path(href) for href in hrefs if urlparse(href).netloc == urlparse(BASE_URL).netloc}

    expected_paths = {path for path, _ in PUBLIC_ROUTES if path not in {"/", "/tutor-login", "/super-admin-login"}}
    missing = sorted(expected_paths - paths)
    assert not missing, f"Homepage missing public inventory links: {missing}; found={sorted(paths)}"


@pytest.mark.parametrize(("path", "section_text"), TUTOR_DASHBOARD_ROUTES)
def test_qa23_tutor_dashboard_route_loads_expected_section(tutor_page: Page, path: str, section_text: str):
    """Tutor dashboard route exists and displays expected section heading/content."""
    _assert_healthy_page(tutor_page, path, (section_text,))


def test_qa23_tutor_sidebar_has_all_current_sections(tutor_page: Page):
    """Tutor sidebar must expose every current tutor section and no retired dashboard links."""
    tutor_page.goto(BASE_URL + "/dashboard", wait_until="domcontentloaded", timeout=30000)
    tutor_page.wait_for_timeout(2000)
    hrefs = tutor_page.locator("a").evaluate_all("els => els.map(a => a.href).filter(Boolean)")
    paths = {_app_path(href) for href in hrefs if urlparse(href).netloc == urlparse(BASE_URL).netloc}

    missing = sorted(TUTOR_SIDEBAR_ROUTES - paths)
    stale = sorted(paths & REMOVED_DASHBOARD_ROUTES)

    assert not missing, f"Tutor sidebar missing current sections: {missing}; found={sorted(paths)}"
    assert not stale, f"Tutor sidebar links retired/unavailable routes: {stale}"


@pytest.mark.parametrize("path", sorted(REMOVED_DASHBOARD_ROUTES))
def test_qa23_retired_dashboard_route_not_visible_in_tutor_navigation(tutor_page: Page, path: str):
    """Unavailable dashboard routes must not be advertised in active tutor navigation."""
    tutor_page.goto(BASE_URL + "/dashboard", wait_until="domcontentloaded", timeout=30000)
    tutor_page.wait_for_timeout(1500)
    hrefs = tutor_page.locator("a").evaluate_all("els => els.map(a => a.href).filter(Boolean)")
    paths = {_app_path(href) for href in hrefs if urlparse(href).netloc == urlparse(BASE_URL).netloc}
    assert path not in paths, f"Retired/unavailable route still visible in tutor nav: {path}"
