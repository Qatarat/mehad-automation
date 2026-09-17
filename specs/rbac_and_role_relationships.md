# Page: Cross-Role Relationships & RBAC Access Matrix

**URL:** `https://dev.mehadedu.com/en`

## Description
Every other spec tests one role in isolation. This spec is the capstone that verifies the *relationships* between roles actually work end-to-end, and that role boundaries are actually enforced (not just documented per-spec as scattered edge cases). Two halves:

1. **Positive integration** — an action by one role must correctly produce the right visible effect for the *other* roles connected to it (Parent books → Admin sees lead → Admin assigns Tutor → Tutor sees offer → Tutor accepts → Parent/Child see the confirmed session → session happens → Parent/Student can review the Tutor → Tutor's earnings reflect the completed session).
2. **Negative isolation (RBAC matrix)** — each of the six roles (Public, Parent, Student, Child, Tutor, Admin/Super Admin) must be denied access to every other role's protected routes and data, with no partial leaks.

This closes the gap where role interactions were only ever implied, never verified as a chain.

## UI Elements
(This spec drives multiple pages/roles in sequence — see individual role specs for element selectors: `login.md`, `child_portal.md`, `parent_dashboard.md`, `request_tutor_wizard.md`, `admin_lead_management.md`, `teacher_dashboard_overview.md`, `session.md`, `tutor_earnings_payout.md`, `student_review_and_ratings.md`.)

| Element | Selector | Notes |
|---|---|---|
| Role badge in account switcher | `text="Parent"`, `text="Student"`, `text="Child"`, `text="Tutor"`, `text="Admin"` | Required — used to assert which role is active after each login |
| Generic "Access Denied" / 403 state | `:text("Access Denied"), :text("403"), :text("Unauthorized")` | Required for negative checks |

## User Flows

### Flow 1: Full Lifecycle — Request to Reviewed Session
1. As Parent: complete `request_tutor_wizard.md` Flow 1 → get REQ-ID
2. As Admin: find that REQ-ID in Leads (`admin_lead_management.md` Flow 1), assign a Tutor
3. As Tutor: see the new lead offer in their dashboard, accept it
4. As Parent: confirm the session now shows "Confirmed" with the assigned Tutor's name (not just "Offered")
5. As Child or Student (whichever the session was booked for): confirm the session appears in *their* Sessions list too
6. Join and complete the session (see `live_classroom.md`)
7. As Student/Parent: submit a review/rating for the Tutor (`student_review_and_ratings.md`)
8. As Tutor: confirm the review appears on their public/instructor profile and the completed session is reflected in Earnings (`tutor_earnings_payout.md`)
→ Expected: Every step's output is visible to the correct downstream role with matching IDs/names/status — no step is a dead end

### Flow 2: Admin Reassignment Propagates Correctly
1. As Tutor A: decline an assigned lead
2. As Admin: reassign the same lead to Tutor B
3. As Tutor A: confirm the lead no longer appears as pending/assigned to them
4. As Tutor B: confirm the lead now appears as offered to them
5. As Parent: confirm the dashboard reflects Tutor B, not Tutor A
→ Expected: The reassignment is consistently visible to all three affected accounts, no stale references to Tutor A remain anywhere the Parent or Tutor B can see

### Flow 3: Parent-Provisioned Child Credentials Take Effect
1. As Parent: set/reset a child's Child Login username+password (`parent_dashboard.md` Flow 2)
2. In a separate session: log in at `/en/child-login` with those exact credentials
→ Expected: Child login succeeds immediately, no propagation delay, no stale old credentials still working after a reset

### Flow 4: Admin Platform-Fee Change Reflects in Tutor Earnings
1. As Admin: change the platform commission fee (`admin_lead_management.md` Flow 5)
2. As Tutor: complete a new session after the change and check Earnings
→ Expected: The new session's earnings calculation uses the *new* fee percentage; a session completed *before* the change still reflects the *old* fee (no retroactive rewrite)

### Flow 5: RBAC Matrix — Each Role Against Every Other Role's Routes
For each (actingRole, targetRoute) pair below, log in as `actingRole` and directly navigate to `targetRoute`:

| Acting Role | Target Route (belongs to) | Expected |
|---|---|---|
| Public (no session) | `/en/dashboard/sessions` (any authed role) | Redirect to login, no content |
| Child | `/en/dashboard/wallet` (Parent/Student) | 403/redirect, no wallet data |
| Child | `/en/dashboard/earnings` (Tutor) | 403/redirect |
| Child | Admin lead-management route | 403/redirect |
| Student | Tutor's Earnings & Payouts page | 403/redirect |
| Student | Admin lead-management route | 403/redirect |
| Parent | Another parent's child profile (by guessed/incremented ID) | 403/redirect, no data (IDOR) |
| Tutor | Admin's Add Admin / Add Super Admin page | 403/redirect |
| Tutor | Another tutor's Earnings & Payouts page (by guessed ID) | 403/redirect (IDOR) |
| Admin (non-Super) | Super-Admin-only Add Super Admin page | 403/redirect, unless account also holds Super Admin |
→ Expected for every row: no 200-with-real-data response; either a redirect to login/home or an explicit 403/Access-Denied state — never a silent empty page that could be mistaken for "no data" when it's actually "blocked"

## Requirements
- REQ-01: A REQ-ID created by a Parent/Student is discoverable by Admin with all original wizard selections intact
- REQ-02: A lead assignment by Admin is visible to the assigned Tutor within the same session (no manual refresh workaround required to "make it appear")
- REQ-03: A Tutor's accept/decline action is reflected back to both Admin and the requesting Parent/Student without manual intervention
- REQ-04: A booked session is visible to *all* legitimately connected parties (Tutor, and whichever of Parent/Student/Child the session is for) with consistent details (date, time, subject)
- REQ-05: A review submitted by Student/Parent is visible on the correct Tutor's profile and nowhere else
- REQ-06: Every cross-role data reference (lead → tutor, session → child, review → tutor) uses server-side authorization, not just UI hiding — verify via direct URL/ID manipulation, not just checking the nav menu doesn't show a link
- REQ-07: No role can read or write another party's data by ID manipulation alone (systematic IDOR/BOLA check across parent↔child, tutor↔tutor, admin↔admin boundaries)
- REQ-08: Session/role state does not bleed across logins — logging out of one role and into another in the same browser must not retain the previous role's cached dashboard data

## Edge Cases
| EC-01 | Admin assigns a lead to a Tutor, then immediately deletes/deactivates that Tutor's account | Lead reverts to unassigned/flagged for Admin, does not silently vanish or stay "assigned" to a dead account |
| EC-02 | Parent removes a child profile that has an in-progress lead/session | System either blocks the removal or gracefully cancels the dependent lead/session — no orphaned reference visible to the Tutor/Admin |
| EC-03 | Two different roles' sessions open in two tabs of the same browser (e.g. Parent in tab 1, Admin in tab 2, same browser profile) | Each tab's session/role stays correctly isolated — no cross-contamination of cookies/local storage causing one tab to act as the wrong role |
| EC-04 | Tutor accepts a lead that Admin has, in the same instant, reassigned away from them | System resolves to one consistent final state (documented, whichever it is) — never a state where both the old and new tutor believe they own the session |
| EC-05 | Child attempts a direct API call (not just UI navigation) to a Parent-only endpoint using dev tools/network replay | Server rejects it (401/403) purely on role, independent of what the UI shows |
| EC-06 | Review submitted for a session that was never actually completed/joined | Either blocked, or clearly flagged as unverified — must not be indistinguishable from a genuine post-session review |
| EC-07 | Admin views the leads list while a Parent is mid-submission of the request wizard (not yet finalized) | Incomplete/draft requests do not appear as if they were finalized leads |

## Test Data
### Valid
| Field | Value |
|---|---|
| name | Automations Parent |
| name | Automations Tutor |
| name | Automations Student |
| name | Child |

### Invalid
| Field | Value |
|---|---|
| name | ' OR 1=1-- |
| name | <script>alert(1)</script> |
| name | 999999999 |
