# Page: Super Admin Login and Reset Password

**URL:** `https://dev.mehadedu.com/en/super-admin-login`

## Description
Super Admin login via WhatsApp number and password, plus forgot password flow via OTP. After login, admin accesses the full management dashboard.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Super admin login heading | `h1:has-text("Super Admin"), h2:has-text("Super Admin Login")` | Required |
| Country code selector | `[aria-label="Country code"], button:has-text("+966")` | Required |
| Phone/WhatsApp input | `input[type="tel"]` | Required |
| Password input | `input[type="password"]` | Required |
| Continue button | `button:has-text("Continue"), button[type="submit"]` | Required |
| Forgot Password link | `a:has-text("Forgot Password"), button:has-text("Forgot Password")` | Optional |
| Send OTP button | `button:has-text("Send OTP"), button:has-text("Send Code")` | Conditional |
| OTP input | `input[autocomplete="one-time-code"], input[placeholder="000000"]` | Conditional |
| Verify button | `button:has-text("Verify")` | Conditional |
| New password input | `input[name="newPassword"], input[placeholder*="New Password"]` | Conditional |
| Confirm password input | `input[name="confirmPassword"], input[placeholder*="Confirm"]` | Conditional |
| Reset button | `button:has-text("Reset")` | Conditional |

## User Flows

### Flow 1: Super Admin Login
1. Navigate to https://dev.mehadedu.com/en/super-admin-login
2. Select country code
3. Enter valid WhatsApp number
4. Enter password
5. Click "Continue"
→ Expected: Dashboard loads after successful login

### Flow 2: Forgot Password
1. Navigate to super admin login
2. Click "Forgot Password"
3. Select country code, enter registered number
4. Click "Send OTP"
5. Enter OTP
6. Click "Verify"
7. Enter new password
8. Enter confirm password (must match)
9. Click "Reset"
→ Expected: Password reset, can login with new password

## Requirements
- REQ-01: Super admin login page at /en/super-admin-login
- REQ-02: Phone number validates by country code (max 12 digits)
- REQ-03: Password field is masked
- REQ-04: Invalid credentials show error message
- REQ-05: Forgot password sends OTP to registered number
- REQ-06: New password must differ from old password
- REQ-07: Confirm password must match new password
- REQ-08: Old password does not work after reset

## Edge Cases
| EC-01 | Wrong password | Error message shown |
| EC-02 | Invalid phone number | Validation error |
| EC-03 | Wrong OTP in reset | Error shown |
| EC-04 | Passwords do not match | Validation error |
| EC-05 | New password same as old | Error shown |

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
| name | abc |
| name | 000000 |
| name | 123 |
