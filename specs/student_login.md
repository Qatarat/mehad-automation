# Page: Student Login — WhatsApp OTP Authentication

**URL:** `https://dev.mehadedu.com/en`

## Description
Student authentication via WhatsApp OTP modal. Students click "Log In" in the header, select country code +880, enter phone 98976564, receive OTP, and authenticate.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Log In button | `button:has-text("Log In")` | Required |
| Login dialog | `[role="dialog"]` | Required |
| Welcome heading | `[role="dialog"] h2` | Required |
| Country code selector | `[role="dialog"] button:has-text("+966")` | Required |
| Country search input | `[role="dialog"] input[placeholder="Search..."]` | Conditional |
| Phone input | `[role="dialog"] input[type="tel"]` | Required |
| Send Code button | `[role="dialog"] button:has-text("Send Code")` | Required |
| OTP input | `[role="dialog"] input[autocomplete="one-time-code"]` | Required |
| Continue button | `[role="dialog"] button:has-text("Continue")` | Required |
| Resend timer text | `[role="dialog"] :has-text("Resend in")` | Conditional |
| Change number link | `[role="dialog"] button:has-text("Change Mobile Number")` | Conditional |
| Close button | `[role="dialog"] button[aria-label="Close"]` | Optional |

## User Flows

### Flow 1: Complete Student Login
1. Navigate to https://dev.mehadedu.com/en
2. Click "Log In" button in header
3. Dialog opens with heading "Welcome back"
4. Click country code button showing "+966"
5. Type "Bangladesh" in search field
6. Select "+880 Bangladesh" option
7. Fill phone input with 98976564
8. Click "Send Code" button
9. Fill OTP input with 123456
10. Click "Continue"
→ Expected: Dialog closes, user authenticated, header shows user name

### Flow 2: Wrong OTP Rejected
1. Navigate to homepage and open login modal
2. Select country +880, enter phone 98976564
3. Click Send Code
4. Enter wrong OTP 000000
5. Click Continue
→ Expected: Error message displayed, modal stays open

### Flow 3: Change Phone Number
1. Open login modal
2. Select country +880, enter phone 98976564
3. Click Send Code
4. Click "Change Mobile Number"
→ Expected: Returns to phone entry step

## Requirements
- REQ-01: Log In button must be visible in unauthenticated header
- REQ-02: Dialog must open with role="dialog" and heading "Welcome back"
- REQ-03: Country code defaults to +966, can be changed to +880
- REQ-04: Phone input is type="tel" and accepts only numeric input
- REQ-05: Send Code is disabled when phone field is empty
- REQ-06: OTP input is disabled until Send Code is successfully clicked
- REQ-07: OTP field accepts exactly 6 digits with maxlength="6"
- REQ-08: Continue triggers authentication
- REQ-09: Successful login closes modal and shows user name in header
- REQ-10: Failed OTP shows error without full page reload

## Edge Cases
| EC-01 | Empty phone submitted | Send Code stays disabled |
| EC-02 | Non-numeric phone characters | Characters rejected |
| EC-03 | Wrong OTP 000000 | Error message displayed |
| EC-04 | Phone too short (3 digits) | Send Code stays disabled |
| EC-05 | Modal closed before completing | No session created |
| EC-06 | Rapid double-click Continue | Only one auth attempt |
| EC-07 | Network error during Send Code | User-friendly error shown |
| EC-08 | OTP entered before Send Code click | OTP field remains disabled |

## Test Data
### Valid
| Field | Value |
|---|---|
| name | 98976564 |
| name | 123456 |
| name | +880 |

### Invalid
| Field | Value |
|---|---|
| name | abc123 |
| name | 123 |
| name | 000000 |
