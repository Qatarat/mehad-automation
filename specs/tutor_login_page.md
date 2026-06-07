# Teacher Login Page Spec

**URL:** `https://dev.mehadedu.com/en/tutor-login`

## Overview
The Teacher Login page (`/en/tutor-login`) is a standalone page (not a modal) for tutors to authenticate via WhatsApp OTP. It is reached from the Become a Tutor page's "Apply Now" button. After successful authentication existing tutors land on `/en/dashboard/availability`. New tutors see a multi-step signup form.

## URL
`/en/tutor-login`

## Roles
- Public (unauthenticated tutor applicant / existing tutor)

## Prerequisites
- Tutor credentials: Bangladesh +880, phone 98976564, OTP 123456 (staging hardcoded)
- Expected name after login: "Automations Tutor"

## Test Scenarios

### TL-01: Page loads with Teacher Login heading
**Given** a user navigates to `https://dev.mehadedu.com/en/tutor-login`
**When** the page finishes loading
**Then** the heading "Teacher Login" and subtitle "Sign in to access your teaching dashboard" are visible
**Selectors:**
- heading: `h2:has-text("Teacher Login")`
- subtitle: `p:has-text("Sign in to access your teaching dashboard")`

### TL-02: Form is inline (not a modal dialog)
**Given** the teacher login page is loaded
**When** the user views the page
**Then** the OTP form is displayed inline on the page (not inside a [role=dialog])
**Selectors:**
- inline form: `main input[type="tel"]`
- no dialog: `[role="dialog"]` should NOT exist

### TL-03: Country code defaults to +966
**Given** the teacher login page is loaded
**When** the user views the country code button
**Then** it shows "+966" (Saudi Arabia) by default
**Selectors:**
- country button: `button:has-text("+966")`

### TL-04: Country code can be changed via searchable dropdown
**Given** the teacher login page is loaded
**When** the user clicks the country code button and searches "Bangladesh"
**Then** the "Bangladesh +880" option appears and can be selected
**Selectors:**
- country button: `button:has-text("+966")`
- search input: `input[placeholder="Search..."], input[placeholder*="Search"]`
- bangladesh option: `[role=option]:has-text("Bangladesh")`

### TL-05: Send Code button disabled when phone is empty
**Given** the teacher login page is loaded
**When** no phone number has been entered
**Then** the Send Code button is disabled
**Selectors:**
- send code: `button:has-text("Send Code")[disabled]`

### TL-06: Send Code enables after valid phone entry
**Given** the teacher login page is loaded
**When** the user enters a valid phone number (e.g. 98976564 with +880)
**Then** the Send Code button becomes enabled and a "Valid phone number" hint appears
**Selectors:**
- phone input: `input[type="tel"]`
- send code enabled: `button:has-text("Send Code"):not([disabled])`
- valid hint: `text="Valid phone number"`

### TL-07: OTP field is disabled until Send Code is clicked
**Given** the teacher login page is loaded and a valid phone has been entered
**When** before Send Code is clicked
**Then** the OTP input field with placeholder "000000" is disabled
**Selectors:**
- otp input disabled: `input[placeholder="000000"][disabled]`

### TL-08: After Send Code, OTP field enables and Resend timer appears
**Given** the teacher login page is loaded and a valid phone has been entered
**When** the user clicks Send Code
**Then** the OTP field becomes enabled, "Code already sent" hint appears, and a disabled "Resend in Xs" button is shown
**Selectors:**
- otp input enabled: `input[placeholder="000000"]:not([disabled])`
- code sent hint: `text="Code already sent"`
- resend button: `button:has-text("Resend in")`
- change number button: `button:has-text("Change mobile number")`

### TL-09: Successful teacher OTP login redirects to availability dashboard
**Given** the teacher login page is loaded
**When** the user enters +880, phone 98976564, clicks Send Code, enters OTP 123456, and clicks Continue
**Then** the browser navigates to `/en/dashboard/availability` and the sidebar shows "Automations Tutor"
**Selectors:**
- otp input: `input[placeholder="000000"]`
- continue button: `button:has-text("Continue")`
- post-login url: `/en/dashboard/availability`
- teacher name: `text="Automations Tutor"`

### TL-10: Change mobile number link resets the form
**Given** the OTP has been sent on the teacher login page
**When** the user clicks "Change mobile number"
**Then** the OTP field is hidden/disabled and the phone entry state is restored
**Selectors:**
- change number: `button:has-text("Change mobile number")`

### TL-11: Negative — Wrong OTP shows error
**Given** OTP has been sent on the teacher login page
**When** the user enters an incorrect OTP (e.g. "000000") and clicks Continue
**Then** an error message is displayed and login does not succeed
**Selectors:**
- otp input: `input[placeholder="000000"]`
- continue button: `button:has-text("Continue")`
- error: `text=/invalid|incorrect|wrong|error/i`

### TL-12: Negative — Phone too short keeps Send Code disabled
**Given** the teacher login page is loaded
**When** the user enters fewer than 7 digits in the phone field
**Then** the Send Code button remains disabled
**Selectors:**
- phone input: `input[type="tel"]`
- send code disabled: `button:has-text("Send Code")[disabled]`
