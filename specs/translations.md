# Page: Translation Management — Super Admin

**URL:** `https://dev.mehadedu.com/en/dashboard/translations`

## Description
Dynamic localization system for Super Admins. Manages key-value translations for English and Arabic across Admin, Student, Tutor, and Public roles. Changes apply platform-wide in real time.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Translation Management link | `a:has-text("Translation"), [data-testid="translation-nav"]` | Required |
| Translations heading | `h1:has-text("Translation"), h2:has-text("Translations")` | Required |
| Search input | `input[placeholder*="Search by Key"], input[placeholder*="Search"]` | Optional |
| Language filter | `select[aria-label*="Language"], [placeholder*="English"]` | Optional |
| App/Role filter | `select[aria-label*="App"], [placeholder*="Admin"]` | Optional |
| Group filter | `select[aria-label*="Group"]` | Optional |
| Clear filters button | `button:has-text("Clear"), button:has-text("Reset")` | Optional |
| Translations table | `table, [data-testid="translations-table"]` | Required |
| Create Translation button | `button:has-text("Create Translation")` | Required |
| Key input | `input[name="key"], input[placeholder*="Key"]` | Required |
| English value input | `input[name="enValue"], textarea[name="en"]` | Required |
| Arabic value input | `input[name="arValue"], textarea[name="ar"]` | Optional |
| App select | `select[name="app"]` | Required |
| Group select | `select[name="group"]` | Required |
| Edit option | `[role="menuitem"]:has-text("Edit")` | Optional |
| Delete option | `[role="menuitem"]:has-text("Delete")` | Optional |

## User Flows

### Flow 1: Create Translation
1. Navigate to Translation Management
2. Click "Create Translation"
3. Select Language: English
4. Select App: Student
5. Select Group: General
6. Enter Key: welcome_message
7. Enter English value: Welcome to Mehad
8. Enter Arabic value: مرحباً بكم
9. Click "Create Translation"
10. Translation active across system

### Flow 2: Filter Translations
1. Select Language filter: Arabic
2. Only Arabic translations shown
3. Select App: Tutor
4. Only tutor-role translations shown

### Flow 3: Edit Translation
1. Find translation in table
2. Click Edit
3. Update English or Arabic value
4. Save
5. Platform reflects updated text

## Requirements
- REQ-01: Translation module accessible from Account Settings
- REQ-02: Key-value pairs support English and Arabic
- REQ-03: Role-based: Admin, Student, Tutor, Public
- REQ-04: Group-based organization
- REQ-05: Search by key or value works
- REQ-06: Edit saves and applies immediately
- REQ-07: Delete removes translation from system

## Edge Cases
| EC-01 | Empty key | Validation error |
| EC-02 | Duplicate key for same role/group | Error or override |
| EC-03 | Delete used translation | UI shows key or fallback |
| EC-04 | Search with no match | Empty results |

## Test Data
### Valid
| Field | Value |
|---|---|
| name | welcome_message |
| name | login_button |
| name | book_session |

### Invalid
| Field | Value |
|---|---|
| name | empty_key |
| name | duplicate_key |
