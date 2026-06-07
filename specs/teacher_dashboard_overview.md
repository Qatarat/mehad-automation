# Teacher Dashboard Overview Spec

**URL:** `https://dev.mehadedu.com/en/dashboard/availability`

## Overview
The Teacher (Tutor) Dashboard is accessible after logging in via `/en/tutor-login`. The teacher lands on the Availability Calendar (`/en/dashboard/availability`). The sidebar provides navigation to: Availability Calendar, Booked Sessions, Group Sessions, Messages, Earnings & Payouts, Reviews, Notifications (with unread badge), Instructor Profile, and Help Center. The account switcher shows the tutor name and role.

## URL
`/en/dashboard/availability` (default landing after teacher login)

## Roles
- Teacher (authenticated)

## Prerequisites
- Teacher must be logged in via `/en/tutor-login`
- Teacher credentials: Bangladesh +880, phone 98976564, OTP 123456
- Expected teacher name: "Automations Tutor"
- Login redirects to: `/en/dashboard/availability`

## Test Scenarios

### TDO-01: After teacher login, redirects to availability calendar
**Given** a teacher completes OTP login at `/en/tutor-login`
**When** authentication succeeds
**Then** the browser navigates to `/en/dashboard/availability`
**Selectors:**
- post-login url: `/en/dashboard/availability`
- availability heading: `text="Availability Calendar"`

### TDO-02: Teacher sidebar shows all navigation items
**Given** a teacher is logged into the dashboard
**When** the user views the sidebar
**Then** links for Availability Calendar, Booked Sessions, Group Sessions, Messages, Earnings & Payouts, Reviews, Notifications, Instructor Profile, and Help Center are all present
**Selectors:**
- availability link: `a[href="/en/dashboard/availability"]`
- booked sessions link: `a[href="/en/dashboard/booked-sessions"]`
- group sessions link: `a[href="/en/dashboard/group-sessions"]`
- messages link: `a[href="/en/dashboard/messages"]`
- earnings link: `a[href="/en/dashboard/earnings"]`
- reviews link: `a[href="/en/dashboard/reviews"]`
- notifications link: `a[href="/en/dashboard/notifications"]`
- instructor profile link: `a[href="/en/dashboard/instructor-profile"]`
- help center link: `a[href="/en/dashboard/help-center"]`

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
