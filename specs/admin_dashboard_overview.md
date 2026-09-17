# Page: Admin Command Dashboard — Overview & Navigation

**URL:** `https://dev.mehadedu.com/en/admin/dashboard`

## Description
CORRECTED 2026-09-17 after live verification (logged in as Admin, dev.mehadedu.com, dev vault credentials: phone 5654565 BD, password Rumel1234, OTP 123456 — all confirmed working). The main landing dashboard after Admin login, at `/en/admin/dashboard` (not the login URL itself) — distinct from the Super Admin's account-management pages (`add_admin.md`, `add_super_admin.md`, `payout.md`, `platfromfee.md`, `reports.md`) which live under `/en/super-admin-login`. Real page heading: "Good morning, Admin" under an "OPERATIONS COMMAND CENTER" eyebrow label. The account switcher shows the literal seeded name "Test1 Admin" with role badge "Admin". Sidebar items confirmed live, exactly: **Dashboard, Teaching Requests, Messages, Bookings, Tutors, Students, Settings** — there is no separate "Leads", "Finance", or "Reports" sidebar item at the regular-Admin level (Reports may be Super-Admin-only, unverified). Dashboard widgets confirmed live: "Recent Tutor Requests" (columns: Request, Student, Assigned, Created, Action) and "Recent Notifications" (e.g. "New Tutor Joined the Platform").

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Admin login phone field | `input[placeholder="50 123 4567"]` | Required — with country-code selector, default +966 |
| Admin login password field | `input[type="password"], input[placeholder*="password" i]` | Required |
| Admin login Continue button | `button:has-text("Continue")` | Required — submits phone+password, then navigates to a separate OTP verify step |
| OTP verify heading | `h1:has-text("Verify your login")` | Required — at `/en/admin-login/verify?phone=...` |
| OTP 6-box input | `input` (6 separate single-digit boxes) | Required — accepts the full 6-digit code typed in sequence, auto-advances between boxes |
| Verify Login button | `button:has-text("Verify Login")` | Required |
| Dashboard heading | `h1:has-text("Good morning, Admin"), :text("Operations Command Center")` | Required |
| Recent Tutor Requests widget | `:text("Recent Tutor Requests")` | Required |
| Recent Notifications widget | `:text("Recent Notifications")` | Required |
| Stat cards | `[data-testid="stat-card"], .stat-card` | Present but exact metrics unverified — re-check on next pass |
| Sidebar: Dashboard | `a:has-text("Dashboard")` | Required |
| Sidebar: Teaching Requests | `a:has-text("Teaching Requests")` | Required — NOT "Leads" |
| Sidebar: Messages | `a:has-text("Messages")` | Required |
| Sidebar: Bookings | `a:has-text("Bookings")` | Required |
| Sidebar: Tutors | `a:has-text("Tutors")` | Required |
| Sidebar: Students | `a:has-text("Students")` | Required |
| Sidebar: Settings | `a:has-text("Settings")` | Required |
| Notifications bell | `button[aria-label*="notification" i], svg + [class*="badge"]` | Required — shows a "99+" style unread badge |
| Account switcher (role badge) | `text="Admin"` | Required — shown under the account name "Test1 Admin" |
| Logout action | `button:has-text("Logout"), a:has-text("Logout")` | Required — inside the account switcher dropdown |

## User Flows

### Flow 1: Admin Login and Dashboard Landing
1. Navigate to `/en/admin-login`
2. Select country code Bangladesh (+880), enter phone `5654565`
3. Enter password `Rumel1234`
4. Click "Continue" — navigates to `/en/admin-login/verify?phone=%2B8805654565`
5. Enter OTP `123456` into the 6-digit box
→ Expected: Auto-navigates to `/en/admin/dashboard`, heading "Good morning, Admin" with "Recent Tutor Requests" and "Recent Notifications" widgets populated — confirmed live, works exactly as described

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
