# Page: Reset Password — Super Admin Account Settings

**URL:** `https://dev.mehadedu.com/en/dashboard/account-settings`

## Description
Super Admin password reset from Account Settings. Admin enters new password and confirms it. After reset, old password becomes invalid and new password required for login.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Account Settings link | `a:has-text("Account Settings"), [data-testid="account-settings"]` | Required |
| Reset Password card | `:has-text("Reset Password"), [data-testid="reset-password-card"]` | Required |
| New password input | `input[type="password"][name="newPassword"], input[placeholder*="New Password"]` | Required |
| Show password toggle | `button[aria-label*="show"], button[aria-label*="eye"]` | Optional |
| Confirm password input | `input[type="password"][name="confirmPassword"], input[placeholder*="Confirm"]` | Required |
| Reset Password button | `button:has-text("Reset Password"), button[type="submit"]` | Required |
| Success message | `:has-text("Password"), :has-text("updated"), :has-text("reset")` | Conditional |

## User Flows

### Flow 1: Reset Password Successfully
1. Login as super admin
2. Navigate to Account Settings
3. Click "Reset Password" card
4. Modal opens with new password fields
5. Enter new strong password
6. Enter same password in confirm field
7. Click "Reset Password"
8. Success message shown
9. Old password no longer works
10. New password required for next login

### Flow 2: Password Mismatch
1. Enter new password: NewPass@123
2. Enter confirm: DifferentPass@123
3. Click "Reset Password"
4. Error: passwords do not match

## Requirements
- REQ-01: Reset Password accessible from Account Settings
- REQ-02: New password must be strong
- REQ-03: Confirm password must match new password
- REQ-04: Old password becomes invalid after reset
- REQ-05: Eye icon toggles password visibility
- REQ-06: Success message shown after reset

## Edge Cases
| EC-01 | Passwords do not match | Error shown |
| EC-02 | Weak password | Validation error |
| EC-03 | Same as old password | Error: must be unique |
| EC-04 | Empty new password field | Validation error |
| EC-05 | Empty confirm password | Validation error |

## Test Data
### Valid
| Field | Value |
|---|---|
| name | NewSecure@Pass123 |
| name | StrongPass@456 |

### Invalid
| Field | Value |
|---|---|
| name | weakpassword |
| name | mismatch_confirm |
