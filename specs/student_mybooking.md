# Page: Student My Bookings

**URL:** `https://dev.mehadedu.com/en/dashboard/bookings`

## Description
Student's booking management page. Shows upcoming and completed sessions. Students can join active sessions, complete them, and view session recordings from history.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| My Bookings heading | `h1:has-text("My Bookings"), h2:has-text("Bookings")` | Required |
| Upcoming sessions section | `:has-text("Upcoming"), [data-tab="upcoming"]` | Required |
| Session History section | `:has-text("Session History"), [data-tab="history"]` | Required |
| Session card | `.session-card, [data-testid="booking-card"]` | Required |
| Join Classroom button | `button:has-text("Join Classroom")` | Conditional — at session time |
| Complete Session button | `button:has-text("Complete Session")` | Conditional — after session ends |
| View Recording button | `button:has-text("View Recording")` | Conditional — in history |
| Session title | `.session-title, [data-testid="session-title"]` | Required |
| Session date-time | `.session-datetime, time` | Required |
| Session status | `.session-status, [data-testid="status"]` | Required |
| Unbooked section | `:has-text("Unbooked"), [data-tab="unbooked"]` | Conditional |

## User Flows

### Flow 1: View My Bookings
1. Navigate to https://dev.mehadedu.com/en/dashboard/bookings
2. Page shows upcoming sessions
3. Sessions are sorted by nearest time
→ Expected: Upcoming sessions displayed with correct details

### Flow 2: Join a Session at Scheduled Time
1. Navigate to My Bookings
2. Find session whose time has arrived
3. "Join Classroom" button is now visible
4. Click "Join Classroom"
5. Classroom opens
→ Expected: Live classroom session starts

### Flow 3: Complete Session and Write Review
1. After session ends, navigate to My Bookings
2. Find completed session
3. Click "Complete Session"
4. Review prompt may appear
5. Submit rating and review
→ Expected: Session moves to Session History

### Flow 4: View Recording in Session History
1. Navigate to My Bookings
2. Click "Session History" tab
3. Find completed session
4. Click "View Recording"
→ Expected: Recording file loads (e.g. "Recording 1.1")

## Requirements
- REQ-01: My Bookings page accessible at /en/dashboard/bookings
- REQ-02: Upcoming sessions show session title, date-time, status
- REQ-03: Join Classroom button only appears at scheduled session time
- REQ-04: Complete Session button appears after session ends
- REQ-05: Clicking Complete Session updates status and moves to history
- REQ-06: Session History shows completed sessions with recording option
- REQ-07: View Recording opens a valid recording file
- REQ-08: Tutor cancellation moves session to Unbooked section
- REQ-09: Student cannot join session before scheduled time
- REQ-10: Cancelled sessions do not appear in Upcoming

## Edge Cases
| EC-01 | Join before session time | Join button not visible or disabled |
| EC-02 | Complete Session before session ends | Button not visible |
| EC-03 | No bookings exist | Empty state message shown |
| EC-04 | Tutor cancels 1-to-1 session | Session appears in Unbooked section |
| EC-05 | Student books same group session twice | System prevents duplicate |
| EC-06 | Recording not yet available | View Recording disabled or shows pending |
| EC-07 | Unauthenticated user accesses bookings | Redirects to login |

## Test Data
### Valid
| Field | Value |
|---|---|
| name | 98976564 |
| name | 123456 |
| name | upcoming |
| name | completed |

### Invalid
| Field | Value |
|---|---|
| name | 000000 |
| name | 000000 |
