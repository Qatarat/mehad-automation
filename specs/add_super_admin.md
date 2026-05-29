# Page: Add Super Admin — Super Admin Dashboard

**URL:** `https://dev.mehadedu.com/en/super-admin-login`

## Description
Super admin management page. Existing super admins can add, view, and delete other super admin accounts. Includes full validation for name, email, phone, password, and timezone.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Super Admin section | `a:has-text("Super Admin"), [data-testid="super-admin-nav"]` | Required |
| Add Super Admin button | `button:has-text("Add Super Admin")` | Required |
| First name input | `input[name="firstName"], input[placeholder*="First Name"]` | Required |
| Last name input | `input[name="lastName"], input[placeholder*="Last Name"]` | Required |
| Email input | `input[type="email"]` | Required |
| Phone input | `input[type="tel"]` | Required |
| Password input | `input[type="password"]` | Required |
| Timezone selector | `select[name="timezone"], [placeholder*="Time Zone"]` | Required |
| Create button | `button:has-text("Create")` | Required |
| Super admin list table | `table, [data-testid="super-admin-list"]` | Required |
| Three dot menu | `button[aria-label*="actions"]` | Required |
| Delete option | `[role="menuitem"]:has-text("Delete")` | Optional |

## User Flows

### Flow 1: Add New Super Admin
1. Navigate to Super Admin Dashboard
2. Click "Super Admin" in sidebar
3. Click "Add Super Admin"
4. Fill First Name (max 32 chars)
5. Fill Last Name (max 32 chars)
6. Fill unique Email
7. Select country and fill Phone
8. Set Password
9. Select Timezone
10. Click "Create"
→ Expected: Super admin created, appears in list

### Flow 2: Delete Super Admin
1. Find super admin in list
2. Click three-dot menu
3. Click "Delete"
4. Confirm deletion
→ Expected: Deleted, removed from list, cannot login

## Requirements
- REQ-01: Super Admin list shows all super admins
- REQ-02: First/last name max 32 characters
- REQ-03: Email must be unique and valid format
- REQ-04: Password validates strength requirements
- REQ-05: Delete requires confirmation
- REQ-06: Deleted super admin cannot login

## Edge Cases
| EC-01 | Duplicate email | Error shown |
| EC-02 | Name over 32 chars | Validation error |
| EC-03 | Weak password | Validation error |
| EC-04 | Delete self | Should be prevented |

## Test Data
### Valid
| Field | Value |
|---|---|
| name | Super |
| name | Admin |
| name | superadmin@mehadedu.com |

### Invalid
| Field | Value |
|---|---|
| name | notanemail |
| name | 123 |
