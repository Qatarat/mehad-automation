# Page: Platform Fee Management

**URL:** `https://dev.mehadedu.com/en/dashboard/account-settings`

## Description
Super Admin manages the platform fee percentage deducted from tutor earnings per session. Fee updated from Account Settings. Applies globally to all tutors.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Account Settings link | `a:has-text("Account Settings"), [data-testid="account-settings"]` | Required |
| Platform Fee card | `:has-text("Platform Fee"), [data-testid="platform-fee-card"]` | Required |
| New Platform Fee input | `input[name="platformFee"], input[placeholder*="Platform Fee"]` | Required |
| Save Changes button | `button:has-text("Save Changes"), button:has-text("Save")` | Required |
| Success message | `:has-text("Platform Fee Updated Successfully")` | Conditional |

## User Flows

### Flow 1: Update Platform Fee
1. Login as super admin
2. Open sidebar
3. Navigate to Account Settings
4. Click "Platform Fee" card
5. Modal opens with New Platform Fee field
6. Enter new fee value (e.g., 10)
7. Click "Save Changes"
→ Expected: Success message, fee applied globally

### Flow 2: Verify Fee Deduction
1. Student books a session
2. Session completed
3. Navigate to tutor earnings
4. Platform fee deducted from session earning
→ Expected: Tutor earning = session price - platform fee

## Requirements
- REQ-01: Platform fee configurable from Account Settings
- REQ-02: Fee applies globally to all tutors
- REQ-03: Fee deducted from tutor earnings per session
- REQ-04: Save shows "Platform Fee Updated Successfully"
- REQ-05: Updated fee visible in tutor earnings breakdown

## Edge Cases
| EC-01 | Fee value negative | Validation error |
| EC-02 | Fee value over 100% | Validation error |
| EC-03 | Empty fee field | Validation error |
| EC-04 | Fee = 0 | Allowed, tutor gets full amount |

## Test Data
### Valid
| Field | Value |
|---|---|
| name | platform_fee_10 |
| name | platform_fee_15 |

### Invalid
| Field | Value |
|---|---|
| name | negative_fee |
| name | over_100_fee |
