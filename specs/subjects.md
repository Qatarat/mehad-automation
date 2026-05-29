# Page: Subjects Management

**URL:** `https://dev.mehadedu.com/en/dashboard/subjects`

## Description
Super Admin manages subjects used platform-wide (tutor profiles, search, booking, enrollment). Subjects have Active/Disable status and Featured flag for landing page display. Supports English and Arabic names.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Subjects heading | `h1:has-text("Subjects"), h2:has-text("Subjects")` | Required |
| Create Subject button | `button:has-text("Create Subject")` | Required |
| Search input | `input[placeholder*="Search Subject"]` | Optional |
| Status filter | `select[aria-label*="Status"]` | Optional |
| Subjects table | `table, [data-testid="subjects-table"]` | Required |
| Subject name | `.subject-name, [data-testid="subject-name"]` | Required |
| Status toggle | `[role="switch"]` | Required |
| Featured toggle | `[role="switch"][aria-label*="featured"]` | Optional |
| Logo upload | `input[type="file"]` | Optional |
| Category select | `select[name="category"], [placeholder*="Category"]` | Required |
| Subject name input | `input[name="name"], input[placeholder*="Subject Name"]` | Required |
| Arabic name input | `input[name="nameAr"], input[placeholder*="Arabic"]` | Optional |
| Description textarea | `textarea[name="description"]` | Optional |
| Create Subject button modal | `[role="dialog"] button:has-text("Create Subject")` | Required |

## User Flows

### Flow 1: Create Subject
1. Navigate to Subjects management
2. Click "Create Subject"
3. Upload logo (max 10 MB)
4. Select category
5. Fill Subject Name (max 32 chars): Mathematics
6. Fill Arabic Name: الرياضيات
7. Fill description (max 500 chars)
8. Click "Create Subject"
9. Subject appears in list

### Flow 2: Toggle Featured Subject
1. Find subject in list
2. Toggle Featured to ON
3. Subject appears on landing page
4. Toggle Featured to OFF
5. Subject removed from featured section

### Flow 3: Disable Subject
1. Find subject
2. Toggle Status to Disable
3. Subject not visible in tutor profile selection or search filters

## Requirements
- REQ-01: Subject name max 32 characters
- REQ-02: Logo upload max 10 MB
- REQ-03: Description max 500 characters
- REQ-04: Category selection required
- REQ-05: Active subjects available on tutor profile, search, booking
- REQ-06: Featured subjects appear on landing page
- REQ-07: Arabic name used when language switched to Arabic

## Edge Cases
| EC-01 | Subject name over 32 chars | Validation error |
| EC-02 | Logo over 10 MB | Upload rejected |
| EC-03 | Description over 500 chars | Validation error |
| EC-04 | Disable subject in active use | Tutors with this subject retain it but new selection blocked |
| EC-05 | Empty required fields | Validation error |

## Test Data
### Valid
| Field | Value |
|---|---|
| name | Mathematics |
| name | Physics |
| name | Chemistry |

### Invalid
| Field | Value |
|---|---|
| name | empty_name |
| name | name_over_thirtytwo_chars_invalid_test |
