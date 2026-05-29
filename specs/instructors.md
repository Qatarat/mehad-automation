# Page: Instructors — Super Admin Session Management

**URL:** `https://dev.mehadedu.com/en/super-admin-login`

## Description
Super Admin session management view. Lists all tutor-student sessions with filtering by status (Pending, Completed, Cancelled) and type (1-to-1, Group). Admin can view case files and cancel sessions.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Super admin login | `h1:has-text("Super Admin"), input[type="tel"]` | Required |
| Session section link | `a:has-text("Session"), [data-testid="session-nav"]` | Required |
| Sessions table | `table, [data-testid="sessions-table"]` | Required |
| Search input | `input[placeholder*="Search"], input[type="search"]` | Optional |
| Status filter | `select[aria-label*="Status"], [placeholder*="All Status"]` | Optional |
| Type filter | `select[aria-label*="Type"], [placeholder*="All Types"]` | Optional |
| Tutor name column | `th:has-text("Tutor"), td:first-child` | Required |
| Three dot menu | `button[aria-label*="actions"]` | Required |
| View Case File option | `[role="menuitem"]:has-text("View Case File")` | Required |
| Cancel Session option | `[role="menuitem"]:has-text("Cancel Session")` | Required |
| Cancel confirmation | `[role="dialog"] button:has-text("Confirm")` | Conditional |

## User Flows

### Flow 1: View All Sessions
1. Login to super admin dashboard
2. Click "Session" in sidebar
3. Sessions list loads with all records
→ Expected: Table shows tutor name, student, subject, type, status, price, date

### Flow 2: Filter Sessions by Status
1. Navigate to sessions
2. Click Status filter dropdown
3. Select "Completed"
4. Only completed sessions shown
→ Expected: Filtered list correct

### Flow 3: Cancel a Session
1. Find a session in list
2. Click three-dot menu
3. Click "Cancel Session"
4. Confirmation modal appears
5. Click "Confirm"
→ Expected: Session cancelled, status updated for both tutor and student

### Flow 4: View Case File
1. Click three-dot menu on session
2. Click "View Case File"
3. Full session details shown
→ Expected: All session info correctly displayed

## Requirements
- REQ-01: Sessions page shows all session records
- REQ-02: Each row shows tutor, student, subject, type, status, price, date
- REQ-03: Search filters by tutor/student/subject name
- REQ-04: Status filter: Pending, Completed, Cancelled
- REQ-05: Type filter: One-to-One, Group Session
- REQ-06: Cancel session requires confirmation
- REQ-07: Cancellation reflected on both tutor and student side

## Edge Cases
| EC-01 | Search with invalid name | Empty results shown |
| EC-02 | Cancel already-cancelled session | Error or button disabled |
| EC-03 | Filter shows no results | Empty state shown |

## Test Data
### Valid
| Field | Value |
|---|---|
| name | 98976564 |
| name | 123456 |
| name | Test Tutor |

### Invalid
| Field | Value |
|---|---|
| name | <script>alert(1)</script> |
