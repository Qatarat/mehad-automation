# Page: Reports Management — Super Admin

**URL:** `https://dev.mehadedu.com/en/super-admin-login`

## Description
Super Admin reports dashboard. Shows Total, Pending, Under Review, Resolved, and Dismissed reports. Admin can start review, resolve, or dismiss reports submitted by students after sessions.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Reports link | `a:has-text("Reports"), [data-testid="reports-nav"]` | Required |
| Total Reports card | `:has-text("Total Reports"), [data-testid="total-reports"]` | Required |
| Pending Reports card | `:has-text("Pending"), [data-testid="pending-reports"]` | Required |
| Under Review card | `:has-text("Under Review"), [data-testid="under-review"]` | Required |
| Resolved card | `:has-text("Resolved"), [data-testid="resolved"]` | Optional |
| Reports table | `table, [data-testid="reports-table"]` | Required |
| Student name column | `th:has-text("Student")` | Required |
| Status column | `th:has-text("Status")` | Required |
| View button | `button[aria-label*="view"], button:has-text("View")` | Optional |
| Start Review button | `button:has-text("Start Review")` | Conditional |
| Mark as Resolved button | `button:has-text("Mark as Resolved")` | Conditional |
| Dismiss Report button | `button:has-text("Dismiss")` | Conditional |
| Status filter | `select[aria-label*="Status"], [placeholder*="All"]` | Optional |
| Search input | `input[placeholder*="Search"]` | Optional |

## User Flows

### Flow 1: View Reports Dashboard
1. Login as super admin
2. Click "Reports" in sidebar
3. Dashboard shows report statistics and table
4. Verify student name, date, topic, status shown
5. Apply status filter: Pending
6. Only pending reports shown
7. Search by student name
8. Correct results displayed

### Flow 2: Start Review and Resolve
1. Find pending report
2. Click "Start Review"
3. Status changes to "Under Review"
4. Click "Mark as Resolved"
5. Status changes to "Resolved"

### Flow 3: Dismiss Report
1. Find a report
2. Click "Dismiss"
3. Report dismissed
4. Status shows Dismissed

## Requirements
- REQ-01: Reports page shows all report statistics cards
- REQ-02: Reports table shows student name, date, topic, status
- REQ-03: Start Review changes status to Under Review
- REQ-04: Mark as Resolved changes status to Resolved
- REQ-05: Dismiss Report dismisses the report
- REQ-06: Filter by All, Pending, Under Review, Resolved, Dismissed
- REQ-07: Search by student name or subject

## Edge Cases
| EC-01 | No reports exist | Empty state shown |
| EC-02 | Search with no match | Empty results |
| EC-03 | Dismiss already-dismissed report | Error or button disabled |
| EC-04 | Filter shows no results | Empty state shown |
| EC-05 | XSS in search input | Sanitized |

## Test Data
### Valid
| Field | Value |
|---|---|
| name | 98976564 |
| name | 123456 |
| name | Test Student |

### Invalid
| Field | Value |
|---|---|
| name | <script>alert(1)</script> |
