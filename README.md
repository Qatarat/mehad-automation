# Mehad Autonomous QA Platform

<div align="center">

[![CI](https://github.com/Qatarat/mehad-automation/actions/workflows/ai-tests.yml/badge.svg)](https://github.com/Qatarat/mehad-automation/actions/workflows/ai-tests.yml)
[![Live Report](https://img.shields.io/badge/Live%20Report-qatarat.github.io-brightgreen)](https://qatarat.github.io/mehad-automation/)
![Python](https://img.shields.io/badge/Python-3.12%2B-blue?logo=python)
![Playwright](https://img.shields.io/badge/Playwright-1.44%2B-green?logo=playwright)
![Tests](https://img.shields.io/badge/Tests-2000%2B-orange)
![Specs](https://img.shields.io/badge/Specs-69%20pages-blueviolet)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

**Write a spec file describing your page → get 2000+ automated tests instantly.**

*69 pages · 22 QA agent types · Spec-driven URLs · No hard-coded targets · Production E2E verified*

[**View Live Report →**](https://qatarat.github.io/mehad-automation/)

</div>

---

## Table of Contents

1. [What Is This?](#what-is-this)
2. [Test Scenario Types](#test-scenario-types)
3. [How Spec-Driven URLs Work](#how-spec-driven-urls-work)
4. [Installation](#installation)
5. [Configuration](#configuration-env)
6. [Running Tests](#running-tests)
7. [Production E2E Verified Results](#production-e2e-verified-results)
8. [OTP Options for Production](#otp-options-for-production)
9. [CI / GitHub Actions](#ci--github-actions)
10. [Adding a New Page](#adding-a-new-page)
11. [Project Structure](#project-structure)
11. [Troubleshooting](#troubleshooting)

---

## What Is This?

Mehad Autonomous QA is a fully automated testing platform for the [Mehad](https://mehadedu.com) online tutoring marketplace. It:

- **Reads spec files** (plain-text `.md` files in `specs/`) that describe each page's URL, UI elements, flows, and test data
- **Generates and runs 2000+ tests** covering every page — login, booking, payments, profiles, security, accessibility, and more
- **Runs nightly in CI** via GitHub Actions, publishing results to [the live dashboard](https://qatarat.github.io/mehad-automation/)
- **Never hard-codes the target URL** — each spec file declares its own `**URL:**`, and tests read from there

---

## Test Scenario Types

Every spec drives tests across **all** of the following scenario categories. This ensures no coverage gap regardless of which page is being tested.

### 1. Happy Path
> The "everything works perfectly" flow. Valid data, expected steps, successful outcome.

| Example | What is verified |
|---|---|
| Student logs in with valid phone + OTP | Dashboard shows user name, modal closes |
| Student books a session | Confirmation page reached, booking in history |
| Tutor creates a group session | Session appears in group sessions list |

**Test class:** `TestScenarioHappyPath` · `TestQA01Functional`

---

### 2. Valid Data
> Tests that confirm the system accepts all legitimate inputs and variations.

| Field | Valid values tested |
|---|---|
| Phone number | `98976564` (BD), `501234567` (SA), `0501234567` |
| Country code | `+880` (BD), `+966` (SA), `+971` (UAE), `+1` (USA) |
| OTP | `123456` (staging fixed), 6-digit numeric strings |
| Session duration | `30 min`, `60 min`, `90 min` |
| Search query | `Math`, `Physics`, `English`, `Arabic` |

**Test class:** `TestScenarioValidData`

---

### 3. Invalid Data
> Tests that confirm the system rejects bad inputs with clear, user-friendly error messages.

| Field | Invalid values tested |
|---|---|
| Phone number | `abc123`, `@!#$%`, `123` (too short), `999999999999999` (too long) |
| OTP | `000000`, `abcdef`, `12345` (5 digits), `1234567` (7 digits), `      ` (spaces) |
| Country code search | `ZZZZZ`, `<script>`, `DROP TABLE`, emoji `😀` |
| Session booking date | Past dates, `32/13/2099`, `00/00/0000` |
| Promo code | `FAKEPROMO`, `<IMG SRC=x>`, `' OR 1=1--` |

**Test class:** `TestScenarioInvalidData` · `TestQA02EdgeCaseBoundary` · `TestQA03Security`

---

### 4. Empty / Null / Blank Input
> Tests that confirm the system handles missing data gracefully — no crashes, clear UI feedback.

| Scenario | Expected behaviour |
|---|---|
| Submit login with empty phone | "Send Code" button stays disabled |
| Submit OTP with empty field | "Continue" button stays disabled |
| Search tutors with empty query | Page loads with all tutors or placeholder message |
| Book session with no date selected | Calendar error or submit stays disabled |
| Profile update with blank name | Validation message, save blocked |
| Whitespace-only phone `"   "` | Treated as empty — button stays disabled |

**Test class:** `TestScenarioEmptyInput`

---

### 5. Boundary Value
> Tests at the exact limits — minimum, maximum, and just beyond.

| Field | Boundary values |
|---|---|
| Phone number | 7 digits (min valid), 8 digits, 12 digits (max), 13 digits (over) |
| OTP | 5 digits (under), 6 digits (exact), 7 digits (over) |
| Review rating | `1` (min), `5` (max), `0` (under), `6` (over) |
| Session length | `15 min` (under min), `30 min` (min valid), `180 min` (max) |
| Search query length | `1` char, `100` chars, `1000` chars |

**Test class:** `TestQA02EdgeCaseBoundary`

---

### 6. UAT (User Acceptance Testing)
> End-to-end journeys that mirror real users' goals. Passes only when the full user story succeeds.

| User story | Steps |
|---|---|
| **Student first login** | Open site → Log In → Select country → Enter phone → OTP → Dashboard |
| **Student books a session** | Login → Find tutor → Select date/time → Pay → View booking |
| **Student leaves a review** | Complete session → Rate tutor 1–5 stars → Write comment → Submit |
| **Tutor sets availability** | Login as tutor → Calendar → Add slots → Save → Verify visibility |
| **Admin adds a subject** | Login as admin → Subjects → Add "Calculus" → Verify in student search |
| **Language switch** | Homepage in EN → click AR → verify RTL layout and Arabic text |

**Test class:** `TestScenarioUAT`

---

### 7. Out of the Box / Creative Negative
> Unexpected behaviour users actually do. Catches logic gaps missed by scripted tests.

| Scenario | Why it matters |
|---|---|
| Rapid double-click on "Send Code" | Prevents duplicate OTP requests / API spam |
| Resize browser mid-session | Responsive layout doesn't break in-progress flows |
| Browser Back button after login | Session persists, modal doesn't re-appear |
| Direct URL to protected page (not logged in) | Redirect to login, not blank/500 page |
| Paste a phone number with `+880-989-76564` hyphens | Cleaned and accepted or clearly rejected |
| Open 3 browser tabs simultaneously | Sessions don't interfere with each other |
| Copy OTP from clipboard | OTP field accepts pasted values |
| Submit form via keyboard Enter only (no mouse) | Form submits correctly |
| Emoji in text fields `😀` | Handled gracefully, not stored as garbage |
| URL manipulation — inject `?admin=true` | No privilege escalation |
| Refresh page during OTP countdown | Countdown resets cleanly |
| Very long session — sit idle 30 min | Session timeout / re-auth flow works |

**Test class:** `TestScenarioOutOfTheBox`

---

### 8. Security
> Automated injection and auth bypass checks on every input surface.

| Type | What is tested |
|---|---|
| XSS | `<script>alert(1)</script>`, `"><img src=x onerror=alert(1)>`, 50 payloads |
| SQL Injection | `' OR '1'='1`, `'; DROP TABLE users;--`, 50 payloads |
| SSTI | `{{7*7}}`, `${7*7}`, `<%= 7*7 %>` |
| IDOR | Direct `/api/users/1`, `/api/users/2` — must require auth |
| Auth bypass | Forged JWT, missing Bearer token, expired token |
| HTTPS | All requests over TLS, no mixed content |
| CSP headers | Content-Security-Policy present on all pages |
| Cookie flags | `Secure`, `HttpOnly`, `SameSite` on session cookies |
| Open redirect | `?next=https://evil.com` must not redirect off-domain |

**Test classes:** `TestQA03Security` · `TestQA13SecurityHeaders` · `TestQA14CookieSecurity` · `TestQA15OWASPSurface`

---

### 9. Performance
> Timing and resource budgets.

| Metric | Budget |
|---|---|
| Page load (DOMContentLoaded) | ≤ 8 seconds |
| API response (login, search) | ≤ 5 seconds |
| Largest Contentful Paint (LCP) | ≤ 3.5 seconds |
| Time to Interactive (TTI) | ≤ 6 seconds |
| JS heap growth across 3 navigations | ≤ 50 MB increase |

**Test classes:** `TestQA04PerformanceAndJSErrors` · `TestQA16Lighthouse` · `TestQA17MemoryLeak`

---

### 10. Accessibility
> WCAG 2.1 AA compliance checks.

| Check | Details |
|---|---|
| Keyboard navigation | Tab through all interactive elements, Enter/Space activates |
| Focus visible | Focus ring visible on all focusable elements |
| ARIA labels | Buttons, inputs, dialogs have descriptive labels |
| Heading hierarchy | H1 → H2 → H3 — no skipped levels |
| Image alt text | All `<img>` have non-empty `alt` attributes |
| Colour contrast | Text/background contrast meets 4.5:1 ratio |
| Screen reader | `role="dialog"`, `aria-modal`, `aria-label` present |

**Test class:** `TestQA07Accessibility`

---

### 11. i18n / RTL
> Arabic language and right-to-left layout checks.

| Check | Details |
|---|---|
| Language switch EN → AR | URL changes to `/ar/`, page content is Arabic |
| RTL layout direction | `dir="rtl"` or `direction: rtl` on body/main |
| Arabic text renders | Key headings render as Arabic Unicode, not boxes |
| Numbers in Arabic locale | Dates and amounts shown in correct format |
| Modal works in Arabic | Login modal fields and buttons functional in AR |

**Test class:** `TestQA10I18nAndRTL`

---

### 12. API & Network
> HTTP-level checks beyond what the browser renders.

| Check | Details |
|---|---|
| All API calls return 2xx | No silent 404/500 on page load |
| No 3rd-party data leakage | Request headers don't contain sensitive tokens |
| CORS policy | API rejects cross-origin requests from unknown domains |
| Rate limiting | Rapid login attempts return 429, not 200 |
| Response content-type | JSON APIs return `application/json` |

**Test class:** `TestQA06APIAndNetwork` · `TestQA18NetworkResilience`

---

### 13. Visual Regression
> Pixel-diff screenshots compared against approved baselines.

| Page | Breakpoints |
|---|---|
| Homepage | 1280px, 768px, 375px |
| Login modal | 1280px, 375px |
| Find Tutors | 1280px, 768px |
| Tutor profile | 1280px, 375px |

**Test class:** `TestQA11VisualRegression`

---

### 14. Mobile / Viewport
> Layout, touch targets, and scroll behaviour on small screens.

| Device | Viewport |
|---|---|
| iPhone SE | 375 × 667 |
| iPhone 14 | 390 × 844 |
| iPad | 768 × 1024 |
| Galaxy S21 | 360 × 800 |

| Check | Details |
|---|---|
| Touch targets | All buttons ≥ 44 × 44 px |
| No horizontal scroll | Page fits within viewport width |
| Hamburger menu | Opens/closes and links work |

**Test class:** `TestQA08MobileAndViewport`

---

## How Spec-Driven URLs Work

Every spec file begins with:

```markdown
# Page: Login — Homepage & Student Login Modal

**URL:** `https://dev.mehadedu.com/en`
```

The tests read this URL automatically — nothing is hard-coded:

```python
# In tests/test_qa_comprehensive.py
def _spec_url(spec_name: str, fallback: str = "") -> str:
    spec_path = Path(__file__).parent.parent / "specs" / f"{spec_name}.md"
    if spec_path.exists():
        m = re.search(r'\*\*URL:\*\*\s*`(.+?)`', spec_path.read_text())
        if m:
            return m.group(1).strip()
    return fallback or os.getenv("BASE_URL", "https://dev.mehadedu.com/en")
```

**To point tests at a different environment**, update the URL in the relevant spec file:

```markdown
**URL:** `https://staging.mehadedu.com/en`
```

Run the tests — they automatically target the new URL. No `.env` changes, no CI secrets to update.

---

## Installation

### Requirements

- Python 3.12+
- Node.js 18+ (for WhatsApp bridge on production)
- Git

### One-time setup

```bash
# 1 — Clone
git clone https://github.com/Qatarat/mehad-automation
cd mehad-automation

# 2 — Python dependencies
pip install -r requirements.txt

# 3 — Browser engine
playwright install chromium

# 4 — WhatsApp bridge (production OTP only)
cd scripts && npm install && cd ..

# 5 — Settings file
cp .env.example .env   # then edit .env
```

---

## Configuration (.env)

### Staging (recommended starting point — no real phone needed)

```dotenv
BASE_URL=https://dev.mehadedu.com/en

TEST_PHONE=98976564
TEST_COUNTRY=+880
TEST_OTP=123456

TEACHER_PHONE=98976564
TEACHER_OTP=123456

STUDENT_PHONE=98976564
STUDENT_OTP=123456
```

> Staging always accepts OTP `123456` for registered test accounts.

### Production (requires WhatsApp OTP reader — see next section)

```dotenv
BASE_URL=https://mehadedu.com/en

PROD_OTP_BACKEND=waha          # or: twilio | whatsapp_local | manual
PROD_COUNTRY_CODE=+966
PROD_TEST_PHONE=501234567
PROD_TEACHER_PHONE=501234567
PROD_STUDENT_PHONE=501234567

WAHA_URL=http://localhost:3000
WAHA_SESSION=default
WAHA_CHAT_ID=+966501234567@c.us
```

---

## Running Tests

### By scenario type

```bash
# All 2000+ tests
pytest tests/test_qa_comprehensive.py tests/test_specs_all.py -v

# Happy Path only
pytest tests/test_qa_comprehensive.py -k "HappyPath" -v

# Valid data scenarios
pytest tests/test_qa_comprehensive.py -k "ValidData" -v

# Invalid data scenarios
pytest tests/test_qa_comprehensive.py -k "InvalidData" -v

# Empty input scenarios
pytest tests/test_qa_comprehensive.py -k "EmptyInput" -v

# UAT scenarios
pytest tests/test_qa_comprehensive.py -k "UAT" -v

# Out of the box scenarios
pytest tests/test_qa_comprehensive.py -k "OutOfTheBox" -v

# Security only
pytest tests/test_qa_comprehensive.py -k "Security" -v

# Accessibility only
pytest tests/test_qa_comprehensive.py -k "Accessibility" -v

# Performance only
pytest tests/test_qa_comprehensive.py -k "Performance or Lighthouse or MemoryLeak" -v
```

### By QA agent number

```bash
pytest tests/test_qa_comprehensive.py::TestQA01Functional -v       # Functional
pytest tests/test_qa_comprehensive.py::TestQA02EdgeCaseBoundary -v # Edge cases
pytest tests/test_qa_comprehensive.py::TestQA03Security -v         # Security
pytest tests/test_qa_comprehensive.py::TestQA07Accessibility -v    # Accessibility
pytest tests/test_qa_comprehensive.py::TestQA08MobileAndViewport -v # Mobile
```

### Spec-driven tests (all 68 pages)

```bash
# Regenerate test_specs_all.py from the 68 spec files, then run
python3 scripts/validate_all_specs.py
pytest tests/test_specs_all.py -v

# Single page
pytest tests/test_specs_all.py -k "Login" -v

# With visible browser (great for debugging)
HEADED=1 SLOW_MO=800 pytest tests/test_specs_all.py -k "Login" -v

# Parallel (4 workers)
pytest tests/test_specs_all.py -n 4 -v
```

### Generate an HTML report

```bash
pytest tests/ --html=reports/index.html --self-contained-html -v
```

Open `reports/index.html` in your browser.

---

## Quick Start: Test on Dev or Production

Follow these steps to run the full test suite locally against either environment in under 10 minutes.

---

### Option A — Dev Server (Recommended · No real phone needed)

The dev environment uses a **fixed OTP `123456`** for all test accounts — no WhatsApp or SMS required.

**Step 1 — Clone and install**

```bash
git clone https://github.com/Qatarat/mehad-automation
cd mehad-automation
pip install -r requirements.txt
playwright install chromium
```

**Step 2 — Create `.env`**

```dotenv
# .env  (copy from .env.example and set these values)

BASE_URL=https://dev.mehadedu.com/en

# Student account (pre-registered on dev)
STUDENT_PHONE=98765432
STUDENT_OTP=123456
TEST_COUNTRY=+880

# Tutor account (pre-registered on dev)
TEACHER_PHONE=98976564
TEACHER_OTP=123456
```

> Both accounts are already registered on `dev.mehadedu.com` and always accept OTP `123456`.

**Step 3 — Run**

```bash
# Full suite
pytest tests/ -v

# Payment tests only (sandbox — no real charges)
pytest tests/test_payment_flow.py -v

# Spec-driven tests for all 69 pages
pytest tests/test_specs_all.py -v

# Single feature
pytest tests/test_specs_all.py -k "payment" -v

# With visible browser (good for watching the tests run)
HEADED=1 SLOW_MO=500 pytest tests/test_payment_flow.py -v
```

**Expected result:** All 5 payment tests pass in ~2 minutes. Full suite runs in ~15–20 minutes.

---

### Option B — Production Server (Real phone · Live environment)

Production uses **real SMS/WhatsApp OTPs**. You need a phone number registered on `mehadedu.com`.

> **⚠️ Payment warning:** The production gateway (`sa.myfatoorah.com`) is **live**. Tests verify the booking and payment page load, card fields render, and failure errors show correctly — **no real charge is made** unless you provide a real card.

**Step 1 — Clone and install (same as dev)**

```bash
git clone https://github.com/Qatarat/mehad-automation
cd mehad-automation
pip install -r requirements.txt
playwright install chromium
```

**Step 2 — Create `.env`**

```dotenv
# .env

BASE_URL=https://mehadedu.com/en

# Your registered student account on mehadedu.com
STUDENT_PHONE=1316314566      # digits only, no country code
TEST_COUNTRY=+880              # your country code

# Your registered teacher account
TEACHER_PHONE=1316314566

# OTP method — choose one:
PROD_OTP_BACKEND=manual       # simplest: you type OTP when prompted
# PROD_OTP_BACKEND=waha       # automated via WAHA Docker (see OTP Options section)
```

**Step 3 — Run with manual OTP**

```bash
# Run a single test with -s so the OTP prompt appears in your terminal
pytest tests/test_login_e2e.py -v -s

# When you see "Enter OTP:" in the terminal, check your WhatsApp and type it
```

**Step 4 — Run a specific production scenario**

```bash
# Test the full signup → booking → payment flow
pytest tests/test_specs_all.py -k "production_e2e" -v -s

# Test payment page only (verifies iframe loads + failure page)
pytest tests/test_payment_flow.py::TestPaymentFlow::test_02_payment_iframe_renders -v -s

# Test student login
pytest tests/test_specs_all.py -k "student_login" -v -s
```

**Step 5 — Run all tests with automated OTP (WAHA)**

```bash
# Start WAHA (one-time setup)
docker run -d --name waha -p 3000:3000 devlikeapro/waha

# Open http://localhost:3000/dashboard → Start session → scan QR with WhatsApp
# Update .env:
#   PROD_OTP_BACKEND=waha
#   WAHA_URL=http://localhost:3000
#   WAHA_SESSION=default
#   WAHA_CHAT_ID=+8801316314566@c.us   # your full phone with country code

# Now run the full suite unattended
pytest tests/ -v
```

---

### Dev vs Production — At a Glance

| | Dev (`dev.mehadedu.com`) | Production (`mehadedu.com`) |
|---|---|---|
| **OTP** | Fixed `123456` — no phone needed | Real SMS/WhatsApp OTP |
| **Payment gateway** | `demo.myfatoorah.com` (sandbox) | `sa.myfatoorah.com` (live) |
| **Test card** | `4111 1111 1111 1111` — always succeeds | Same card — rejected (no charge) |
| **Booking prefix** | `DBK-YYYYMMDD-XXXXXX` | `BK-YYYYMMDD-XXXXXX` |
| **3DS** | ACS Emulator auto-approves | Real 3DS challenge |
| **Setup time** | ~5 minutes | ~10 minutes + phone registration |
| **Best for** | CI, automation, PR checks | Smoke tests, pre-release checks |

---

### Running a Targeted Smoke Test (Both Environments)

This one-liner checks the most critical flows — login, booking, and payment page — in under 3 minutes:

```bash
# Dev smoke test
pytest tests/test_login.py tests/test_payment_flow.py -v --timeout=60

# Production smoke test (manual OTP)
BASE_URL=https://mehadedu.com/en pytest tests/test_login_e2e.py tests/test_specs_all.py -k "student_login or payment" -v -s --timeout=90
```

---

## Production E2E Verified Results

Full end-to-end walkthrough on `https://mehadedu.com` — verified 2026-06-06.

### New Teacher Onboarding Flow (Production)
| Step | URL | Status |
|------|-----|--------|
| Become-a-Tutor → Apply Now | `/en/become-tutor` | ✅ |
| Teacher OTP login | `/en/tutor-login` | ✅ |
| 4-step profile wizard | `/en/tutor/profile` | ✅ |
| Application submitted (pending) | `/en/tutor/profile` success screen | ✅ |
| Admin approves → dashboard unlocks | `/en/dashboard` | ✅ |
| Instructor profile data in 3 tabs | `/en/dashboard/instructor-profile` | ✅ |
| Public profile visible | `/en/tutor/301` | ✅ |
| Set availability (Mon–Fri 10–12) | `/en/dashboard/availability` | ✅ |
| Slots appear on public profile | `/en/tutor/301` | ✅ |

### Student Booking Flow (Production)
| Step | Status |
|------|--------|
| Student login (homepage modal) | ✅ |
| Navigate to tutor, see slots | ✅ |
| Book Trial Lesson dialog (duration, date, time) | ✅ |
| Review & Confirm (100 SAR) | ✅ |
| Redirect to payment page | ✅ |
| MyFatoorah iframe loads | ✅ |
| Card fields accept input | ✅ |
| Payment failure error page (`status=failed`) | ✅ |
| Payment success (live card) | 🔲 Requires real card |

### Production-Specific Notes
- **Same phone → dual roles:** One phone number can hold separate student (userId 514) and tutor (userId 615) accounts. Student logs in via homepage modal; tutor logs in via `/en/tutor-login`.
- **Tutor profile ID ≠ User ID:** Tutor profile ID (301) is different from the auth userId (615). Resolved via `GET /api/v1/public/tutors/{id}`.
- **Live payment gateway:** `sa.myfatoorah.com` — real charges apply. Test card `4111 1111 1111 1111` is declined (no charge), but failure page renders correctly.
- **Booking number prefix:** Production uses `BK-` prefix; dev uses `DBK-` prefix.
- **`/en/tutors` is 404:** Use `/en/find-tutors` for tutor listing on production.

See [`specs/production_e2e.md`](specs/production_e2e.md) for the complete step-by-step walkthrough with all observed selectors, URLs, and test data.

---

## OTP Options for Production

When `BASE_URL` points to `mehadedu.com`, the test auto-detects production mode and needs a real OTP reader.

### Option A — WAHA (Recommended · Docker)

```bash
# Start WAHA
docker run -d --name waha --restart unless-stopped -p 3000:3000 devlikeapro/waha

# Scan QR: http://localhost:3000/dashboard → Start session → default
# .env: PROD_OTP_BACKEND=waha
```

### Option B — whatsapp-web.js (No Docker)

```bash
# Already installed. Start in a separate terminal:
cd scripts && node whatsapp_otp_server.js
# Scan QR in terminal. Keep it open.
# .env: PROD_OTP_BACKEND=whatsapp_local
```

### Option C — Twilio

```dotenv
PROD_OTP_BACKEND=twilio
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_NUMBER=+14155238886
```

### Option D — Manual (Zero setup)

```bash
# Just run tests with -s. The test will pause and ask you to type the OTP.
pytest tests/test_qa_comprehensive.py::TestQA01Functional::test_qa01_full_login_flow_success -v -s
```

### Which option?

| Situation | Best option |
|---|---|
| Staging tests | None needed — fixed OTP `123456` used automatically |
| Quick production check | **D — Manual** (zero setup) |
| Automated production CI | **A — WAHA** (reliable, persistent session) |
| No Docker | **B — whatsapp-web.js** |
| Already using Twilio | **C — Twilio** |

---

## CI / GitHub Actions

Tests run automatically on every push to `main` and nightly at 02:00 UTC.

### Secrets to configure (GitHub → Settings → Secrets → Actions)

| Secret | Value |
|---|---|
| `TEST_OTP` | `123456` |
| `TEST_PHONE` | `98976564` |
| `TEST_COUNTRY` | `+880` |
| `TEACHER_PHONE` | `98976564` |
| `STUDENT_PHONE` | `98976564` |

### Trigger a run manually

1. GitHub → **Actions** tab
2. Click **Mehad Autonomous AI Testing**
3. Click **Run workflow**

Results publish automatically to [qatarat.github.io/mehad-automation](https://qatarat.github.io/mehad-automation/).

---

## Adding a New Page

1. Create `specs/my_new_page.md`:

```markdown
# Page: My New Page

**URL:** `https://dev.mehadedu.com/en/my-page`

## Description
Brief description of what this page does.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Submit button | `button:has-text("Submit")` | Required |
| Name input | `input[name="name"]` | Required |

## User Flows

### Flow 1: Happy Path
1. Navigate to page
2. Fill name input with "Test User"
3. Click Submit
→ Expected: Success message visible

## Requirements
- REQ-01: Page loads without 5xx errors

## Edge Cases
| EC-01 | Empty name submitted | Error message shown |
| EC-02 | Name with XSS payload | Input sanitised |

## Test Data
### Valid
| Field | Value |
|---|---|
| name | Test User |
| name | أحمد |

### Invalid
| Field | Value |
|---|---|
| name | <script>alert(1)</script> |
| name | ' OR 1=1-- |
```

2. Regenerate and run:

```bash
python3 scripts/validate_all_specs.py
pytest tests/test_specs_all.py -k "MyNewPage" -v
```

Tests are generated automatically from the spec. No code required.

---

## Project Structure

```
mehad-automation/
│
├── specs/                         # 68 page spec files (plain text)
│   ├── login.md                   # Login page — URL, flows, test data
│   ├── student_login.md           # Student login spec
│   ├── student_payment.md         # Payment flow spec
│   └── ...                        # One .md per page
│
├── tests/
│   ├── test_qa_comprehensive.py   # 215+ hand-crafted tests (all scenario types)
│   ├── test_specs_all.py          # Auto-generated from specs/ (1200+ tests)
│   ├── test_login_e2e.py          # Login E2E tests
│   ├── test_signup_e2e.py         # Signup E2E tests
│   └── test_payment_flow.py       # Payment flow tests
│
├── ai_engine/                     # AI test generator
│   ├── agent.py                   # Autonomous AI test agent
│   ├── spec_parser.py             # Reads spec .md files
│   ├── spec_compiler.py           # Compiles specs to JSON
│   ├── test_generator.py          # Generates Playwright code from specs
│   └── reporter.py                # Builds HTML bug reports
│
├── scripts/
│   ├── consolidate_reports.py     # Merges all agent results
│   ├── build_pages_site.py        # Builds GitHub Pages dashboard
│   ├── validate_all_specs.py      # Regenerates test_specs_all.py
│   ├── get_otp.py                 # Reads OTP from WhatsApp/Twilio/manual
│   └── bug_clustering.py          # Groups bugs by root cause + trend tracking
│
├── payloads/
│   ├── xss.txt                    # 50 XSS payloads
│   ├── sqli.txt                   # 50 SQL injection payloads
│   └── boundary.txt               # Boundary value strings
│
├── gh-pages-site/                 # Built dashboard (deployed to GitHub Pages)
│
├── .github/workflows/ai-tests.yml # CI pipeline (18 parallel QA agents)
├── requirements.txt
└── .env.example
```

---

## Test Data Reference

### Login

| Type | Country | Phone | OTP | Expected result |
|---|---|---|---|---|
| Valid | +880 (BD) | `98976564` | `123456` | Login succeeds |
| Valid | +966 (SA) | `501234567` | `123456` | Login succeeds |
| Invalid | +880 | `abc123` | — | Input rejected |
| Invalid | +880 | `123` | — | Send Code disabled |
| Invalid | — | `98976564` | `000000` | Error message |
| Empty | — | `` | — | Send Code disabled |
| Empty | — | `98976564` | `` | Continue disabled |
| Boundary | +880 | `1234567` (7 digits) | — | Min valid length |
| Boundary | +880 | `1234567890123` (13 digits) | — | Over max length |
| XSS | — | `<script>alert(1)</script>` | — | Sanitised or rejected |
| SQLi | — | `' OR '1'='1` | — | Sanitised or rejected |

### Booking / Session

| Type | Data | Expected |
|---|---|---|
| Valid | Future date, available slot, registered tutor | Booking confirmed |
| Invalid | Past date | Calendar blocks selection |
| Invalid | Unavailable time slot | Slot greyed out |
| Out of bounds | Same-day booking (0 hours notice) | Warning or blocked |
| Duplicate | Re-book exact same slot | Conflict error |

### Search

| Type | Query | Expected |
|---|---|---|
| Valid | `Math` | Results list with tutors |
| Valid | `رياضيات` (Arabic) | Results in Arabic locale |
| Empty | `` | All tutors or placeholder |
| Special chars | `@#$%^` | Empty results, no crash |
| XSS | `<script>alert(1)</script>` | Escaped in results, no alert |
| Very long | 1000-char string | Truncated or rejected gracefully |

---

## Troubleshooting

### "Auth setup failed" / Login not working

```bash
# Watch the browser to see what's happening
HEADED=1 pytest tests/test_qa_comprehensive.py::TestQA01Functional -v -k "login"
```

Check:
- `TEST_PHONE` is a registered staging account
- `TEST_OTP=123456` is in `.env`
- Staging server is up: `curl https://dev.mehadedu.com/en`

### WhatsApp OTP never arrives

- **WAHA:** Check http://localhost:3000/dashboard — session must show **WORKING**
- **whatsapp-web.js:** Keep `node whatsapp_otp_server.js` terminal open
- Phone number in `.env` must match the WhatsApp account connected to WAHA

### "playwright: Executable doesn't exist"

```bash
playwright install chromium
```

### Tests run very slowly

```bash
# Lower load timeout and skip headed mode
LOAD_TIME_LIMIT=20 pytest tests/test_specs_all.py -v --timeout=30
```

### Spec URL not being picked up

Check your spec file has this exact format:

```markdown
**URL:** `https://dev.mehadedu.com/en/your-page`
```

Backticks required. No extra spaces inside them.

### Re-generate tests after editing a spec

```bash
python3 scripts/validate_all_specs.py
pytest tests/test_specs_all.py -v
```

---

## Getting Help

- Check the **Troubleshooting** section above
- Add `HEADED=1` to watch the browser
- [Open an issue](https://github.com/Qatarat/mehad-automation/issues)
- [View the live dashboard](https://qatarat.github.io/mehad-automation/)

---

<div align="center">

**Mehad Autonomous QA Platform**

Built by **[Mejbaur Bahar Fagun](mailto:mejbaur@markopolo.ai)**  
Senior Software Engineer QA (IV) · Markopolo.ai

Powered by Playwright · Ollama · 22 AI QA Agents

</div>
