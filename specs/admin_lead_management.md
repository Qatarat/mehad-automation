# Page: Admin Control Center — Lead Assignment, Reassignment & Bookings

**URL:** `https://dev.mehadedu.com/en/admin-login`

## Description
The existing `add_admin.md`/`add_super_admin.md` specs only cover admin-user CRUD in the Super Admin area. This spec covers the Admin's core day-to-day workflow referenced in dashboard.html's "Admin Control Center" feature: reviewing incoming tutor-request leads (created by `request_tutor_wizard.md`), assigning a tutor to a lead, reassigning it to a different tutor if declined/unavailable, and managing the resulting bookings. This closes a gap where the request-wizard → admin-assignment → tutor-accept/decline pipeline had no end-to-end spec despite being the platform's core business flow.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Admin login form | `input[name="phone"], input[type="tel"]` | Required — phone+password+OTP per dashboard credential vault |
| Leads/Requests nav item | `a:has-text("Leads"), a:has-text("Requests")` | Required |
| Leads table | `table, [data-testid="leads-table"]` | Required |
| Lead row status badge | `.status-badge, :text("New"), :text("Assigned"), :text("Offered")` | Required |
| Assign Tutor button | `button:has-text("Assign"), button:has-text("Recommend to Customer")` | Required |
| Tutor picker (search/select) | `input[placeholder*="tutor" i], [role="combobox"]` | Required |
| Reassign button | `button:has-text("Reassign")` | Required — visible after a tutor declines |
| Confirm assignment dialog | `[role="dialog"] button:has-text("Confirm")` | Required |
| Bookings nav item | `a:has-text("Bookings")` | Required |
| Bookings table | `table, [data-testid="bookings-table"]` | Required |
| Booking status filter | `select[aria-label*="status" i]` | Required |
| Finance/Settings CMS nav item | `a:has-text("Finance"), a:has-text("Settings")` | Required |
| Platform fee input | `input[name*="fee" i], input[name*="commission" i]` | Required |

## User Flows

### Flow 1: New Lead Appears After Wizard Submission
1. (Precondition) A customer completes `request_tutor_wizard.md` Flow 1 and gets a REQ-ID
2. Log in as Admin
3. Navigate to Leads/Requests
→ Expected: The new REQ-ID appears in the leads table with status "New", matching curriculum/subject/schedule selected in the wizard

### Flow 2: Assign a Tutor to a Lead
1. Open a "New" lead
2. Click "Assign" / search and select a matching tutor
3. Click "Recommend to Customer" / Confirm
→ Expected: Lead status changes to "Offered", tutor sees the lead appear in their own portal (see `teacher_dashboard_overview.md`) for accept/decline

### Flow 3: Reassign After Tutor Decline
1. (Precondition) A previously assigned tutor declines the lead
2. Reopen the lead in Admin
3. Click "Reassign"
4. Select a different tutor
5. Confirm
→ Expected: Lead status updates and a new offer is sent to the newly selected tutor; the declining tutor no longer sees this lead as pending

### Flow 4: View and Filter Bookings
1. Navigate to Bookings
2. Filter by status (e.g. "Confirmed", "Completed", "Cancelled")
→ Expected: Table updates to show only matching bookings, counts are internally consistent

### Flow 5: Update Platform Fee / Finance Settings
1. Navigate to Finance/Settings
2. Change the platform commission fee percentage
3. Save
→ Expected: Change is persisted and reflected in newly calculated tutor payouts (does not retroactively alter already-settled payouts)

## Requirements
- REQ-01: A lead created by the request wizard must be visible to Admin with all customer-selected details intact (curriculum, subject, schedule, contact)
- REQ-02: Assigning a tutor changes the lead's status in a way visible both to Admin and to the assigned tutor
- REQ-03: Reassignment must be possible any number of times and must always reflect the *current* assignee only — no stale "assigned" state pointing at a tutor who already declined
- REQ-04: Only Admin/Super Admin roles can access lead assignment and finance settings — a Tutor or Parent session hitting these routes directly must be denied (RBAC/privilege-escalation check)
- REQ-05: Bookings table status filter options are mutually exclusive and their counts reconcile with the unfiltered total
- REQ-06: Platform fee changes apply going forward only, not retroactively, unless explicitly designed otherwise (verify actual behavior and document it)
- REQ-07: Lead/booking actions are logged/auditable (who assigned/reassigned, when) — verify at least that the UI surfaces this, even if the underlying audit log itself isn't directly testable via UI
- REQ-08: Page title must not contain 500 or 404 anywhere in this area

## Edge Cases
| EC-01 | Assign a tutor whose availability doesn't match the lead's requested schedule | Either blocked with a warning or clearly flagged, not silently mismatched |
| EC-02 | Reassign a lead that has already been accepted by the current tutor | Blocked or requires explicit confirmation — must not silently un-assign an already-accepted session |
| EC-03 | Two admins assign different tutors to the same lead concurrently | Last write wins with a clear resulting state, or a conflict is surfaced — no split-brain state where both tutors think they're assigned |
| EC-04 | Non-admin role (Tutor session) directly navigates to the admin leads URL | Denied — redirect or 403, no lead data exposed |
| EC-05 | Set platform fee to a negative number or > 100% | Rejected with validation error |
| EC-06 | Set platform fee to a non-numeric value | Rejected with validation error |
| EC-07 | SQL injection payload in the tutor-picker search box (`' OR 1=1--`) | Rejected/escaped safely, no data leakage, no 500 |
| EC-08 | XSS payload in any admin-editable text field (lead notes, CMS content) (`<script>alert(1)</script>`) | Rendered as literal text everywhere it's later displayed |
| EC-09 | Filter bookings by a status that has zero matching records | Clean empty state, no console errors |
| EC-10 | Reassign a lead many times in rapid succession | System remains consistent — final state reflects the last reassignment only, no duplicate offers sent to earlier tutors |

## Test Data
### Valid
| Field | Value |
|---|---|
| name | Automations Tutor |
| name | Math |
| name | Assigned |
| name | Confirmed |

### Invalid
| Field | Value |
|---|---|
| name | -5 |
| name | 150 |
| name | abc |
| name | ' OR 1=1-- |
| name | <script>alert(1)</script> |
