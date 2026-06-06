# Page: Session — Join Classroom

**URL:** `https://dev.mehadedu.com/en/dashboard/sessions`

## Description
Session management for both tutors and students. Shows session details, join classroom workflow at scheduled time, and session history. Auto-closes when session end time is reached.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Sessions heading | `h1:has-text("Sessions"), h2:has-text("Session")` | Required |
| Upcoming sessions | `:has-text("Upcoming"), [data-tab="upcoming"]` | Required |
| Session card | `.session-card, [data-testid="session-card"]` | Required |
| Tutor name in card | `.tutor-name, [data-testid="tutor-name"]` | Required |
| Student name in card | `.student-name, [data-testid="student-name"]` | Required |
| Session type badge | `.session-type, :has-text("1-to-1"), :has-text("Group")` | Required |
| Session date-time | `time, .session-time, [data-testid="session-time"]` | Required |
| Join Classroom button | `button:has-text("Join Classroom")` | Conditional — at session time |
| Join modal | `[role="dialog"]:has-text("Join Classroom")` | Conditional |
| Join Classroom confirm | `[role="dialog"] button:has-text("Join Classroom")` | Conditional |
| Session status | `.status-badge, [data-testid="status"]` | Required |
| Search box | `input[placeholder*="Search"], input[type="search"]` | Optional |
| Status filter | `select[aria-label*="Status"], [placeholder*="All Status"]` | Optional |
| Type filter | `select[aria-label*="Type"], [placeholder*="All Types"]` | Optional |

## User Flows

### Flow 1: Join Classroom at Session Time
1. Navigate to /en/dashboard/sessions or My Bookings
2. Find session with current scheduled time
3. "Join Classroom" button appears
4. Click "Join Classroom"
5. Confirmation modal opens
6. Click "Join Classroom" in modal
→ Expected: Classroom starts, participants can interact

### Flow 2: Session Auto-Closes at End Time
1. Join a classroom session
2. Wait for session end time
3. Classroom auto-closes
→ Expected: Session marked as completed

### Flow 3: View Completed Sessions (History)
1. Navigate to session history
2. View past sessions with status
→ Expected: Completed sessions listed with details

## Requirements
- REQ-01: Sessions page shows upcoming and past sessions
- REQ-02: Each session shows tutor name, student name, subject, type, status, price, date-time
- REQ-03: Join Classroom button appears only at scheduled session time
- REQ-04: Clicking Join Classroom opens confirmation modal
- REQ-05: Session automatically closes when end time is reached
- REQ-06: Completed sessions appear in session history
- REQ-07: Search functionality filters by tutor/student/subject name
- REQ-08: Status filter shows Pending, Completed, Cancelled
- REQ-09: Type filter shows 1-to-1 and Group Session options

## Edge Cases
| EC-01 | Join before session time | Join button not visible — automation always validates this since sessions are booked for future dates |
| EC-02 | Session end time reached | Auto-close triggers |
| EC-03 | Search with invalid name | Empty results shown |
| EC-04 | Filter Cancelled sessions | Only cancelled sessions shown |
| EC-05 | Filter Group sessions | Only group sessions shown |
| EC-06 | Session cancelled mid-join | Error handled gracefully |

## Automation Notes
- Don't test the actual Join Classroom click flow in automated smoke/regression runs — it requires real-time session presence and is covered by xfail in tests/test_live_session_superadmin.py.
- Session History tab accessibility IS tested: see TBS-06 and TestTeacherSessionHistory.
- Slots are intentionally created for future dates; see TestSlotFutureDates for the date contract.

## Test Data
### Valid
| Field | Value |
|---|---|
| name | 98976564 |
| name | 123456 |
| name | group |
| name | 1-to-1 |

### Invalid
| Field | Value |
|---|---|
| name | <script>alert(1)</script> |
