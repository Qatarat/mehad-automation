# Page: Student Management — Super Admin

**URL:** `https://dev.mehadedu.com/en/super-admin-login`

## Description
Super Admin student management dashboard. Lists all student accounts with search, status filter (Pending, Active, Suspended), and actions: View Details, Verify Profile, Suspend, Reject, Delete.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Student section link | `a:has-text("Student"), [data-testid="students-nav"]` | Required |
| Students table | `table, [data-testid="students-table"]` | Required |
| Search input | `input[placeholder*="Search"]` | Optional |
| Status filter | `select[aria-label*="Status"], [placeholder*="All Status"]` | Optional |
| Student name column | `th:has-text("Student Name")` | Required |
| Phone column | `th:has-text("Phone")` | Required |
| Status column | `th:has-text("Status")` | Required |
| Pagination next | `button:has-text("Next"), [aria-label="Next page"]` | Optional |
| Three dot menu | `button[aria-label*="actions"]` | Required |
| View Details | `[role="menuitem"]:has-text("View Details")` | Required |
| Verify Profile | `[role="menuitem"]:has-text("Verify Profile")` | Optional |
| Suspend Profile | `[role="menuitem"]:has-text("Suspend Profile")` | Optional |
| Delete Profile | `[role="menuitem"]:has-text("Delete Profile")` | Optional |

## User Flows

### Flow 1: View All Students
1. Login as super admin
2. Click "Student" in sidebar
3. Student list shows all accounts
4. Each row shows name, phone, location, member since, status

### Flow 2: Search Students
1. Type student name in search
2. Matching students shown
3. Invalid search shows empty results

### Flow 3: Suspend Student
1. Find student in list
2. Click three-dot menu
3. Click "Suspend Profile"
4. Student account suspended
5. Student cannot book sessions

### Flow 4: Delete Student
1. Find student
2. Click three-dot menu
3. Click "Delete Profile"
4. Confirm deletion
5. Student deleted, cannot login

## Requirements
- REQ-01: Student list shows name, phone, location, member date, status
- REQ-02: Search by name or email filters correctly
- REQ-03: Status filter: Pending, Active, Suspended
- REQ-04: Verify Profile adds verified badge
- REQ-05: Suspend prevents student from booking sessions
- REQ-06: Delete permanently removes account

## Edge Cases
| EC-01 | Search with no match | Empty state shown |
| EC-02 | Suspended student tries to book | Booking blocked |
| EC-03 | Delete student with active bookings | System handles gracefully |
| EC-04 | Filter with no results | Empty state |

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
