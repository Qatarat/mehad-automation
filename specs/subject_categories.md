# Page: Subject Categories Management

**URL:** `https://dev.mehadedu.com/en/dashboard/subject-categories`

## Description
Super Admin manages subject categories used when creating subjects. Categories have Active/Disable status. Active categories appear in subject creation dropdowns. Categories can be reordered via drag toggle.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Subject Categories heading | `h1:has-text("Subject Categories"), h2:has-text("Categories")` | Required |
| Create Categories button | `button:has-text("Create Categories"), button:has-text("Create Category")` | Required |
| Search input | `input[placeholder*="Search"]` | Optional |
| Status filter | `select[aria-label*="Status"], [placeholder*="Active"]` | Optional |
| Category list | `table, [data-testid="categories-list"]` | Required |
| Category name | `.category-name, [data-testid="name"]` | Required |
| Status toggle | `[role="switch"], input[type="checkbox"]` | Required |
| Drag/sort toggle | `[data-testid="sort-handle"], button[aria-label*="sort"]` | Optional |
| Category name input | `input[name="name"], input[placeholder*="Category Name"]` | Required |
| Icon upload | `input[type="file"]` | Optional |
| Description textarea | `textarea[name="description"]` | Optional |
| Active toggle in form | `[role="switch"]` | Optional |
| Create Category button | `button:has-text("Create Category")` | Required |

## User Flows

### Flow 1: Create Subject Category
1. Navigate to Subject Categories
2. Click "Create Categories"
3. Fill Category Name (max 40 chars): Science
4. Upload icon (max 2 MB)
5. Fill description (max 500 chars)
6. Toggle Active
7. Click "Create Category"
8. Category appears in list

### Flow 2: Disable Category
1. Find category in list
2. Toggle status to Disable
3. Category no longer visible in Subject selection

### Flow 3: Reorder Categories
1. Use drag toggle to reorder
2. Updated order reflects in Subject creation dropdown

## Requirements
- REQ-01: Category name max 40 characters
- REQ-02: Icon upload max 2 MB
- REQ-03: Description max 500 characters
- REQ-04: Active categories appear in Subject creation
- REQ-05: Disabled categories hidden from Subject selection
- REQ-06: Sorting reflects in public order

## Edge Cases
| EC-01 | Name over 40 chars | Validation error |
| EC-02 | Icon file over 2 MB | Upload rejected |
| EC-03 | Description over 500 chars | Validation error |
| EC-04 | Disable used category | Subject still exists but category hidden |

## Test Data
### Valid
| Field | Value |
|---|---|
| name | Science |
| name | Mathematics |
| name | Literature |

### Invalid
| Field | Value |
|---|---|
| name | empty_name |
| name | name_over_forty_characters_long_invalid |
