# Page: Admin Command Dashboard — Overview & Navigation

**URL:** `https://dev.mehadedu.com/en/admin-login`

## Description
The main landing dashboard after Admin login — distinct from the Super Admin's account-management pages (`add_admin.md`, `add_super_admin.md`, `payout.md`, `platfromfee.md`, `reports.md`) which all live under `/en/super-admin-login`. This spec covers the day-one Admin experience: the command-center overview (stat cards, recent activity), the full sidebar navigation surface, notifications, and role-scoped access — closing the gap where "Admin Control Center" (dashboard.html's feature) had no dedicated overview/navigation spec of its own; `admin_lead_management.md` only covers the leads/bookings workflow once inside the dashboard.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Admin login phone/OTP form | `input[type="tel"], input[name="phone"]` | Required |
| Admin login password field | `input[type="password"]` | Required — Admin auth uses phone+password+OTP per credential vault |
| Dashboard heading | `h1:has-text("Dashboard"), h1:has-text("Overview")` | Required |
| Stat cards (leads/bookings/revenue/active tutors) | `[data-testid="stat-card"], .stat-card` | Required |
| Sidebar: Leads/Requests | `a:has-text("Leads"), a:has-text("Requests")` | Required |
| Sidebar: Bookings | `a:has-text("Bookings")` | Required |
| Sidebar: Tutors | `a:has-text("Tutors")` | Required |
| Sidebar: Students/Parents | `a:has-text("Students"), a:has-text("Parents")` | Required |
| Sidebar: Finance/Settings | `a:has-text("Finance"), a:has-text("Settings")` | Required |
| Sidebar: Reports | `a:has-text("Reports")` | Optional — may be Super-Admin only |
| Notifications bell | `button[aria-label*="notification" i]` | Required |
| Notifications unread badge | `button[aria-label*="notification" i] span` | Conditional |
| Account switcher (role badge) | `text="Admin"` | Required |
| Logout action | `button:has-text("Logout"), a:has-text("Logout")` | Required |

## User Flows

### Flow 1: Admin Login and Dashboard Landing
1. Navigate to `/en/admin-login`
2. Enter phone `1926009607`, password, OTP per credential vault
3. Submit
→ Expected: Redirects to the main Admin dashboard with stat cards populated (not stuck loading, not showing raw `undefined`/`NaN`)

### Flow 2: Sidebar Navigation Covers Every Admin Area
1. Log in as Admin
2. Click through every sidebar link once
→ Expected: Each link loads its target page without a 404/500 and without an "Access Denied" state (since this account IS Admin)

### Flow 3: Notifications
1. Log in as Admin with unread notifications
2. Click the notifications bell
→ Expected: A list/dropdown of notifications opens; clicking one marks it read and the unread badge count decreases

### Flow 4: Logout Clears Session
1. Log in as Admin
2. Click Logout
3. Attempt to navigate back to the dashboard URL directly
→ Expected: Redirected to `/en/admin-login`, no dashboard content is visible

## Requirements
- REQ-01: Admin dashboard stat cards must render real numeric values (or an explicit zero/empty state), never `undefined`, `NaN`, or a perpetual spinner
- REQ-02: Every sidebar link an Admin sees must be reachable by that Admin (no dead links, no links that 404)
- REQ-03: A regular Admin's dashboard must not expose Super-Admin-only actions (create/delete other Admins) unless that specific account also holds Super Admin rights
- REQ-04: Notifications must reflect real unread counts and update after being read
- REQ-05: Logout must fully invalidate the session — direct back-navigation to a dashboard URL after logout must not render admin content from cache
- REQ-06: Failed Admin login (wrong password/OTP) must not reveal whether the phone number itself is registered (no user-enumeration via differing error messages)
- REQ-07: Page title must not contain 500 or 404 anywhere in the Admin dashboard

## Edge Cases
| EC-01 | Login with correct phone, wrong password | Generic invalid-credentials error, no redirect |
| EC-02 | Login with correct phone+password, wrong OTP | Generic invalid-OTP error, no redirect |
| EC-03 | Direct navigation to a dashboard URL while logged out | Redirect to `/en/admin-login`, no flash of dashboard content |
| EC-04 | Session idle for an extended period, then click a sidebar link | Either session still valid, or a clean re-login prompt — no broken half-authenticated state |
| EC-05 | Regular Admin (non-Super) directly navigates to `/en/super-admin-login`-gated routes | Denied — redirect or 403 |
| EC-06 | Rapid repeated failed logins | Rate limiting/lockout messaging shown, no unbounded retries |
| EC-07 | SQL injection payload in the login phone field (`' OR 1=1--`) | Rejected as invalid input, no 500, no auth bypass |
| EC-08 | XSS payload anywhere an Admin can enter free text (e.g. a notification note) | Rendered as literal text, no script execution |
| EC-09 | Notifications list with zero notifications | Clean empty state, no console errors |
| EC-10 | Two Admin sessions logged in simultaneously in two browsers | Both function independently; one logging out does not silently kill the other's session unless that's the intended design (verify actual behavior and document it) |

## Test Data
### Valid
| Field | Value |
|---|---|
| name | 1926009607 |
| name | 5654565 |

### Invalid
| Field | Value |
|---|---|
| name | ' OR 1=1-- |
| name | <script>alert(1)</script> |
| name | 000000 |
