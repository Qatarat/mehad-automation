# Page: Student Profile Settings

**URL:** `https://dev.mehadedu.com/en/dashboard/settings`

## Description
Student account settings page. Students can update display name, email, phone, profile picture, and preferences. Accessible from profile icon sidebar.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Settings heading | `h1:has-text("Settings"), h2:has-text("Profile")` | Required |
| Edit Profile button | `button:has-text("Edit Profile")` | Required |
| Display name input | `input[name="displayName"], input[placeholder*="Display Name"]` | Required |
| Email input | `input[type="email"]` | Optional |
| Phone display field | `input[name="phone"], :has-text("98976564")` | Optional |
| Profile picture upload | `input[type="file"]` | Optional |
| Save Changes button | `button:has-text("Save Changes"), button:has-text("Save")` | Required |
| Location field | `input[name="location"], input[placeholder*="Location"]` | Optional |
| Join date display | `:has-text("Joined"), .join-date` | Optional |

## User Flows

### Flow 1: Update Display Name
1. Navigate to https://dev.mehadedu.com/en/dashboard/settings
2. Click "Edit Profile"
3. Update display name field
4. Click "Save Changes"
→ Expected: Name updated, success toast shown

### Flow 2: Upload Profile Picture
1. Navigate to settings
2. Click profile picture area
3. Select image file
4. Upload processes
→ Expected: Profile picture updated

### Flow 3: View Profile Information
1. Navigate to settings
2. Page shows email, phone, location, join date
→ Expected: Correct student information displayed

## Requirements
- REQ-01: Settings page accessible to authenticated students
- REQ-02: Display name field is editable
- REQ-03: Save Changes persists updates
- REQ-04: Phone number shown (read-only)
- REQ-05: Email field validates format
- REQ-06: Profile picture upload accepts images only

## Edge Cases
| EC-01 | Name field empty on save | Validation error shown |
| EC-02 | Invalid email format | Validation error shown |
| EC-03 | Non-image file for avatar | Upload rejected |
| EC-04 | XSS in name field | Input sanitized |
| EC-05 | Name over max length | Truncated or blocked |
| EC-06 | Unauthenticated access to settings | Redirects to login |

## Test Data
### Valid
| Field | Value |
|---|---|
| name | 98976564 |
| name | 123456 |
| name | Updated Student |
| name | test@mehadedu.com |

### Invalid
| Field | Value |
|---|---|
| name | (empty) |
| name | notanemail |
| name | <script>alert(1)</script> |
