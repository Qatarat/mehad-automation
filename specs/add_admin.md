# Page: Add Admin — Super Admin Dashboard

**URL:** `https://dev.mehadedu.com/en/super-admin-login`

## Description
Admin management page in the Super Admin dashboard. Super admins can view, add, and delete admin users. Includes name, email, phone, role, and status management.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Admin section link | `a:has-text("Admin"), [data-testid="admin-nav"]` | Required |
| Admin list table | `table, [data-testid="admin-list"]` | Required |
| Add Admin button | `button:has-text("Add Admin")` | Required |
| First name input | `input[name="firstName"], input[placeholder*="First Name"]` | Required |
| Last name input | `input[name="lastName"], input[placeholder*="Last Name"]` | Required |
| Email input | `input[type="email"]` | Required |
| Phone input | `input[type="tel"]` | Required |
| Country code selector | `[aria-label="Country code"], button:has-text("+")` | Required |
| Timezone selector | `select[name="timezone"], [placeholder*="Time Zone"]` | Required |
| Create button | `button:has-text("Create")` | Required |
| Three dot menu | `button[aria-label*="actions"], button:has-text("...")` | Required |
| View option | `[role="menuitem"]:has-text("View")` | Optional |
| Delete option | `[role="menuitem"]:has-text("Delete")` | Optional |
| Delete confirmation | `[role="dialog"] button:has-text("Confirm"), [role="dialog"] button:has-text("Delete")` | Conditional |

## User Flows

### Flow 1: Add New Admin
1. Navigate to Super Admin Dashboard
2. Click "Admin" in sidebar
3. Click "Add Admin"
4. Fill First Name (max 32 chars)
5. Fill Last Name (max 32 chars)
6. Fill valid Email
7. Select country code and fill Phone
8. Select Timezone
9. Click "Create"
→ Expected: Admin created, appears in list with success message

### Flow 2: View Admin Profile
1. Find admin in list
2. Click three-dot action menu
3. Click "View"
4. Profile details shown
→ Expected: All admin details displayed correctly

### Flow 3: Delete Admin
1. Find admin in list
2. Click three-dot menu
3. Click "Delete"
4. Confirmation modal appears
5. Click "Confirm"
→ Expected: Admin deleted, removed from list

## Requirements
- REQ-01: Admin list shows all admins with name, email, phone, role, status, dates
- REQ-02: First name and last name max 32 characters each
- REQ-03: Email must be valid format and unique
- REQ-04: Phone number validates by country code
- REQ-05: Create button creates admin and shows success
- REQ-06: Delete requires confirmation modal
- REQ-07: Deleted admin cannot login

## Edge Cases
| EC-01 | First name over 32 chars | Validation error shown |
| EC-02 | Duplicate email | Error: email already exists |
| EC-03 | Invalid email format | Validation error |
| EC-04 | Empty required fields | Validation errors shown |
| EC-05 | Delete own super admin account | Should be prevented |

## Test Data
### Valid
| Field | Value |
|---|---|
| name | Test |
| name | Admin |
| name | testadmin@mehadedu.com |
| name | 98976564 |

### Invalid
| Field | Value |
|---|---|
| name | notanemail |
| name | AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA (over 32) |
