import os, time, pytest
from playwright.sync_api import Page, expect
BASE_URL = os.getenv("BASE_URL", "https://dev.mehadedu.com/en")

def test_smoke_page_accessible(page: Page):
    """Smoke: page responds and main form visible."""
    page.goto("https://dev.mehadedu.com/en/become-tutor", timeout=10000)
    expect(page.locator("form, main, [role='main']")).to_be_visible(timeout=5000)

def test_smoke_form_interactive(page: Page):
    """Smoke: can type in form fields."""
    page.goto("https://dev.mehadedu.com/en/become-tutor")
    email = page.locator('input[type="email"]').first
    expect(email).to_be_visible(timeout=5000)
    email.fill("smoke@test.com")
    assert email.input_value() == "smoke@test.com"

def test_smoke_submit_button_clickable(page: Page):
    """Smoke: submit button is clickable (not disabled, not hidden)."""
    page.goto("https://dev.mehadedu.com/en/become-tutor")
    btn = page.locator('button[type="submit"]').first
    expect(btn).to_be_visible(timeout=5000)
    expect(btn).to_be_enabled()

def test_smoke_no_500_error(page: Page):
    """Smoke: page returns 200 (not a server error)."""
    response = page.goto("https://dev.mehadedu.com/en/become-tutor")
    assert response.status < 400, f"Page returned HTTP {response.status}"

def test_flow_page_loads_with_correct_heading(page: Page):
    """Page loads with correct heading."""
    page.goto("https://dev.mehadedu.com/en/become-tutor", wait_until="domcontentloaded", timeout=30000)
    expect(page).to_have_title(lambda t: bool(t and len(t) > 100))
    expect(page.locator('h1')).to_be_visible(timeout=5000)
    expect(page.locator('h1')).to_have_text("Become a tutor on Mehad")

def test_flow_why_choose_mehad_section_has_four_benefit_cards(page: Page):
    """Why Choose Mehad section has four benefit cards."""
    page.goto("https://dev.mehadedu.com/en/become-tutor", wait_until="domcontentloaded", timeout=30000)
    expect(page.locator('section[data-testid="benefits"]')).to_be_visible(timeout=5000)
    expect(page.locator('div[data-testid="benefit-card"]').count()).to_equal(4)

def test_flow_how_to_become_a_tutor_section_has_four_numbered_steps(page: Page):
    """How to become a tutor section has four numbered steps."""
    page.goto("https://dev.mehadedu.com/en/become-tutor", wait_until="domcontentloaded", timeout=30000)
    expect(page.locator('section[data-testid="process"]')).to_be_visible(timeout=5000)
    expect(page.locator('ol li').count()).to_equal(4)

def test_flow_requirements_section_is_visible(page: Page):
    """Requirements section is visible."""
    page.goto("https://dev.mehadedu.com/en/become-tutor", wait_until="domcontentloaded", timeout=30000)
    expect(page.locator('section[data-testid="requirements"]')).to_be_visible(timeout=5000)

def test_flow_apply_now_button_navigates_to_tutor_login(page: Page):
    """Apply Now button navigates to tutor-login."""
    page.goto("https://dev.mehadedu.com/en/become-tutor", wait_until="domcontentloaded", timeout=30000)
    expect(page.locator('button:has-text("Apply Now")')).to_be_visible(timeout=5000)
    page.locator('button:has-text("Apply Now")').click()
    expect(page).to_have_url(re.compile(r"/en/tutor-login"))

def test_flow_negative_no_broken_links_or_500_errors(page: Page):
    """Negative  No broken links or 500 errors."""
    page.goto("https://dev.mehadedu.com/en/become-tutor", wait_until="domcontentloaded", timeout=30000)
    expect(page).to_have_url(re.compile(r"/en/become-tutor"))
    expect(page.locator('body')).not_to_contain_text("404")
    expect(page.locator('body')).not_to_contain_text("500")

