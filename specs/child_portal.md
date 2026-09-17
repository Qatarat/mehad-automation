# Page: Child Login & Restricted Child Portal

**URL:** `https://dev.mehadedu.com/en/child-login`

## Description
Dedicated standalone login page for the Child Learner role — no OTP, username + password only (default test credentials: username `Child`, password `1234`). After login the child lands on `/en/dashboard/sessions` inside a heavily restricted sidebar that shows **only "Sessions" and "Messages"** (verified live via Chrome MCP, 2026-09-17) — no Wallet, Settings, Profile, Bookings, Payments, or child-management links. This is intentionally the most locked-down role in the platform and needs explicit negative/RBAC coverage: a child session must never be able to reach parent-only, student-only, tutor-only, or admin-only routes.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Mehad logo | `img[alt*="MEHAD" i], text="MEHAD"` | Required |
| Page heading | `h1:has-text("Child Login"), h2:has-text("Child Login")` | Required |
| Subheading | `text="Enter your username and password to login"` | Required |
| Username input | `input[placeholder="Enter your username"]` | Required |
| Password input | `input[placeholder="Enter your password"]` | Required |
| Password visibility toggle | `button[aria-label*="password" i], svg + button` | Optional |
| Login button | `button:has-text("Login")` | Required |
| Back to Home link | `a:has-text("Back to Home"), text="Back to Home"` | Required |
| Sidebar Sessions link | `a:has-text("Sessions")` | Required — only nav item besides Messages |
| Sidebar Messages link | `a:has-text("Messages")` | Required |
| Sidebar Support link | `text="Support"` | Optional |
| Sidebar Language selector | `text="English"` | Optional |
| Account switcher (bottom) | `text="Child"` | Required — shows role badge "Child" |
| Upcoming/Past tabs | `button:has-text("Upcoming"), button:has-text("Past")` | Required on Sessions page |

## User Flows

### Flow 1: Successful Child Login
1. Navigate to https://dev.mehadedu.com/en/child-login
2. Enter username: Child
3. Enter password: 1234
4. Click "Login"
→ Expected: Toast "Login successful!", redirect to `/en/dashboard/sessions`, sidebar shows exactly Sessions + Messages

### Flow 2: Child Portal Shows Only Sessions and Messages
1. Log in as Child
2. Inspect the full sidebar
→ Expected: No links for Wallet, Payments, Settings, Profile, Bookings, Manage Children, Find Tutors, Become a Tutor, Admin, or Earnings anywhere in the DOM

### Flow 3: Navigate to Sessions Tabs
1. Log in as Child
2. Click "Upcoming" tab, then "Past" tab
→ Expected: Each tab loads without error; empty state shows "No upcoming sessions found." (or equivalent) when there is no data

### Flow 4: Back to Home From Login Page
1. Navigate to `/en/child-login`
2. Click "Back to Home"
→ Expected: Redirects to homepage `/en`, no session created

## Requirements
- REQ-01: `/en/child-login` must render a username+password form with no OTP/WhatsApp elements
- REQ-02: Correct credentials (Child/1234 on dev) authenticate and redirect to `/en/dashboard/sessions`
- REQ-03: Post-login sidebar must contain exactly two nav items: Sessions and Messages
- REQ-04: A child session must return 403/redirect (not 200 with content) when directly navigating to parent, student, tutor, or admin dashboard routes (e.g. `/en/dashboard/wallet`, `/en/dashboard/earnings`, `/en/admin-login`-authenticated routes)
- REQ-05: Password field must mask input by default with an optional show/hide toggle
- REQ-06: Login button must be disabled or show inline validation when username or password is empty
- REQ-07: Failed login must show an error message and must not redirect
- REQ-08: Child role badge/label "Child" must be visible in the account switcher after login
- REQ-09: Logging out from the child portal must fully clear the session (revisiting `/en/dashboard/sessions` afterwards redirects to `/en/child-login`)
- REQ-10: Page title must not contain 500 or 404

## Edge Cases
| EC-01 | Empty username, empty password, click Login | Login stays disabled or shows required-field errors |
| EC-02 | Correct username, wrong password | Inline error, no redirect, no session |
| EC-03 | Wrong username, correct password | Inline error, no redirect, no session |
| EC-04 | SQL injection in username (' OR '1'='1) | Rejected as invalid login, no 500, no auth bypass |
| EC-05 | XSS payload in username (<img src=x onerror=alert(1)>) | Rendered as literal text/escaped, no script execution, no auth bypass |
| EC-06 | Username with leading/trailing whitespace ("  Child  ") | Either trimmed and logs in, or rejected consistently — no crash |
| EC-07 | Extremely long username (300+ chars) | Input capped or rejected gracefully, no 500 |
| EC-08 | Direct URL access to `/en/dashboard/wallet` while authenticated as Child | Blocked — redirect or 403, wallet content never renders |
| EC-09 | Direct URL access to `/en/dashboard/earnings` (tutor-only) while authenticated as Child | Blocked — redirect or 403 |
| EC-10 | Direct URL access to `/en/admin-login`-gated admin route while authenticated as Child | Blocked — redirect or 403 |
| EC-11 | Repeated failed logins (5+ attempts) | Rate limiting or lockout messaging, no unbounded retry side-channel |
| EC-12 | Session token reused after logout (replay old cookie/localStorage token) | Server rejects stale session, redirect to login |
| EC-13 | Child account with zero sessions visits Sessions tab | Clean empty state, no console errors |
| EC-14 | Network failure during login submit | User-friendly error shown, form remains usable, no stuck spinner |

## Test Data
### Valid
| Field | Value |
|---|---|
| username | Child |
| password | 1234 |

### Invalid
| Field | Value |
|---|---|
| username | WrongChild |
| password | wrongpass |
| username | ' OR '1'='1 |
| username | <img src=x onerror=alert(1)> |
| username |   Child   |
| password |  |
