# Page: Super Admin 2FA Number Update

**URL:** `https://dev.mehadedu.com/en/super-admin-login`

## Description
Super Admin login via WhatsApp OTP and 2FA number update. The super admin can update their 2FA phone number from Account Settings. New number takes effect on next login.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Super admin login heading | `h1:has-text("Super Admin"), h2:has-text("Super Admin Login")` | Required |
| Country code selector | `button:has-text("+966"), [aria-label="Country code"]` | Required |
| Phone input | `input[type="tel"]` | Required |
| Send Code button | `button:has-text("Send Code")` | Required |
| OTP input | `input[autocomplete="one-time-code"], input[placeholder="000000"]` | Required |
| Continue/Verify button | `button:has-text("Continue"), button:has-text("Verify")` | Required |
| Account Settings link | `a:has-text("Account Settings"), [data-testid="account-settings"]` | Required |
| 2FA Number card | `:has-text("2FA Number"), [data-testid="2fa-card"]` | Required |
| New country code selector | `[aria-label="Country code"]` | Required |
| New phone input | `input[type="tel"]` | Required |
| Send Verification Code button | `button:has-text("Send Verification Code")` | Required |
| New OTP input | `input[autocomplete="one-time-code"]` | Required |
| Save/Update button | `button:has-text("Save"), button:has-text("Update")` | Required |

## User Flows

### Flow 1: Super Admin Login
1. Navigate to https://dev.mehadedu.com/en/super-admin-login
2. Select country code
3. Enter valid phone number
4. Click "Send Code"
5. Enter OTP
6. Click "Continue"
→ Expected: Super admin dashboard loads

### Flow 2: Update 2FA Number
1. Login as super admin
2. Open sidebar
3. Navigate to Account Settings
4. Open "2FA Number" card
5. Select new country code
6. Enter new valid WhatsApp number
7. Click "Send Verification Code"
8. Enter received OTP
9. After verification, number is updated
→ Expected: New 2FA number saved, used on next login

## Requirements
- REQ-01: Super admin login page available at /en/super-admin-login
- REQ-02: OTP login flow same as student/tutor
- REQ-03: Account Settings accessible from sidebar
- REQ-04: 2FA Number card shows current number
- REQ-05: New number requires OTP verification before saving
- REQ-06: Updated number used for login from next session

## Edge Cases
| EC-01 | Invalid new phone number | Validation error shown |
| EC-02 | Wrong verification OTP | Error shown, number not updated |
| EC-03 | Same number entered | System may allow or show warning |
| EC-04 | Network error during update | Error shown, previous number retained |

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
| name | 000000 |
