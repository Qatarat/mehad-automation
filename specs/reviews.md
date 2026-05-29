# Page: Reviews Management — Super Admin

**URL:** `https://dev.mehadedu.com/en/super-admin-login`

## Description
Super Admin reviews moderation dashboard. Shows all student reviews of tutors. Admin can search by student name, filter by status/rating/subject/date, and Approve, Reject, or Delete reviews.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Reviews link | `a:has-text("Reviews"), [data-testid="reviews-nav"]` | Required |
| Reviews table | `table, [data-testid="reviews-table"]` | Required |
| Search input | `input[placeholder*="Search"], input[placeholder*="student"]` | Optional |
| Filter option | `button:has-text("Filter"), [data-testid="filter"]` | Optional |
| Status filter | `select[aria-label*="Status"]` | Optional |
| Rating filter | `select[aria-label*="Rating"]` | Optional |
| Student name column | `th:has-text("Student")` | Required |
| Review content column | `th:has-text("Review"), th:has-text("Comment")` | Required |
| Status column | `th:has-text("Status")` | Required |
| Approve button | `button:has-text("Approve")` | Conditional |
| Reject button | `button:has-text("Reject")` | Conditional |
| Delete button | `button:has-text("Delete")` | Conditional |

## User Flows

### Flow 1: Moderate Reviews
1. Login as super admin
2. Navigate to Reviews
3. Reviews table shows student name, tutor, review, rating, status
4. Click "Approve" on a review
5. Review becomes visible on tutor profile

### Flow 2: Reject Review
1. Find a review
2. Click "Reject"
3. Review no longer visible

### Flow 3: Search and Filter Reviews
1. Type student name in search
2. Matching reviews shown
3. Apply filter: 5 stars
4. Only 5-star reviews shown

## Requirements
- REQ-01: Reviews table shows student name, subject, review, status
- REQ-02: Approve makes review visible on tutor profile
- REQ-03: Reject hides review from public
- REQ-04: Delete permanently removes review
- REQ-05: Search by student name filters correctly
- REQ-06: Filter by status, rating, subject, date works

## Edge Cases
| EC-01 | Search with no match | Empty state shown |
| EC-02 | Filter shows no results | Empty state shown |
| EC-03 | Delete already-deleted review | Error or button unavailable |
| EC-04 | XSS in search input | Sanitized |

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
