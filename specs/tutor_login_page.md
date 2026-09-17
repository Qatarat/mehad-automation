# Tutor Login Page Spec

**URL:** `https://dev.mehadedu.com/en/tutor-login`

## Overview
The Tutor Login page (`/en/tutor-login`) is a standalone page (not a modal) for tutors to authenticate via **Email Address + 4-digit OTP** (not phone/WhatsApp — corrected 2026-09-17 after live verification against dev.mehadedu.com found this entire spec was stale). It is reached from the Become a Tutor page's "Apply Now" button. The page heading is "Tutor Login" (not "Teacher Login"). After successful authentication, existing tutors land on `/en/dashboard/instructor-profile` (not `/en/dashboard/availability`). The OTP field auto-submits on reaching 4 digits and navigates immediately — there is no "Continue" button in this flow.

This stale spec was the root cause of a CI-wide failure: the shared Python auth helper (`scripts/validate_all_specs.py::_otp_login`) had been built against this incorrect documentation and unconditionally tried a phone/country-code flow that doesn't exist on this page, causing every test that depends on tutor authentication (the majority of the generated suite, since the default `page` fixture logs in as Tutor) to fail at the very first setup step. See the accompanying fix commit for the corrected helper.

## URL
`/en/tutor-login`

## Roles
- Public (unauthenticated tutor applicant / existing tutor)

## Prerequisites
- Tutor credentials (dev, live-verified 2026-09-17): email `rumelmhmd@gmail.com`, OTP `6789`
- Expected name after login: "Tester Teacher" (dev) — the dashboard.html credential vault documents "Automations Tutor" as the production account's display name; the two environments use different seeded accounts
- Expected landing page after login: `/en/dashboard/instructor-profile`

## Test Scenarios

### TL-01: Page loads with Tutor Login heading
**Given** a user navigates to `https://dev.mehadedu.com/en/tutor-login`
**When** the page finishes loading
**Then** the heading "Tutor Login" and subtitle "Sign in to access your teaching dashboard" are visible
**Selectors:**
- heading: `h2:has-text("Tutor Login")`
- subtitle: `p:has-text("Sign in to access your teaching dashboard")`

### TL-02: Form is inline (not a modal dialog) and uses email, not phone
**Given** the tutor login page is loaded
**When** the user views the page
**Then** the login form is displayed inline on the page (not inside a `[role=dialog]`) with an Email Address field — there is no country-code selector or `input[type="tel"]` anywhere on this page
**Selectors:**
- email input: `input[type="email"], input[placeholder*="email" i]`
- no dialog: `[role="dialog"]` should NOT exist
- no tel input: `input[type="tel"]` should NOT exist
- no country-code button: `button:has-text("+966")` should NOT exist

### TL-03: Send Code button disabled when email is empty
**Given** the tutor login page is loaded
**When** no email has been entered
**Then** the Send Code button is disabled or clicking it performs no action
**Selectors:**
- send code: `button:has-text("Send Code")`

### TL-04: Send Code enables after valid email entry
**Given** the tutor login page is loaded
**When** the user enters a valid email address
**Then** the Send Code button becomes clickable
**Selectors:**
- email input: `input[type="email"]`
- send code enabled: `button:has-text("Send Code"):not([disabled])`

### TL-05: OTP field is disabled until Send Code is clicked
**Given** the tutor login page is loaded and a valid email has been entered
**When** before Send Code is clicked
**Then** the OTP input field (placeholder "0000") is disabled
**Selectors:**
- otp input disabled: `input[placeholder="0000"][disabled]`

### TL-06: After Send Code, OTP field enables and a resend cooldown appears
**Given** the tutor login page is loaded and a valid email has been entered
**When** the user clicks Send Code
**Then** the OTP field becomes enabled, a "Code already sent" hint appears near Send Code, and a "Resend in Xs" countdown is shown
**Selectors:**
- otp input enabled: `input[placeholder="0000"]:not([disabled])`
- code sent hint: `text="Code already sent"`
- resend countdown: `text=/Resend in \\d+s/`

### TL-07: Successful tutor OTP login auto-submits and redirects to Instructor Profile
**Given** the tutor login page is loaded
**When** the user enters a valid email, clicks Send Code, then enters the correct 4-digit OTP
**Then** the form auto-submits on the 4th digit (no Continue click needed) and the browser navigates to `/en/dashboard/instructor-profile` with the tutor's name visible in the header account switcher
**Selectors:**
- otp input: `input[placeholder="0000"]`
- post-login url: `/en/dashboard/instructor-profile`
- account switcher name: `[data-testid="account-name"], header :text("Tutor")`

### TL-08: Negative — Wrong OTP shows error and does not navigate
**Given** OTP has been sent on the tutor login page
**When** the user enters an incorrect 4-digit OTP (e.g. "0000")
**Then** an error message is displayed and the page does not navigate away from `/en/tutor-login`
**Selectors:**
- otp input: `input[placeholder="0000"]`
- error: `text=/invalid|incorrect|wrong|error/i`

### TL-09: Negative — Malformed email keeps Send Code disabled
**Given** the tutor login page is loaded
**When** the user enters a malformed email (e.g. "not-an-email")
**Then** the Send Code button remains disabled or an inline validation error is shown
**Selectors:**
- email input: `input[type="email"]`
- send code: `button:has-text("Send Code")`

### TL-10: Resend cooldown blocks immediate re-send
**Given** Send Code was just clicked (cooldown active)
**When** the user attempts to click Send Code again before the cooldown expires
**Then** no new code is sent and the countdown continues (button is disabled during cooldown)
**Selectors:**
- resend/send code button: `button:has-text("Resend in"), button:has-text("Send Code")`

## Edge Cases
| EC-01 | Email field with SQL injection payload (' OR 1=1--) | Rejected as invalid email format, no 500, no auth bypass |
| EC-02 | Email field with XSS payload (<script>alert(1)</script>) | Rejected as invalid email format or safely escaped, no script execution |
| EC-03 | OTP field with non-numeric input | Rejected, numeric-only enforced |
| EC-04 | OTP field with fewer than 4 digits, wait past auto-submit expectation | Does not auto-submit prematurely; no partial-code submission |
| EC-05 | Rapid repeated Send Code clicks (bypassing UI cooldown via fast automation) | Server-side rate limiting still applies, no unbounded OTP spam |
| EC-06 | Navigate directly to `/en/dashboard/instructor-profile` while logged out | Redirected to `/en/tutor-login`, no dashboard content leaks |

## Test Data
### Valid
| Field | Value |
|---|---|
| email | rumelmhmd@gmail.com |
| name | 6789 |

### Invalid
| Field | Value |
|---|---|
| email | not-an-email |
| email | ' OR 1=1-- |
| email | <script>alert(1)</script> |
| name | 0000 |
| name | abcd |
