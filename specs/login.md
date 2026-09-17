# Page: Login — Homepage Login Modal (Parent / Student tabs + Child Login)

**URL:** `https://dev.mehadedu.com/en`

## Description
The Mehad homepage is the primary entry point for Parents and Students. The "Log In" button in the header opens a WhatsApp OTP modal with two tabs: **Parent** (active/default tab) and **Student**. Both authenticate with country code + phone number + 6-digit OTP. Below the OTP form, an "OR / Child Login" link routes to the dedicated username+password Child portal at `/en/child-login`. This corrects an earlier version of this spec that only documented a single "Student" flow — live verification (2026-09-17, Chrome MCP against dev.mehadedu.com) confirmed the modal actually defaults to the **Parent** tab.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Log In button | `button:has-text("Log In")` | Required — opens login modal |
| Login modal dialog | `[role="dialog"]` | Required — appears after clicking Log In |
| Modal heading | `[role="dialog"] h2:has-text("Welcome back")` | Required |
| Parent tab | `[role="dialog"] :text("Parent")` | Required — active/default tab on modal open |
| Student tab | `[role="dialog"] :text("Student")` | Required — second tab |
| Country code button | `[role="dialog"] [aria-label="Country code"], [role="dialog"] button:has-text("+966")` | Required — default +966 |
| Phone number input | `[role="dialog"] input[type="tel"], [role="dialog"] input[placeholder="50 123 4567"]` | Required |
| Send Code button | `[role="dialog"] button:has-text("Send Code")` | Required |
| OTP input | `[role="dialog"] input[placeholder="0000"], [role="dialog"] input[placeholder="000000"], [role="dialog"] input[autocomplete="one-time-code"]` | Required |
| Continue button | `[role="dialog"] button:has-text("Continue")` | Required |
| Close modal button | `[role="dialog"] button[aria-label="Close"], [role="dialog"] [data-slot="dialog-close"]` | Optional |
| Change number link | `[role="dialog"] button:has-text("Change Mobile Number")` | Conditional — visible after Send Code |
| OR divider | `[role="dialog"] :text("OR")` | Required |
| Child Login link | `[role="dialog"] :text("Child Login")` | Required — navigates to `/en/child-login` |
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

### Flow 4: Parent Tab Is the Default Active Tab
1. Navigate to homepage
2. Click "Log In" button
→ Expected: Modal opens with "Parent" tab visually active (underlined/highlighted) and its WhatsApp Number form visible

### Flow 5: Switch to Student Tab
1. Click "Log In" to open modal (Parent tab active by default)
2. Click "Student" tab
→ Expected: Tab switches, form resets (phone + OTP inputs cleared), Student's own OTP form is shown

### Flow 6: Navigate to Child Login From Modal
1. Click "Log In" to open modal
2. Scroll to "OR" divider
3. Click "Child Login"
→ Expected: Browser navigates to `/en/child-login`, modal closes, a Username/Password form is shown (no OTP)

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
- REQ-11: Parent tab is selected/active by default when the modal first opens
- REQ-12: Switching tabs (Parent <-> Student) must reset the phone/OTP form state
- REQ-13: Each tab authenticates against its own role — a Parent OTP session must not grant Student-only routes and vice versa
- REQ-14: "Child Login" link must always be visible below the OR divider regardless of active tab
- REQ-15: Child Login must not accept a blank username or blank password (Login button disabled or inline error)

## Edge Cases
| EC-01 | Phone field empty — click Send Code | Send Code button stays disabled |
| EC-02 | Invalid phone format (letters) | Input rejects non-numeric characters |
| EC-03 | Wrong OTP entered (000000) | Error message shown, field clears |
| EC-04 | Close modal mid-flow | Modal closes, no session created |
| EC-05 | Already logged-in visits homepage | Log In button replaced by user name |
| EC-06 | Send Code clicked twice | Cooldown timer resets or shows "Code already sent" |
| EC-07 | Phone too short (< 7 digits) | Send Code stays disabled |
| EC-08 | Network failure during OTP send | User-friendly error message shown |
| EC-09 | Switch Parent to Student tab mid-OTP-entry | Partially entered OTP is cleared, no stale session mixing |
| EC-10 | Child Login with wrong password (Child / wrongpass) | Inline error shown, no dashboard access |
| EC-11 | Child Login with SQL injection payload as username (' OR 1=1--) | Rejected as invalid credentials, no 500 error, no auth bypass |
| EC-12 | Child Login username field with XSS payload (<script>alert(1)</script>) | Input rendered as literal text, no script execution |
| EC-13 | Rapid-fire Send Code across Parent and Student tabs for the same phone number | Server-side rate limit triggers, no duplicate/overlapping OTP sessions |
| EC-14 | Direct navigation to `/en/child-login` while already authenticated as Parent/Student | Either redirects to that role's dashboard or shows Child login form without corrupting the existing session |

## Test Data
### Valid
| Field | Value |
|---|---|
| name | 98976564 |
| name | 123456 |
| name | +880 |
| name | Automations Student |
| name | 500000000 |
| name | 6789 |
| name | Child |
| name | 1234 |

### Invalid
| Field | Value |
|---|---|
| name | abc123 |
| name | 123 |
| name | 000000 |
| name | 12345 |
| name | ' OR 1=1-- |
| name | <script>alert(1)</script> |
| name | 501234567890123456789 |
| name |    501234567    |
