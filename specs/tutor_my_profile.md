# Page: Tutor My Profile

**URL:** `https://dev.mehadedu.com/en/dashboard/profile`

## Description
Tutor profile editing page. Tutors can update their publicly displayed name, email, phone, and display name. Changes save immediately without admin approval for basic info.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| My Profile option | `button:has-text("My Profile"), a:has-text("My Profile")` | Required |
| Edit Profile button | `button:has-text("Edit Profile")` | Required |
| First name input | `input[name="firstName"], input[placeholder*="First"]` | Required |
| Last name input | `input[name="lastName"], input[placeholder*="Last"]` | Required |
| Display name input | `input[name="displayName"], input[placeholder*="Display"]` | Optional |
| Email input | `input[type="email"]` | Required |
| Phone input | `input[type="tel"]` | Optional |
| Country code button | `[aria-label="Country code"], button:has-text("+")` | Optional |
| Save button | `button:has-text("Save"), button[type="submit"]` | Required |
| Profile avatar | `img[alt*="profile"], .avatar` | Optional |

## User Flows

### Flow 1: Edit Profile Information
1. Log in as tutor (phone 98976564, OTP 123456)
2. Click tutor avatar at bottom of sidebar
3. Click "My Profile" from popup
4. Click "Edit Profile"
5. Update first name, last name, or email
6. Click "Save"
→ Expected: Changes saved, profile updated immediately

### Flow 2: Update Phone Number
1. Navigate to My Profile
2. Click Edit Profile
3. Click country code button, select +880
4. Update phone number
5. Click Save
→ Expected: Phone number updated

## Requirements
- REQ-01: Profile accessible from sidebar avatar popup
- REQ-02: First name, last name, display name fields editable
- REQ-03: Email field validates format
- REQ-04: Phone field validates number format
- REQ-05: Save updates profile immediately
- REQ-06: Changes do not require admin approval for basic info

## Edge Cases
| EC-01 | Invalid email format | Validation error shown |
| EC-02 | Empty first name | Validation error shown |
| EC-03 | Phone number invalid | Validation error shown |
| EC-04 | First name over 30 chars | Truncated or blocked |

## Test Data
### Valid
| Field | Value |
|---|---|
| name | 98976564 |
| name | 123456 |
| name | testtutor@mehadedu.com |
| name | TestTutor |

### Invalid
| Field | Value |
|---|---|
| name | notanemail |
| name | (empty) |