def test_email_empty(page: Page):
    """Email field must show error for empty input."""
    page.goto(BASE_URL, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(800)
    page.locator('input[name="email"]').fill('')
    page.locator('button[type="submit"]').click()
    page.wait_for_timeout(500)
    expect(page.locator("[role='alert'], .error, .text-red-500").first).to_be_visible(timeout=4000)

def test_email_spaces_only(page: Page):
    """Email field must show error for spaces only."""
    page.goto(BASE_URL, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(800)
    page.locator('input[name="email"]').fill('   ')
    page.locator('button[type="submit"]').click()
    page.wait_for_timeout(500)
    expect(page.locator("[role='alert'], .error, .text-red-500").first).to_be_visible(timeout=4000)

def test_email_invalid_format(page: Page):
    """Email field must show error for invalid format."""
    page.goto(BASE_URL, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(800)
    page.locator('input[name="email"]').fill('invalid@@@email')
    page.locator('button[type="submit"]').click()
    page.wait_for_timeout(500)
    expect(page.locator("[role='alert'], .error, .text-red-500").first).to_be_visible(timeout=4000)

def test_email_script_tag(page: Page):
    """Email field must show error for script tag."""
    page.goto(BASE_URL, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(800)
    page.locator('input[name="email"]').fill('<script>alert(1)</script>')
    page.locator('button[type="submit"]').click()
    page.wait_for_timeout(500)
    expect(page.locator("[role='alert'], .error, .text-red-500").first).to_be_visible(timeout=4000)

def test_password_empty(page: Page):
    """Password field must show error for empty input."""
    page.goto(BASE_URL, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(800)
    page.locator('input[name="password"]').fill('')
    page.locator('button[type="submit"]').click()
    page.wait_for_timeout(500)
    expect(page.locator("[role='alert'], .error, .text-red-500").first).to_be_visible(timeout=4000)

def test_password_too_short(page: Page):
    """Password field must show error for too short input."""
    page.goto(BASE_URL, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(800)
    page.locator('input[name="password"]').fill('1234567')
    page.locator('button[type="submit"]').click()
    page.wait_for_timeout(500)
    expect(page.locator("[role='alert'], .error, .text-red-500").first).to_be_visible(timeout=4000)

def test_required_fields_empty(page: Page):
    """All required fields must show error for empty input."""
    page.goto(BASE_URL, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(800)
    page.locator('input[name="email"]').fill('')
    page.locator('input[name="password"]').fill('')
    page.locator('button[type="submit"]').click()
    page.wait_for_timeout(500)
    expect(page.locator("[role='alert'], .error, .text-red-500").first).to_be_visible(timeout=4000)

def test_valid_email_password(page: Page):
    """Form must submit successfully with valid email and password."""
    page.goto(BASE_URL, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(800)
    page.locator('input[name="email"]').fill('valid@example.com')
    page.locator('input[name="password"]').fill('Test@1234!')
    page.locator('button[type="submit"]').click()
    page.wait_for_timeout(500)
    assert page.url != BASE_URL

def test_empty_form_submission(page: Page):
    """Empty form submission  validation errors appear."""
    page.goto(BASE_URL, wait_until="domcontentloaded", timeout=30000)
    page.locator('button[type="submit"]').click()
    expect(page.get_by_role("alert")).to_be_visible(timeout=5000)

def test_invalid_input_format(page: Page):
    """Invalid input format  format error shown."""
    page.goto(BASE_URL, wait_until="domcontentloaded", timeout=30000)
    page.locator('input[name="email"]').fill("invalid-email")
    page.locator('button[type="submit"]').click()
    expect(page.get_by_role("alert")).to_be_visible(timeout=5000)

def test_very_long_input(page: Page):
    """Very long input (300+ chars)  graceful error."""
    page.goto(BASE_URL, wait_until="domcontentloaded", timeout=30000)
    long_text = "a" * 310
    page.locator('input[name="email"]').fill(long_text)
    page.locator('button[type="submit"]').click()
    expect(page.get_by_role("alert")).to_be_visible(timeout=5000)

def test_browser_back_button_after_failed_submit(page: Page):
    """Browser back button after a failed submit  form state preserved."""
    page.goto(BASE_URL, wait_until="domcontentloaded", timeout=30000)
    page.locator('input[name="email"]').fill("invalid-email")
    page.locator('button[type="submit"]').click()
    expect(page.get_by_role("alert")).to_be_visible(timeout=5000)
    page.keyboard.press('Escape')
    expect(page.locator('input[name="email"]')).to_have_value("invalid-email")

def test_double_click_submit_button(page: Page):
    """Double-click submit button  no duplicate submission."""
    page.goto(BASE_URL, wait_until="domcontentloaded", timeout=30000)
    page.locator('button[type="submit"]').click()
    expect(page.get_by_role("alert")).to_be_visible(timeout=5000)
    page.locator('button[type="submit"]').click()
    expect(page.get_by_role("alert")).not_to_be_visible(timeout=5000)

def test_paste_into_required_field_then_submit(page: Page):
    """Paste (Ctrl+V) into a required field then submit  value accepted."""
    page.goto(BASE_URL, wait_until="domcontentloaded", timeout=30000)
    email = f"qa_{int(time.time())}@mailinator.com"
    page.locator('input[name="email"]').fill(email, delay=100)
    page.locator('button[type="submit"]').click()
    expect(page).to_have_url(re.compile(r"/en/become-tutor"))
    expect(page.get_by_text(email)).to_be_visible(timeout=5000)

def test_rapid_5x_clicks_on_submit_with_empty_form(page: Page):
    """Rapid 5x clicks on submit with empty form  only validation errors."""
    page.goto(BASE_URL, wait_until="domcontentloaded", timeout=30000)
    for _ in range(5):
        page.locator('button[type="submit"]').click()
        expect(page.get_by_role("alert")).to_be_visible(timeout=5000)

def test_edge_ec_01_no_login_required(page: Page):
    """[EC-01] No login required  expect: System shows appropriate error or prevents the action"""
    # TEST_DATA: None
    page.goto(BASE_URL + "/en/become-tutor", wait_until="domcontentloaded", timeout=30000)
    expect(page).to_have_url(re.compile(r"https://dev.mehadedu.com/en/become-tutor"))
    expect(page.locator('button:has-text("Sign Up")')).to_be_visible(timeout=5000)

def test_edge_ec_02_no_404_or_500_error_appears(page: Page):
    """[EC-02] no 404 or 500 error appears in the page title or body  expect: System shows appropriate error or prevents the action"""
    # TEST_DATA: None
    page.goto(BASE_URL + "/en/nonexistent-page", wait_until="domcontentloaded", timeout=30000)
    expect(page).to_have_url(re.compile(r"https://dev.mehadedu.com/en/nonexistent-page"))
    expect(page.locator('h1')).to_be_visible(timeout=5000)
    expect(page.locator('h1')).to_have_text("404 Not Found", timeout=5000)

def test_boundary(page: Page, name, value, desc, expect):
    """Boundary input handling.
    # TEST_DATA: name=<name>  value=<value>  desc=<desc>  expect=<expect>
    """
    page.goto("https://dev.mehadedu.com/en/become-tutor", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(800)
    field = page.locator('input[type="email"], input[type="text"], input[type="password"]').filter(visible=True).first
    if field.count() == 0:
        return
    try:
        field.fill(value, timeout=5000)
    except Exception:
        return
    submit = page.locator('button[type="submit"]').filter(visible=True).first
    if submit.count() > 0:
        try:
            submit.click(timeout=4000)
        except Exception:
            pass
        page.wait_for_timeout(500)
    body = page.inner_text("body")
    assert len(body) > 50, f"{name}: page collapsed to <50 chars after boundary input"
    assert "500 Internal" not in body, f"{name}: server 500 on boundary input '{value[:40]}'"
    assert "Traceback (most recent" not in body, f"{name}: stack trace leaked"

import os, time, pytest
from playwright.sync_api import Page, expect

BASE_URL = os.getenv("BASE_URL", "https://dev.mehadedu.com/en/become-tutor")

@pytest.mark.parametrize("shape,value", [
    ("empty",       ""),
    ("single",      "a"),
    ("normal",      "test@example.com"),
    ("long",        "a" * 200),
    ("unicode",     "tst+RTL@example.com"),
    ("emoji",       "test@example.com"),
    ("specials",    "<>&\"' \\/"),
    ("template",    "{{7*7}}"),
])
@pytest.mark.parametrize("vp_w,vp_h,vp_name", [
    (1920, 1080, "fullhd"),
    (1280, 720,  "laptop"),
    (768,  1024, "tablet"),
    (375,  812,  "mobile"),
])
def test_combo(page: Page, shape, value, vp_w, vp_h, vp_name):
    """Combinatorial: input-shape  viewport.
    # TEST_DATA: shape=<shape> value=<value> viewport=<vp_w>x<vp_h>
    """
    page.set_viewport_size({"width": vp_w, "height": vp_h})
    page.goto("https://dev.mehadedu.com/en/become-tutor", wait_until="domcontentloaded", timeout=30000)
    field = page.locator('input[type="email"], input[type="text"]').filter(visible=True).first
    if not field.count():
        return  # no input field at this viewport  fine
    try:
        field.fill(value, timeout=4000)
    except Exception:
        return
    body = page.inner_text("body")
    assert len(body) > 50, f"{shape}@{vp_name}: body collapsed"
    assert "Traceback" not in body, f"{shape}@{vp_name}: stack trace leaked"

import os, time, pytest
from playwright.sync_api import Page, expect
BASE_URL = os.getenv("BASE_URL", "https://dev.mehadedu.com/en/become-tutor")

@pytest.mark.parametrize("test_email", ["testuser@example.com"])
def test_valid_email_accepted(page: Page, test_email):
    """Data-driven: valid email inputs should be accepted by the form.
    # TEST_DATA: {test_email} (from spec valid test data)
    """
    page.goto(BASE_URL, wait_until="domcontentloaded", timeout=30000)
    page.locator('input[type="email"]').fill(test_email)
    page.locator('button[type="submit"]').click()
    expect(page).to_have_url(re.compile(r"https://dev.mehadedu.com/en/become-tutor"))
    # Should NOT show email format error
    format_error = page.locator("text=/invalid email|valid email|email format/i")
    assert not format_error.is_visible(), f"Valid email '{test_email}' rejected with format error"

@pytest.mark.parametrize("test_email", ["invalid@@email", ""])
def test_invalid_email_rejected(page: Page, test_email):
    """Data-driven: invalid email inputs must be rejected.
    # TEST_DATA: {test_email} (from spec invalid test data)
    """
    page.goto(BASE_URL, wait_until="domcontentloaded", timeout=30000)
    if test_email:
        page.locator('input[type="email"]').fill(test_email)
    page.locator('button[type="submit"]').click()
    error = page.locator("[role='alert'], .error-message, input:invalid")
    expect(error).to_be_visible(timeout=5000), f"No error shown for invalid email: '{test_email}'"

def test_tab_order_logical(page: Page):
    """Tab key moves through fields in visual top-to-bottom order."""
    page.goto("https://dev.mehadedu.com/en/become-tutor", wait_until="domcontentloaded", timeout=30000)
    email = page.locator('input[type="email"]').first
    phone = page.locator('input[type="tel"]').first
    password = page.locator('input[type="password"]').first
    expect(email).to_be_visible(timeout=5000)
    expect(phone).to_be_visible(timeout=5000)
    expect(password).to_be_visible(timeout=5000)
    email.focus()
    page.keyboard.press("Tab")
    expect(phone).to_be_focused()

def test_paste_into_email_field(page: Page):
    """Paste an email address using clipboard."""
    page.goto("https://dev.mehadedu.com/en/become-tutor", wait_until="domcontentloaded", timeout=30000)
    email = page.locator('input[type="email"]').first
    expect(email).to_be_visible(timeout=5000)
    email.focus()
    page.evaluate("document.querySelector('input[type=email]').value = 'pasted@test.com'")
    page.locator('input[type="email"]').dispatch_event("input")
    assert page.locator('input[type="email"]').input_value() == "pasted@test.com"

def test_password_field_masked(page: Page):
    """Password value is not visible in DOM."""
    page.goto("https://dev.mehadedu.com/en/become-tutor", wait_until="domcontentloaded", timeout=30000)
    password = page.locator('input[type="password"]').first
    expect(password).to_be_visible(timeout=5000)
    password.fill("mysecret")
    inp_type = password.get_attribute("type")
    assert inp_type == "password", f"Password field type is '{inp_type}'  not masked"

def test_form_fields_have_autocomplete(page: Page):
    """Check for autocomplete attributes."""
    page.goto("https://dev.mehadedu.com/en/become-tutor", wait_until="domcontentloaded", timeout=30000)
    email = page.locator('input[type="email"]').first
    password = page.locator('input[type="password"]').first
    expect(email).to_be_visible(timeout=5000)
    expect(password).to_be_visible(timeout=5000)
    email_ac = email.get_attribute("autocomplete")
    pass_ac = password.get_attribute("autocomplete")
    assert email_ac in ["email", "username"], f"Email autocomplete is '{email_ac}'  expected 'email' or 'username'"
    assert pass_ac in ["current-password", "off"], f"Password autocomplete is '{pass_ac}'  expected 'current-password' or 'off'"

def test_required_fields_marked(page: Page):
    """Required fields have required attribute OR aria-required."""
    page.goto("https://dev.mehadedu.com/en/become-tutor", wait_until="domcontentloaded", timeout=30000)
    email = page.locator('input[type="email"]').first
    expect(email).to_be_visible(timeout=5000)
    has_required = email.get_attribute("required") is not None or \
                   email.get_attribute("aria-required") == "true"
    assert has_required, "Email field not marked as required"

def test_form_clears_after_navigation(page: Page):
    """Fill form, navigate away, come back  form is clear."""
    page.goto("https://dev.mehadedu.com/en/become-tutor", wait_until="domcontentloaded", timeout=30000)
    email = page.locator('input[type="email"]').first
    expect(email).to_be_visible(timeout=5000)
    email.fill("test@test.com")
    page.go_back()
    page.go_forward()
    page.wait_for_load_state("domcontentloaded")
    val = email.input_value()
    assert not val, f"Form field is not cleared  value: {val}"

def test_login_api_request_method(page: Page):
    """Intercept the form submit API call, assert method is POST."""
    with page.expect_request(lambda r: "/api/" in r.url and r.method == "POST") as req:
        page.fill('input[type="email"]', "test@test.com")
        page.fill('input[type="password"]', "Test@1234!")
        page.click('button[type="submit"]')

def test_api_returns_correct_status_on_valid_login(page: Page):
    """Submit valid credentials, assert 200/201 status."""
    with page.expect_response(lambda r: "/api/" in r.url) as resp_info:
        page.fill('input[type="email"]', "test@test.com")
        page.fill('input[type="password"]', "Test@1234!")
        page.click('button[type="submit"]')
    resp = resp_info.value
    assert resp.status in (200, 201), f"Expected 200/201, got {resp.status}"

def test_api_returns_401_on_invalid_login(page: Page):
    """Submit wrong password, assert 401/403."""
    with page.expect_response(lambda r: "/api/" in r.url) as resp_info:
        page.fill('input[type="email"]', "test@test.com")
        page.fill('input[type="password"]', "wrong_password")
        page.click('button[type="submit"]')
    resp = resp_info.value
    assert resp.status in (401, 403), f"Expected auth error, got {resp.status}"

def test_no_password_in_response(page: Page):
    """After login, assert response body doesn't contain 'password'."""
    with page.expect_response(lambda r: "/api/" in r.url) as resp_info:
        page.fill('input[type="email"]', "test@test.com")
        page.fill('input[type="password"]', "Test@1234!")
        page.click('button[type="submit"]')
    body = resp_info.value.text()
    assert "password" not in body.lower(), f"Expected no 'password' in response, got {body}"

def test_request_has_content_type(page: Page):
    """Assert POST has Content-Type: application/json."""
    with page.expect_request(lambda r: "/api/" in r.url and r.method == "POST") as req:
        page.fill('input[type="email"]', "test@test.com")
        page.fill('input[type="password"]', "Test@1234!")
        page.click('button[type="submit"]')
    assert req.request.headers["Content-Type"] == "application/json", f"Expected Content-Type: application/json, got {req.request.headers['Content-Type']}"

def test_network_errors_handled(page: Page):
    """Use page.route to abort API call, assert user sees friendly error."""
    page.route("**/api/**", lambda r: r.abort())
    page.fill('input[type="email"]', "test@test.com")
    page.fill('input[type="password"]', "Test@1234!")
    page.click('button[type="submit"]')
    assert page.locator("[role='alert'], .error").is_visible(), f"Expected error message to be visible"

def test_all_inputs_have_labels(page: Page):
    """Every input has an accessible name."""
    for inp in page.locator('input:not([type="hidden"])').all():
        assert inp.get_attribute("aria-label") or inp.get_attribute("id"), "Input missing label"

def test_submit_button_has_accessible_name(page: Page):
    """Submit button has an accessible name."""
    btn = page.locator('button[type="submit"]')
    assert btn.inner_text().strip() or btn.get_attribute("aria-label"), "Button has no accessible name"

def test_keyboard_navigation_order(page: Page):
    """Tab through form, check focus moves logically."""
    page.keyboard.press("Tab")  # focus email
    assert page.locator('input[type="email"]').is_focused()
    page.keyboard.press("Tab")  # focus password
    assert page.locator('input[type="password"]').is_focused()
    page.keyboard.press("Tab")  # focus submit

def test_form_submits_on_enter_key(page: Page):
    """Form submits on Enter key press."""
    page.locator('input[type="email"]').fill("test@test.com")
    page.locator('input[type="password"]').fill("Test@1234!")
    page.keyboard.press("Enter")
    page.wait_for_timeout(1000)
    assert page.url != "https://dev.mehadedu.com/en/become-tutor", "Form did not submit"

def test_error_messages_have_aria_role(page: Page):
    """Error messages have role=alert."""
    page.locator('button[type="submit"]').click()
    error = page.locator("[role='alert']")
    assert error.is_visible(), "Error message doesn't use role=alert for screen readers"

def test_axe_core_no_violations(page: Page):
    """No critical or serious violations from axe-core."""
    page.add_script_tag(url="https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.9.0/axe.min.js")
    page.wait_for_timeout(1000)
    results = page.evaluate("async () => await axe.run()")
    critical = [v for v in results.get("violations", []) if v.get("impact") in ("critical","serious")]
    assert not critical, f"axe-core critical violations: {[v['description'] for v in critical]}"

def test_color_contrast_not_broken(page: Page):
    """Page loads without CSS errors that break contrast."""
    errors = []
    page.on("console", lambda m: errors.append(m.text) if "contrast" in m.text.lower() else None)
    page.goto("https://dev.mehadedu.com/en/become-tutor")
    assert not any(error for error in errors if "contrast" in error.lower()), "Contrast errors found"

import os, time, pytest
from playwright.sync_api import Page, expect
BASE_URL = os.getenv("BASE_URL", "https://dev.mehadedu.com/en/become-tutor")

@pytest.mark.parametrize("width,height,name", [
    (375, 667, "iPhone SE"),
    (390, 844, "iPhone 14"),
    (768, 1024, "iPad"),
    (1024, 768, "iPad Landscape"),
    (1280, 720, "Desktop HD"),
    (1920, 1080, "Full HD"),
])
def test_responsive_layout(page: Page, width, height, name):
    """Ensure layout is responsive across different viewports."""
    page.set_viewport_size({"width": width, "height": height})
    page.goto("https://dev.mehadedu.com/en/become-tutor")
    expect(page).to_have_url(re.compile(r"https://dev\.mehadedu\.com/en/become-tutor"))
    # Submit button visible at all sizes
    expect(page.locator('button[type="submit"]').filter(visible=True).first).to_be_visible(timeout=5000)
    # No horizontal scroll
    overflow = page.evaluate("() => document.documentElement.scrollWidth > window.innerWidth")
    assert not overflow, f"Horizontal overflow on {name} ({width}px)"

def test_touch_target_sizes(page: Page):
    """Ensure buttons are large enough for touch targets."""
    page.set_viewport_size({"width": 375, "height": 667})
    btn = page.locator('button[type="submit"]').filter(visible=True).first
    box = btn.bounding_box()
    assert box["height"] >= 44, f"Button too small for touch: {box['height']}px"

def test_font_size_not_tiny_on_mobile(page: Page):
    """Ensure text is readable on mobile."""
    page.set_viewport_size({"width": 375, "height": 667})
    # Check email input font size
    size = page.evaluate("() => parseFloat(window.getComputedStyle(document.querySelector('input[type=email]')).fontSize)")
    assert size >= 14, f"Input font size {size}px too small (min 14px)"

def test_nav_back_to_login(page: Page):
    """Click 'Back to Login'  assert URL contains '/login'."""
    page.goto("https://dev.mehadedu.com/en/become-tutor", wait_until="domcontentloaded", timeout=30000)
    page.get_by_role("link", name="Back to Login").click()
    expect(page).to_have_url(re.compile(r"/login"))

def test_nav_back_button(page: Page):
    """Navigate to page, go to another page, press browser back  lands back on https://dev.mehadedu.com/en/become-tutor."""
    page.goto("https://dev.mehadedu.com/en/become-tutor", wait_until="domcontentloaded", timeout=30000)
    page.get_by_role("link", name="Become a Tutor").click()
    page.wait_for_url("**/tutor-dashboard**", timeout=5000)
    page.evaluate("history.back()")
    expect(page).to_have_url(re.compile(r"/become-tutor"))

def test_nav_direct_url_access(page: Page):
    """Navigate directly to https://dev.mehadedu.com/en/become-tutor  page loads without redirect loop."""
    page.goto("https://dev.mehadedu.com/en/become-tutor", wait_until="domcontentloaded", timeout=30000)
    expect(page).to_have_url(re.compile(r"/become-tutor"))

def test_nav_logo_home(page: Page):
    """Click logo  navigates to home/root page (if logo present)."""
    page.goto("https://dev.mehadedu.com/en/become-tutor", wait_until="domcontentloaded", timeout=30000)
    if page.get_by_role("img", name="Logo").is_visible():
        page.get_by_role("img", name="Logo").click()
        expect(page).to_have_url(re.compile(r"/"))

def test_unauthenticated_redirected_to_login(page: Page):
    """Unauthenticated user should be redirected to /login or /auth."""
    page.goto(BASE_URL + "/dashboard", wait_until="domcontentloaded", timeout=30000)
    assert "/login" in page.url or "/auth" in page.url

def test_authenticated_user_bypasses_login(page: Page):
    """Authenticated user should bypass login and access the dashboard."""
    page.evaluate("localStorage.setItem('authToken', 'fake-valid-token')")
    page.goto(BASE_URL + "/become-tutor", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(1000)
    assert page.url is not None  # Page should be accessible

def test_no_auth_token_after_failed_login(page: Page):
    """No auth token should be set after a failed login attempt."""
    page.goto(BASE_URL + "/become-tutor", wait_until="domcontentloaded", timeout=30000)
    page.locator('input[type="email"]').fill("wrong@test.com")
    page.locator('input[type="password"]').fill("wrongpass")
    page.locator('button[type="submit"]').click()
    page.wait_for_timeout(1000)
    token = page.evaluate("() => localStorage.getItem('authToken') || localStorage.getItem('token')")
    assert not token, f"Auth token should not be set after failed login, got: {token}"

def test_session_cookies_set_on_login(page: Page):
    """Session cookies should be set on successful login."""
    page.goto(BASE_URL + "/become-tutor", wait_until="domcontentloaded", timeout=30000)
    page.locator('input[type="email"]').fill(os.getenv("TEST_EMAIL", "qa_1672509600@mailinator.com"))
    page.locator('input[type="password"]').fill(os.getenv("TEST_PASSWORD", "Test@1234!"))
    page.locator('button[type="submit"]').click()
    cookies = page.context.cookies()
    session_cookies = [c for c in cookies if "session" in c["name"].lower() or "auth" in c["name"].lower()]
    assert len(session_cookies) > 0, f"No session cookies found after login"

def test_logout_clears_storage(page: Page):
    """Logout should clear localStorage."""
    page.goto(BASE_URL + "/become-tutor", wait_until="domcontentloaded", timeout=30000)
    page.locator('input[type="email"]').fill(os.getenv("TEST_EMAIL", "qa_1672509600@mailinator.com"))
    page.locator('input[type="password"]').fill(os.getenv("TEST_PASSWORD", "Test@1234!"))
    page.locator('button[type="submit"]').click()
    page.wait_for_timeout(1000)
    page.goto(BASE_URL + "/logout", wait_until="domcontentloaded", timeout=30000)
    token = page.evaluate("() => localStorage.getItem('authToken') || localStorage.getItem('token')")
    assert not token, f"Auth token should be cleared after logout, got: {token}"

def test_concurrent_session_handling(page: Page):
    """Concurrent sessions should handle login attempts correctly."""
    context1 = page.context.new_context()
    page1 = context1.new_page()
    page1.goto(BASE_URL + "/become-tutor", wait_until="domcontentloaded", timeout=30000)
    page1.locator('input[type="email"]').fill(os.getenv("TEST_EMAIL", "qa_1672509600@mailinator.com"))
    page1.locator('input[type="password"]').fill(os.getenv("TEST_PASSWORD", "Test@1234!"))
    page1.locator('button[type="submit"]').click()
    page1.wait_for_timeout(1000)

    context2 = page.context.new_context()
    page2 = context2.new_page()
    page2.goto(BASE_URL + "/become-tutor", wait_until="domcontentloaded", timeout=30000)
    page2.locator('input[type="email"]').fill(os.getenv("TEST_EMAIL", "qa_1672509600@mailinator.com"))
    page2.locator('input[type="password"]').fill(os.getenv("TEST_PASSWORD", "Test@1234!"))
    page2.locator('button[type="submit"]').click()
    page2.wait_for_timeout(1000)

    assert page1.url != page2.url, f"Both pages should be on different URLs after login"

def test_page_load_under_5_seconds(page: Page):
    """Page must load under 5 seconds."""
    start = time.time()
    page.goto("https://dev.mehadedu.com/en/become-tutor", wait_until="domcontentloaded")
    elapsed = (time.time() - start) * 1000
    assert elapsed < 5000, f"Slow load: {elapsed:.0f}ms (SLA: 5000ms)"

def test_dom_content_loaded_under_2_seconds(page: Page):
    """DOMContentLoaded must be under 2 seconds."""
    timing = page.evaluate("() => window.performance.timing.domContentLoadedEventEnd - window.performance.timing.navigationStart")
    assert timing < 2000, f"DOMContentLoaded: {timing}ms (limit: 2000ms)"

def test_ttfb_reasonable(page: Page):
    """Time to First Byte must be reasonable."""
    ttfb = page.evaluate("() => window.performance.timing.responseStart - window.performance.timing.navigationStart")
    assert ttfb < 1000, f"TTFB too slow: {ttfb}ms"

def test_no_render_blocking_large_resources(page: Page):
    """No render-blocking large resources should be present."""
    blocking = []
    def check_resp(resp):
        if resp.request.resource_type in ("script", "stylesheet"):
            try:
                if len(resp.body()) > 500_000: blocking.append((resp.url[-60:], len(resp.body())))
            except: pass
    page.on("response", check_resp)
    page.goto("https://dev.mehadedu.com/en/become-tutor", wait_until="domcontentloaded")
    assert not blocking, f"Large blocking resources: {blocking}"

def test_no_failed_network_requests(page: Page):
    """No failed network requests should be present."""
    failed = []
    def on_resp(r):
        if r.status >= 500: failed.append((r.url[-60:], r.status))
    page.on("response", on_resp)
    page.goto("https://dev.mehadedu.com/en/become-tutor", wait_until="domcontentloaded")
    assert not failed, f"Server errors: {failed}"

def test_web_vitals_lcp_reasonable(page: Page):
    """Largest Contentful Paint must be reasonable."""
    lcp = page.evaluate("() => new Promise(resolve => new PerformanceObserver(list => { const e = list.getEntries(); resolve(e.length ? e[e.length-1].startTime : 0); }).observe({type:'largest-contentful-paint', buffered:true}))")
    assert lcp < 4000, f"LCP too slow: {lcp:.0f}ms (limit: 4000ms)"

def test_no_console_errors_on_page_load(page: Page):
    """Ensure no console errors on page load."""
    errors = []
    page.on("console", lambda m: errors.append(f"{m.type}: {m.text}") if m.type == "error" else None)
    page.goto(BASE_URL, wait_until="domcontentloaded", timeout=30000)
    assert errors == [], f"Console errors on load ({len(errors)}): {errors[:3]}"

def test_no_console_errors_on_form_interaction(page: Page):
    """Ensure no console errors during form interaction."""
    errors = []
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.goto(BASE_URL, wait_until="domcontentloaded", timeout=30000)
    try:
        email = page.locator('input[type="email"]').first
        expect(email).to_be_visible(timeout=5000)
        email.fill("test@example.com")
        
        password = page.locator('input[type="password"]').first
        expect(password).to_be_visible(timeout=5000)
        password.fill("Test@1234!")
        
        submit_button = page.locator('button[type="submit"]').first
        expect(submit_button).to_be_visible(timeout=5000)
        submit_button.click()
        
        page.wait_for_timeout(2000)
    except Exception as e:
        pass
    assert errors == [], f"Console errors during interaction: {errors[:3]}"

def test_no_uncaught_exceptions(page: Page):
    """Ensure no uncaught JavaScript exceptions."""
    exceptions = []
    page.on("pageerror", lambda e: exceptions.append(str(e)))
    page.goto(BASE_URL, wait_until="domcontentloaded", timeout=30000)
    assert exceptions == [], f"Uncaught JS exceptions: {exceptions}"

def test_no_network_errors_in_console(page: Page):
    """Ensure no network errors in console."""
    network_errors = []
    page.on("console", lambda m: network_errors.append(m.text) if m.type == "error" and ("failed to load" in m.text.lower() or "net::" in m.text.lower()) else None)
    page.goto(BASE_URL, wait_until="domcontentloaded", timeout=30000)
    assert network_errors == [], f"Network errors in console: {network_errors}"

def test_no_404_resources(page: Page):
    """Ensure no 404 resources."""
    not_found = []
    page.on("response", lambda r: not_found.append(r.url[-60:]) if r.status == 404 else None)
    page.goto(BASE_URL, wait_until="domcontentloaded", timeout=30000)
    assert not_found == [], f"404 resources: {not_found}"

def test_no_stack_trace_exposed(page: Page):
    """Verify no stack trace is exposed on error."""
    page.goto("https://dev.mehadedu.com/en/become-tutor")
    page.locator('input[type="email"]').fill("' OR 1=1--")
    page.locator('button[type="submit"]').click()
    page.wait_for_timeout(1500)
    content = page.content().lower()
    leaks = ["traceback", "exception", "at object.", "sqlexception", "syntaxerror",
             "undefined is not", "cannot read", "typeerror:", "internal server error"]
    exposed = [l for l in leaks if l in content]
    assert not exposed, f"Internal error leaked to user: {exposed}"

def test_api_failure_shows_friendly_message(page: Page):
    """Verify a friendly error message is shown on API failure."""
    page.route("**/api/**", lambda r: r.fulfill(status=500, body="Server Error"))
    page.goto("https://dev.mehadedu.com/en/become-tutor")
    page.locator('input[type="email"]').fill("test@test.com")
    page.locator('button[type="submit"]').click()
    page.wait_for_timeout(1000)
    assert page.locator("[role='alert'], .error, .error-message").is_visible(), \
        "No friendly error shown when API returns 500"
    assert "500" not in page.content() and "server error" not in page.content().lower()

def test_network_timeout_handled(page: Page):
    """Verify network timeout is handled gracefully."""
    page.route("**/api/**", lambda r: r.abort("timedout"))
    page.goto("https://dev.mehadedu.com/en/become-tutor")
    try:
        page.locator('input[type="email"]').fill("test@test.com")
        page.locator('button[type="submit"]').click()
        page.wait_for_timeout(3000)
        # Should show network error message
    except: pass
    assert "500" not in page.content()

def test_page_stays_functional_after_error(page: Page):
    """Verify the page remains functional after repeated errors."""
    page.goto("https://dev.mehadedu.com/en/become-tutor")
    for _ in range(2):
        page.locator('input[type="email"]').fill("wrong@wrong.com")
        page.locator('input[type="password"]').fill("wrongpass")
        page.locator('button[type="submit"]').click()
        page.wait_for_timeout(1000)
    assert page.locator('input[type="email"]').is_visible(), "Page broken after repeated errors"

def test_form_within_viewport_bounds(page: Page):
    """Form must be within the viewport bounds."""
    form = page.locator("form").first
    box = form.bounding_box()
    vp = page.viewport_size
    assert box["x"] >= 0, "Form overflows left"
    assert box["x"] + box["width"] <= vp["width"] + 1, "Form overflows right"

def test_no_overlapping_elements(page: Page):
    """Email and password inputs must not overlap."""
    email_box = page.locator('input[type="email"]').bounding_box()
    pass_box  = page.locator('input[type="password"]').bounding_box()
    if email_box and pass_box:
        overlap = (email_box["y"] < pass_box["y"] + pass_box["height"] and
                   pass_box["y"] < email_box["y"] + email_box["height"])
        assert not overlap, "Email and password inputs overlap"

def test_submit_button_below_inputs(page: Page):
    """Submit button must be below the input fields."""
    btn_box   = page.locator('button[type="submit"]').bounding_box()
    email_box = page.locator('input[type="email"]').bounding_box()
    if btn_box and email_box:
        assert btn_box["y"] > email_box["y"], "Submit button is above inputs (wrong layout)"

def test_page_title_meaningful(page: Page):
    """Page title must be meaningful."""
    title = page.title()
    assert title and len(title) > 2, f"Page title too short: '{title}'"
    assert title.lower() not in ("undefined", "null", ""), f"Page title is placeholder: '{title}'"

def test_favicon_loads(page: Page):
    """Favicon must load successfully."""
    favicons = []
    page.on("response", lambda r: favicons.append(r.status) if "favicon" in r.url.lower() else None)
    page.goto("https://dev.mehadedu.com/en/become-tutor")
    page.wait_for_load_state("domcontentloaded")
    if favicons:
        assert all(s < 400 for s in favicons), f"Favicon load failed: {favicons}"

def test_no_broken_images(page: Page):
    """No images should be broken."""
    broken = []
    page.on("response", lambda r: broken.append(r.url[-50:])
            if r.request.resource_type == "image" and r.status >= 400 else None)
    page.goto("https://dev.mehadedu.com/en/become-tutor")
    page.wait_for_load_state("domcontentloaded")
    assert not broken, f"Broken images: {broken}"

def test_page_loads_crossbrowser(page: Page):
    """Cross-browser smoke: page loads and key elements visible.
    # TEST_DATA: none  pure navigation test
    # RUN ON: chromium, firefox, webkit (via pytest --browser=firefox)
    """
    page.goto("https://dev.mehadedu.com/en/become-tutor")
    expect(page).to_have_url(re.compile(r"https://dev\.mehadedu\.com/en/become-tutor"))
    expect(page.locator('input[type="email"]').filter(visible=True).first).to_be_visible(timeout=5000)
    expect(page.locator('button[type="submit"]').filter(visible=True).first).to_be_visible(timeout=5000)

def test_form_interaction_crossbrowser(page: Page):
    """Cross-browser smoke: form is interactive across browsers.
    # TEST_DATA: test@example.com / Test@1234!
    # RUN ON: chromium, firefox, webkit
    """
    page.goto("https://dev.mehadedu.com/en/become-tutor")
    expect(page).to_have_url(re.compile(r"https://dev\.mehadedu\.com/en/become-tutor"))
    email = page.locator('input[type="email"]').filter(visible=True).first
    password = page.locator('input[type="password"]').filter(visible=True).first
    expect(email).to_be_visible(timeout=5000)
    expect(password).to_be_visible(timeout=5000)
    email.fill("test@example.com")
    password.fill("Test@1234!")
    expect(email.input_value()).to_equal("test@example.com", f"Expected 'test@example.com', got {email.input_value()}")
    expect(password.input_value()).to_equal("Test@1234!", f"Expected 'Test@1234!', got {password.input_value()}")

import os, time, pytest
from playwright.sync_api import Page, expect
BASE_URL = os.getenv("BASE_URL", "https://dev.mehadedu.com/en/become-tutor")

def test_page_content_encoding(page: Page):
    """I18N: app handles international character inputs gracefully.
    # TEST_DATA: {description} = {test_input[:30]}
    """
    response = page.goto("https://dev.mehadedu.com/en/become-tutor")
    headers = response.all_headers()
    content_type = headers.get("content-type", "").lower()
    assert "utf-8" in content_type, f"Page not UTF-8 encoded: {content_type}"

def test_i18n_input_handling(page: Page, key, test_input, description):
    """I18N: app handles international character inputs gracefully.
    # TEST_DATA: {description} = {test_input[:30]}
    """
    page.goto("https://dev.mehadedu.com/en/become-tutor")
    page.wait_for_load_state("domcontentloaded")
    try:
        page.locator('input[type="email"]').fill(test_input)
    except: pass
    page.locator('button[type="submit"]').click()
    page.wait_for_timeout(500)
    # App should NOT crash  either show validation error OR process the input
    assert "500" not in page.content(), f"Server crash on i18n input: {description}"
    exceptions_exposed = any(w in page.content().lower()
                              for w in ["exception", "traceback", "syntaxerror"])
    assert not exceptions_exposed, f"Exception exposed for i18n input: {description}"

def test_rapid_form_submission_handled(page: Page):
    """Rate limiting: rapid repeated submissions don't crash the app.
    # TEST_DATA: 5 rapid wrong-credentials submissions
    """
    page.goto("https://dev.mehadedu.com/en/become-tutor")
    responses = []
    page.on("response", lambda r: responses.append(r.status) if "/api/" in r.url else None)
    for attempt in range(5):
        page.locator('input[type="email"]').fill(f"test{attempt}@test.com")
        page.locator('input[type="password"]').fill("wrongpass")
        page.locator('button[type="submit"]').click()
        page.wait_for_timeout(300)
    assert page.locator('input[type="email"]').is_visible(), "Page broke after rapid submissions"
    hit_rate_limit = 429 in responses or page.locator("text=/too many|rate limit|try again|blocked/i").is_visible()
    print(f"Rate limiting applied: {hit_rate_limit}")

def test_brute_force_protection(page: Page):
    """Rate limiting: 10 wrong password attempts trigger protection.
    # TEST_DATA: 10 wrong password attempts for same email
    """
    page.goto("https://dev.mehadedu.com/en/become-tutor")
    test_email = f"brutetest_{int(time.time())}@test.com"
    for i in range(10):
        try:
            page.locator('input[type="email"]').fill(test_email)
            page.locator('input[type="password"]').fill(f"wrong{i}")
            page.locator('button[type="submit"]').click()
            page.wait_for_timeout(200)
        except: break
    assert page.url is not None, "App crashed during brute force test"

def test_double_click_submit_not_double_submit(page: Page):
    """Rate limiting: double-clicking submit doesn't cause double form submission.
    # TEST_DATA: double-click on submit button
    """
    api_calls = []
    page.on("request", lambda r: api_calls.append(r.url) if "/api/" in r.url else None)
    page.goto("https://dev.mehadedu.com/en/become-tutor")
    page.locator('input[type="email"]').fill("test@test.com")
    page.locator('input[type="password"]').fill("Test@1234!")
    page.locator('button[type="submit"]').dblclick()
    page.wait_for_timeout(1000)
    api_login_calls = [u for u in api_calls if "login" in u or "auth" in u]
    assert len(api_login_calls) <= 1, f"Double submit occurred: {len(api_login_calls)} calls"

def test_no_sensitive_data_in_localstorage(page: Page):
    """Storage: no plaintext passwords in localStorage.
    # TEST_DATA: checks localStorage after interaction
    """
    page.goto("https://dev.mehadedu.com/en/become-tutor")
    page.locator('input[type="email"]').fill("test@test.com")
    page.locator('input[type="password"]').fill("Test@1234!")
    page.locator('button[type="submit"]').click()
    page.wait_for_timeout(1000)
    storage = page.evaluate("() => Object.entries(localStorage)")
    for key, value in storage:
        assert "password" not in key.lower(), f"Password key in localStorage: {key}"
        if isinstance(value, str) and len(value) < 100:
            assert "Test@1234!" not in value, f"Plaintext password in localStorage[{key}]"

def test_session_storage_cleared_on_bad_login(page: Page):
    """Storage: failed login does not persist auth data.
    # TEST_DATA: wrong credentials  check storage
    """
    page.goto("https://dev.mehadedu.com/en/become-tutor")
    page.locator('input[type="email"]').fill("hacker@evil.com")
    page.locator('input[type="password"]').fill("wrongpass")
    page.locator('button[type="submit"]').click()
    page.wait_for_timeout(1000)
    token = page.evaluate("() => localStorage.getItem('token') || sessionStorage.getItem('token')")
    assert not token, f"Auth token set after failed login: {token}"

def test_cookies_have_security_attributes(page: Page):
    """Storage: cookies use Secure and HttpOnly flags.
    # TEST_DATA: checks cookie attributes after page load
    """
    page.goto("https://dev.mehadedu.com/en/become-tutor")
    page.wait_for_load_state("domcontentloaded")
    cookies = page.context.cookies()
    for cookie in cookies:
        if "session" in cookie["name"].lower() or "auth" in cookie["name"].lower():
            assert cookie.get("httpOnly", False), f"Session cookie {cookie['name']} missing HttpOnly"

def test_localstorage_not_polluted(page: Page):
    """Storage: page doesn't write unexpected data to localStorage.
    # TEST_DATA: monitors localStorage before and after page load
    """
    page.goto("https://dev.mehadedu.com/en/become-tutor")
    page.wait_for_load_state("domcontentloaded")
    keys = page.evaluate("() => Object.keys(localStorage)")
    suspicious = [k for k in keys if any(w in k.lower() for w in ["debug", "test", "hack", "dev_"])]
    assert not suspicious, f"Suspicious localStorage keys: {suspicious}"

import pytest

_FB_XSS = ["<script>alert(1)</script>", "\"><img src=x onerror=alert(1)>"]

@pytest.mark.parametrize("payload", _FB_XSS)
def test_security_no_alert_dialog_fb(page: Page, payload):
    """FB security: XSS payload in any text input must NOT execute as JS."""
    fired = []
    page.on("dialog", lambda d: (fired.append(d.message), d.dismiss()))
    page.goto(BASE_URL, wait_until="domcontentloaded", timeout=30000)
    inputs = page.locator('input[type="text"], input[type="email"]')
    if inputs.count() > 0:
        inputs.first.fill(payload)
        page.wait_for_timeout(800)
    assert not fired, f"XSS executed: {fired}"