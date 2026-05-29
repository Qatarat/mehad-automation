# Page: Tutor Group Session Management

**URL:** `https://dev.mehadedu.com/en/dashboard/group-sessions`

## Description
Tutor's group session management page. Shows all created group sessions with Manage and Edit options. Tutors can view enrollment, attendance, and revenue. Edit is only available before any student enrolls.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Group Sessions heading | `h1:has-text("Group"), h2:has-text("Group Session")` | Required |
| Session card | `.session-card, [data-testid="session-card"]` | Required — per session |
| Manage button | `button:has-text("Manage")` | Required — per session |
| Edit button | `button:has-text("Edit")` | Conditional — only before enrollment |
| Class tab | `[role="tab"]:has-text("Class")` | Required in manage view |
| Student tab | `[role="tab"]:has-text("Student")` | Required in manage view |
| Session schedule | `:has-text("Schedule"), .schedule-info` | Required |
| Enrolled students count | `:has-text("Students"), .student-count` | Required |
| Available seats | `:has-text("seats"), .seats-available` | Required |
| Revenue section | `:has-text("Revenue"), .revenue-info` | Conditional |
| Join Classroom button | `button:has-text("Join Classroom")` | Conditional — at session time |

## User Flows

### Flow 1: View Group Sessions List
1. Navigate to https://dev.mehadedu.com/en/dashboard/group-sessions
2. Page shows list of created group sessions
3. Each session shows course name, schedule, enrolled count
→ Expected: All group sessions listed correctly

### Flow 2: Manage a Group Session
1. Click "Manage" button on a session card
2. Session details page opens
3. Click "Class" tab to see schedule
4. Click "Student" tab to see enrolled students
→ Expected: Session details and student list shown

### Flow 3: Edit a Group Session (Before Enrollment)
1. Find a session with 0 enrollments
2. Click "Edit" button
3. Update session details
4. Save changes
→ Expected: Session updated successfully

### Flow 4: Join Classroom at Session Time
1. Navigate to group sessions
2. Wait until scheduled session time
3. "Join Classroom" button appears
4. Click "Join Classroom"
5. Confirmation modal opens
6. Click "Join Classroom" in modal
→ Expected: Classroom opens, session starts

## Requirements
- REQ-01: Group sessions page shows all created sessions
- REQ-02: Each session card has Manage and Edit buttons
- REQ-03: Edit button is disabled or hidden after student enrollment
- REQ-04: Manage view shows Class and Student tabs
- REQ-05: Class tab shows session schedule
- REQ-06: Student tab shows enrolled students and attendance
- REQ-07: Join Classroom button appears only at scheduled session time
- REQ-08: Session automatically closes at end time
- REQ-09: Revenue displayed after student enrollment

## Edge Cases
| EC-01 | Edit session with enrolled students | Edit button disabled or hidden |
| EC-02 | Manage session with 0 students | Empty student list shown |
| EC-03 | Join Classroom before session time | Button not visible or disabled |
| EC-04 | Session at end time | Auto-closes classroom |
| EC-05 | Click Join twice | Only one classroom session created |

## Test Data
### Valid
| Field | Value |
|---|---|
| name | 98976564 |
| name | 123456 |
| name | Basic Math course |

### Invalid
| Field | Value |
|---|---|
| name | -10 |
| name | 0 |
