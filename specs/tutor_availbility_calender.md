# Page: Tutor Availability Calendar

**URL:** `https://dev.mehadedu.com/en/dashboard/availability`

## Description
Tutor's availability management page. Tutors create 1-to-1 availability slots and group sessions from here. Group session creation is a 3-page modal; 1-to-1 uses "Add Availability Time" button.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Availability Calendar heading | `h1:has-text("Availability"), h2:has-text("Availability")` | Required |
| Add Availability Time button | `button:has-text("Add Availability Time")` | Required — 1-to-1 |
| Group Session button | `button:has-text("Group Session"), button:has-text("Group session")` | Required |
| Start Date input | `input[placeholder*="Start Date"], [aria-label*="Start Date"]` | Required in modal |
| End Date input | `input[placeholder*="End Date"], [aria-label*="End Date"]` | Required in modal |
| Day selector buttons | `button:has-text("Mo"), button:has-text("Tu"), button:has-text("We")` | Required |
| Start Time input | `input[placeholder*="Start Time"], [aria-label*="Start Time"]` | Required |
| End Time input | `input[placeholder*="End Time"], [aria-label*="End Time"]` | Required |
| Next button | `button:has-text("Next")` | Required in modal |
| Apply button | `button:has-text("Apply")` | Required — 1-to-1 modal |
| Course Name input | `input[placeholder*="Course Name"], input[name*="course"]` | Required — Group step 2 |
| Maximum Students input | `input[placeholder*="Maximum"], input[name*="maxStudents"]` | Required — Group step 2 |
| Minimum Students input | `input[placeholder*="Minimum"], input[name*="minStudents"]` | Required — Group step 2 |
| Price Per Student input | `input[placeholder*="Price"], input[name*="price"]` | Required — Group step 2 |
| Create Group Session button | `button:has-text("Create Group Session")` | Required — Group step 3 |
| Modal container | `[role="dialog"], .modal` | Conditional |

## User Flows

### Flow 1: Create Group Session (3-page modal)
1. Navigate to https://dev.mehadedu.com/en/dashboard/availability
2. Click "Group Session" button
3. Modal page 1 opens
4. Click Start Date and select date
5. Click End Date and select end date
6. Select applicable day(s) (Sa, Su, Mo, Tu, etc.)
7. Set Start Time (at least 30 min before current time)
8. Set End Time
9. Click "Next"
10. Modal page 2: Fill Course Name: "Basic Math course"
11. Fill Maximum Students: 10
12. Fill Minimum Students: 2
13. Fill Price Per Student: 100
14. Click "Next"
15. Modal page 3: Review all details
16. Click "Create Group Session"
→ Expected: Group session created, appears in session list

### Flow 2: Create 1-to-1 Availability
1. Navigate to availability calendar
2. Click "Add Availability Time"
3. Modal opens with date and time fields
4. Select Start Date
5. Select End Date
6. Select day(s)
7. Set Start Time
8. Set End Time
9. Click "Apply"
→ Expected: Availability slot created, shown in calendar

### Flow 3: View Existing Sessions
1. Navigate to availability calendar
2. Page shows existing availability slots and group sessions
→ Expected: Calendar shows scheduled slots

## Requirements
- REQ-01: Availability calendar page loads for authenticated tutors
- REQ-02: "Add Availability Time" button is visible and clickable
- REQ-03: "Group Session" button is visible and clickable
- REQ-04: Group session modal has 3 pages/steps
- REQ-05: Start time must be set at least 30 minutes before current time
- REQ-06: End date must be after or equal to start date
- REQ-07: Course name is required for group sessions
- REQ-08: Maximum students must be greater than minimum students
- REQ-09: Price per student must be a positive number
- REQ-10: Session creation shows confirmation and closes modal

## Edge Cases
| EC-01 | End date before start date | Validation error shown |
| EC-02 | No days selected in modal | Next button disabled or error |
| EC-03 | Minimum students >= maximum students | Validation error |
| EC-04 | Price of 0 | Validation error or warning |
| EC-05 | Start time in the past | Validation error shown |
| EC-06 | Empty course name | Required field error |
| EC-07 | Maximum students = 0 | Validation error |
| EC-08 | Modal closed mid-creation | No partial session created |

## Test Data
### Valid
| Field | Value |
|---|---|
| name | Basic Math course |
| name | 10 |
| name | 2 |
| name | 100 |
| name | 98976564 |
| name | 123456 |

### Invalid
| Field | Value |
|---|---|
| name | 15 (greater than max) |
| name | -1 |
| name | (empty) |
