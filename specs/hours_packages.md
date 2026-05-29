# Page: Hours Packages Management

**URL:** `https://dev.mehadedu.com/en/dashboard/packages`

## Description
Super Admin manages hour packages for 1-to-1 session booking. Packages define duration (hours), discount percentage, and active/disabled visibility. Students must purchase a package before booking 1-to-1 slots.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Packages heading | `h1:has-text("Packages"), h2:has-text("Packages")` | Required |
| Create Package button | `button:has-text("Create Package")` | Required |
| Search Package input | `input[placeholder*="Search Package"], input[placeholder*="Search"]` | Optional |
| Package list table | `table, [data-testid="package-list"]` | Required |
| Package name | `.package-name, [data-testid="package-name"]` | Required |
| Package status toggle | `[role="switch"], input[type="checkbox"]` | Required |
| Action button | `button[aria-label*="actions"], button:has-text("Action")` | Required |
| Edit Package option | `[role="menuitem"]:has-text("Edit Package")` | Optional |
| Package name input | `input[name="name"], input[placeholder*="Package Name"]` | Required in modal |
| Duration select | `select[name="duration"], [placeholder*="Duration"]` | Required in modal |
| Percentage input | `input[name="percentage"], input[placeholder*="Percentage"]` | Required in modal |
| Create/Save button | `button:has-text("Create Package"), button:has-text("Save")` | Required |

## User Flows

### Flow 1: Create a Package
1. Navigate to Packages management
2. Click "Create Package"
3. Fill Package Name (max 100 chars): Starter Pack
4. Select Duration: 5 hours
5. Enter Percentage discount: 10
6. Click "Create Package"
→ Expected: Package created, visible to students

### Flow 2: Edit a Package
1. Find package in list
2. Click "Action" button
3. Click "Edit Package"
4. Update duration or percentage
5. Click "Save"
→ Expected: Package updated publicly

### Flow 3: Toggle Package Visibility
1. Find package in list
2. Click status toggle to change Active/Disable
→ Expected: Package visibility changes immediately

### Flow 4: Search Package
1. Type package name in search input
2. Matching packages shown
→ Expected: Filtered list displayed

## Requirements
- REQ-01: Packages page accessible from Admin Settings
- REQ-02: Package name max 100 characters
- REQ-03: Active packages visible to students
- REQ-04: Disabled packages hidden from students
- REQ-05: Edit saves duration and discount correctly
- REQ-06: Search returns correct matching packages
- REQ-07: Students can purchase active packages

## Edge Cases
| EC-01 | Package name over 100 chars | Validation error |
| EC-02 | Percentage over 100 | Validation error |
| EC-03 | Negative percentage | Validation error |
| EC-04 | Disable active package | Students cannot see it |
| EC-05 | Search with no match | Empty state shown |

## Test Data
### Valid
| Field | Value |
|---|---|
| name | Starter Pack |
| name | Premium Pack |
| name | Basic Pack |

### Invalid
| Field | Value |
|---|---|
| name | empty_name |
| name | negative_percentage |
