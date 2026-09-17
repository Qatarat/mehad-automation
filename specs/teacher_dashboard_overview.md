# Teacher Dashboard Overview Spec

**URL:** `https://dev.mehadedu.com/en/dashboard/instructor-profile`

## Overview
CORRECTED 2026-09-17 after live verification against dev.mehadedu.com — the previous version of this spec was stale on every structural claim below (landing page, sidebar contents, and login credentials all no longer matched reality, which was the direct cause of the shared auth helper being broken; see `tutor_login_page.md` and the auth-fix commit).

The Teacher (Tutor) Dashboard is accessible after logging in via `/en/tutor-login` (email + OTP, not phone — see `tutor_login_page.md`). The teacher lands on **Instructor Profile** (`/en/dashboard/instructor-profile`), not an Availability Calendar page. "Availability" is a **tab inside** Instructor Profile (alongside Personal Information, Certificates & Expertise, Teaching Subjects), not a separate sidebar route. The live-verified sidebar contains exactly four items: **Sessions, Bookings, Instructor Profile, Messages** (Messages shows an unread-count badge). There is no separate "Group Sessions", "Earnings & Payouts", "Reviews", "Notifications", or "Help Center" sidebar link — if the app exposes those areas at all, they are elsewhere (e.g. a header bell icon was observed for notifications) and need their own live re-verification rather than being assumed here.

**Known follow-up:** the sibling specs `teacher_booked_sessions.md`, `teacher_earnings.md`, `teacher_group_sessions_page.md`, `teacher_notifications.md`, and `teacher_reviews_page.md` assume the same now-incorrect sidebar structure (standalone `/en/dashboard/earnings`, `/en/dashboard/reviews`, etc. routes) and should be re-verified against the live site the same way this file was, rather than trusted as-is.

## URL
`/en/dashboard/instructor-profile` (default landing after tutor login)

## Roles
- Tutor (authenticated)

## Prerequisites
- Tutor must be logged in via `/en/tutor-login`
- Tutor credentials (dev, live-verified): email `rumelmhmd@gmail.com`, OTP `6789`
- Expected tutor name (dev account): "Tester Teacher"
- Login redirects to: `/en/dashboard/instructor-profile`

## Test Scenarios

### TDO-01: After tutor login, redirects to Instructor Profile
**Given** a tutor completes OTP login at `/en/tutor-login`
**When** authentication succeeds
**Then** the browser navigates to `/en/dashboard/instructor-profile`
**Selectors:**
- post-login url: `/en/dashboard/instructor-profile`
- profile heading: `text="Instructor Profile"`
- approved badge: `text="Approved"`

### TDO-02: Tutor sidebar shows exactly its four navigation items
**Given** a tutor is logged into the dashboard
**When** the user views the sidebar
**Then** links for Sessions, Bookings, Instructor Profile, and Messages are present — and no links exist for a standalone Availability Calendar, Group Sessions, Earnings & Payouts, Reviews, or Notifications page (those are not separate sidebar routes)
**Selectors:**
- sessions link: `a:has-text("Sessions")`
- bookings link: `a:has-text("Bookings")`
- instructor profile link: `a:has-text("Instructor Profile")`
- messages link: `a:has-text("Messages")`
- messages unread badge: `a:has-text("Messages") >> text=/\\d+/`

### TDO-02b: Instructor Profile has four sub-tabs including Availability
**Given** a tutor is on the Instructor Profile page
**When** the user views the tab strip below the page heading
**Then** four tabs are shown: Personal Information, Certificates & Expertise, Teaching Subjects, and Availability
**Selectors:**
- personal info tab: `:text("Personal Information")`
- certificates tab: `:text("Certificates & Expertise")`
- subjects tab: `:text("Teaching Subjects")`
- availability tab: `:text("Availability")`

### TDO-03: Notifications badge shows unread count
**Given** a teacher has unread notifications
**When** the user views the sidebar Notifications item
**Then** a numeric badge with the unread count is shown on the Notifications link
**Selectors:**
- notifications badge: `a[href="/en/dashboard/notifications"] button`

### TDO-04: Account switcher shows teacher name and Tutor role
**Given** the teacher dashboard is loaded
**When** the user views the account switcher at the bottom of the sidebar
**Then** "Automations Tutor" and "Tutor" role label are displayed
**Selectors:**
- teacher name: `text="Automations Tutor"`
- tutor role: `text="Tutor"`

### TDO-05: Toggle Sidebar collapses sidebar
**Given** the teacher dashboard is loaded
**When** the user clicks "Toggle Sidebar"
**Then** the sidebar collapses or expands
**Selectors:**
- toggle: `button:has-text("Toggle Sidebar")`

### TDO-06: Mehad logo links to homepage
**Given** the teacher dashboard is loaded
**When** the user clicks the Mehad logo
**Then** the browser navigates to `/en`
**Selectors:**
- logo link: `a[href="/en"] img[alt="Mehad logo"]`

### TDO-07: Language switcher shows current language
**Given** the teacher dashboard is loaded
**When** the user views the language switcher in the sidebar
**Then** the current language (e.g. "English") is shown
**Selectors:**
- language switcher: `button:has-text("English"), button:has-text("Arabic")`

### TDO-08: Account switcher opens profile and logout options
**Given** the teacher is on the dashboard
**When** the user clicks "Open account switcher"
**Then** a dropdown with "My Profile" link and "Logout" button appears
**Selectors:**
- account switcher: `button[aria-label="Open account switcher"]`
- my profile link: `a[href="/en/dashboard/profile"], a:has-text("My Profile")`
- logout button: `button:has-text("Logout")`

### TDO-09: Logout navigates back to homepage
**Given** the teacher is logged in on the dashboard
**When** the user opens the account switcher and clicks "Logout"
**Then** the browser navigates to `/en` and the teacher is logged out
**Selectors:**
- logout: `button:has-text("Logout")`
- post-logout url: `/en`

### TDO-10: Negative — Unauthenticated access to teacher dashboard redirects
**Given** a user is not logged in
**When** the user navigates to `/en/dashboard/availability`
**Then** the user is redirected to the homepage or login page
**Selectors:**
- redirect: `/en` url or login page
