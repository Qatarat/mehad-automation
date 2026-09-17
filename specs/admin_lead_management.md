# Page: Admin Control Center — Teaching Requests, Assignment & Bookings

**URL:** `https://dev.mehadedu.com/en/admin/tutor-requests`

## Description
CORRECTED 2026-09-17 after live verification (logged in as Admin, dev.mehadedu.com, using the dashboard.html credential vault's dev Admin account: phone 5654565 BD, password Rumel1234, OTP 123456 — all confirmed working exactly as documented). The sidebar item and page are actually called **"Teaching Requests"**, not "Leads" as this spec previously assumed — the breadcrumb reads "Tutor Requests". Real status values observed live: **"Waiting for Customer Decision"**, **"Under Review"**, **"Booking Created"**, **"Booking Ready"**, **"Awaiting Customer Approval"** (not the generic "New"/"Assigned"/"Offered" previously guessed). The detail page for one request lives at `/en/admin/tutor-requests/{id}` and shows Student, Parent, Subject, Teaching Mode, Package (e.g. "20 Sessions"), and Request ID (e.g. `REQ-1660`) — confirming `request_tutor_wizard.md`'s REQ-ID format is real. A genuine **concurrency lock** was observed live: a request already claimed by one admin shows "This request is being processed by another admin. All actions are disabled." to any other admin who opens it — this is real, working behavior, not a hypothetical edge case.

This spec covers the Admin's core day-to-day workflow: reviewing incoming Teaching Requests (created by the Parent-side `request_tutor_wizard.md`), assigning a tutor, reassigning if declined/unavailable, and managing the resulting bookings.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Admin login form | Phone (WhatsApp Number) + Password, then a 6-digit OTP on a separate `/en/admin-login/verify` step | Required — confirmed live, matches `admin_dashboard_overview.md` |
| Teaching Requests nav item | `a:has-text("Teaching Requests")` | Required — NOT "Leads" |
| Teaching Requests table | `table` | Required, columns: Request ID, Student, Parent, Subject, Grade, Mode, Preferred Schedule, Submitted, Status |
| Status filter | `button:has-text("All Status")` | Required |
| Subject filter | `button:has-text("All Subjects")` | Required |
| Level filter | `button:has-text("All Levels")` | Required |
| Date range filter | `button:has-text("Select date range")` | Required |
| Search by request ID | `input[placeholder*="Search by request ID" i]` | Required |
| Request ID link (row) | `a:has-text("REQ-")` | Required — opens `/en/admin/tutor-requests/{id}` |
| Status badge on detail page | `:text("Awaiting Customer Approval"), :text("Under Review"), :text("Waiting for Customer Decision")` | Required |
| Concurrency lock banner | `text="This request is being processed by another admin. All actions are disabled."` | Required — confirmed real behavior |
| "Assigned to X" banner | `text=/Assigned to .+/` | Required |
| Bookings nav item | `a:has-text("Bookings")` | Required |
| Tutors nav item | `a:has-text("Tutors")` | Required |
| Students nav item | `a:has-text("Students")` | Required |
| Settings nav item | `a:has-text("Settings")` | Required — platform fee likely lives here (see `platfromfee.md`) |

## User Flows

### Flow 1: New Teaching Request Appears After Wizard Submission
1. (Precondition) A parent completes `request_tutor_wizard.md` up to submission and gets a REQ-ID
2. Log in as Admin
3. Navigate to "Teaching Requests"
→ Expected: The new REQ-ID appears in the table with a real status (e.g. "Under Review"), matching the curriculum/subject/schedule selected in the wizard — confirmed live for existing data (REQ-1657 through REQ-1660)

### Flow 2: Open a Request and Assign/Manage It
1. Click a Request ID (e.g. from the Dashboard's "Recent Tutor Requests" widget or the full Teaching Requests table)
2. View the detail page
→ Expected: Shows Student, Parent, Subject, Teaching Mode, Package, Request ID, and current status; if unassigned, admin actions (assign a tutor) are available; if already claimed by another admin, all actions are disabled with the concurrency-lock banner — confirmed live

### Flow 3: Concurrency Lock Prevents Double-Handling
1. (Precondition) Request is already assigned to/being handled by another admin (e.g. "Md. Rakib Islam")
2. Open that request as a different admin account
→ Expected: Banner reads "This request is being processed by another admin. All actions are disabled." and no action controls are interactive — confirmed live

### Flow 4: Filter and Search Teaching Requests
1. Navigate to Teaching Requests
2. Use the status filter, subject filter, or search-by-request-ID box
→ Expected: Table updates to matching rows only

### Flow 5: Dashboard Overview Shows Recent Requests and Notifications
1. Log in as Admin, land on `/en/admin/dashboard`
→ Expected: "Recent Tutor Requests" widget shows the latest REQ rows with Student/Assigned/Created columns; "Recent Notifications" widget shows items like "New Tutor Joined the Platform" — confirmed live

## Requirements
- REQ-01: A Teaching Request created by the wizard is visible to Admin with all parent-selected details intact (student, parent, subject, mode, schedule, package)
- REQ-02: Status values are one of the real observed set (Under Review, Waiting for Customer Decision, Booking Created, Booking Ready, Awaiting Customer Approval) — a spec/test asserting a different status vocabulary is wrong and should be updated
- REQ-03: A request already claimed by one admin must show the concurrency-lock banner and disable all actions for any other admin who opens it
- REQ-04: Only Admin/Super Admin roles can access `/en/admin/*` routes — a Tutor, Parent, Student, or Child session hitting these routes directly must be denied (RBAC/privilege-escalation check)
- REQ-05: Filters (status/subject/level/date range) are combinable and the resulting table is internally consistent
- REQ-06: Page title must not contain 500 or 404 anywhere in this area

## Edge Cases
| EC-01 | Open a request already assigned to another admin | Concurrency-lock banner shown, all actions disabled — confirmed live behavior |
| EC-02 | Non-admin role (Tutor/Parent/Student/Child session) directly navigates to `/en/admin/tutor-requests` | Denied — redirect or 403, no request data exposed |
| EC-03 | Search by a nonexistent request ID | Clean empty state, no console errors |
| EC-04 | Search box with SQL injection payload (`' OR 1=1--`) | Rejected/escaped safely, no data leakage, no 500 |
| EC-05 | Search/filter fields with XSS payload (`<script>alert(1)</script>`) | Rendered as literal text, no script execution |
| EC-06 | Filter by a status combination that has zero matching records | Clean empty state, no console errors |
| EC-07 | Direct navigation to `/en/admin/tutor-requests/{id}` for a nonexistent ID | Clean 404/not-found state within the app shell, not a raw server error |
| EC-08 | Admin OTP entered incorrectly 5+ times | Rate limiting/lockout messaging, no unbounded retries |

## Test Data
### Valid
| Field | Value |
|---|---|
| name | 5654565 |
| name | Rumel1234 |
| name | 123456 |
| name | REQ-1660 |
| name | Under Review |
| name | Waiting for Customer Decision |
| name | Booking Created |
| name | Booking Ready |

### Invalid
| Field | Value |
|---|---|
| name | ' OR 1=1-- |
| name | <script>alert(1)</script> |
| name | REQ-999999 |
