# Page: Login — Homepage & Student Login Modal

**URL:** `https://dev.mehadedu.com/en`

## Description
The Mehad homepage is the primary entry point for students. The "Log In" button in the header opens a WhatsApp OTP modal. Students authenticate with country code + phone number + 6-digit OTP.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Log In button | `button:has-text("Log In")` | Required — opens login modal |
| Login modal dialog | `[role="dialog"]` | Required — appears after clicking Log In |
| Modal heading | `[role="dialog"] h2:has-text("Welcome back")` | Required |
| Country code button | `[role="dialog"] [aria-label="Country code"], [role="dialog"] button:has-text("+966")` | Required — default +966 |
| Phone number input | `[role="dialog"] input[type="tel"], [role="dialog"] input[placeholder="50 123 4567"]` | Required |
| Send Code button | `[role="dialog"] button:has-text("Send Code")` | Required |
| OTP input | `[role="dialog"] input[placeholder="000000"], [role="dialog"] input[autocomplete="one-time-code"]` | Required |
| Continue button | `[role="dialog"] button:has-text("Continue")` | Required |
| Close modal button | `[role="dialog"] button[aria-label="Close"], [role="dialog"] [data-slot="dialog-close"]` | Optional |
| Change number link | `[role="dialog"] button:has-text("Change Mobile Number")` | Conditional — visible after Send Code |
| Find Tutors button | `button:has-text("Find Tutors"), nav button:has-text("Find Tutors")` | Required |
| Become a Tutor link | `a[href="/en/become-tutor"]` | Required |

## User Flows

### Flow 1: Successful Student Login
1. Navigate to https://dev.mehadedu.com/en
2. Click "Log In" button in header
3. Modal opens with heading "Welcome back"
4. Click country code button (default +966)
5. Search for "Bangladesh" in search input
6. Click "Bangladesh +880" option
7. Enter phone number: 98976564
8. Click "Send Code" button
9. Wait for OTP input to become enabled
10. Enter OTP: 123456
11. Click "Continue" button
→ Expected: Modal closes, user is authenticated, header shows user name

### Flow 2: Login Modal Opens and Closes
1. Navigate to homepage
2. Click "Log In" button
3. Modal is visible with heading "Welcome back"
4. Click close button
→ Expected: Modal closes, no session created

### Flow 3: Country Code Selection
1. Click "Log In" to open modal
2. Click country code button
3. Type "Bangladesh" in search
4. Click "+880" option from list
→ Expected: Country code updates to +880

## Requirements
- REQ-01: Log In button must be visible in header on unauthenticated state
- REQ-02: Clicking Log In opens a dialog with role="dialog" and heading "Welcome back"
- REQ-03: Country code defaults to +966 (Saudi Arabia) and is changeable
- REQ-04: Phone number field is type="tel" with inputmode="numeric"
- REQ-05: Send Code button is disabled until phone field has valid input
- REQ-06: OTP field must be disabled until Send Code is clicked successfully
- REQ-07: OTP field has maxlength="6" and accepts only numeric input
- REQ-08: Continue button triggers authentication and closes modal on success
- REQ-09: After successful login, header shows authenticated user name
- REQ-10: Page title must not contain 500 or 404

## Edge Cases
| EC-01 | Phone field empty — click Send Code | Send Code button stays disabled |
| EC-02 | Invalid phone format (letters) | Input rejects non-numeric characters |
| EC-03 | Wrong OTP entered (000000) | Error message shown, field clears |
| EC-04 | Close modal mid-flow | Modal closes, no session created |
| EC-05 | Already logged-in visits homepage | Log In button replaced by user name |
| EC-06 | Send Code clicked twice | Cooldown timer resets or shows "Code already sent" |
| EC-07 | Phone too short (< 7 digits) | Send Code stays disabled |
| EC-08 | Network failure during OTP send | User-friendly error message shown |

## Test Data
### Valid
| Field | Value |
|---|---|
| name | 98976564 |
| name | 123456 |
| name | +880 |
| name | Automations Student |

### Invalid
| Field | Value |
|---|---|
| name | abc123 |
| name | 123 |
| name | 000000 |
| name | 12345 |
