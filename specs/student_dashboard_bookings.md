# Student Dashboard — My Bookings Spec

## Overview
The My Bookings page is the student's session management hub. It shows a greeting, unbooked hours counter, tabs for Upcoming Sessions and Session History, and a CTA to Browse & Book Sessions when there are no bookings. Accessible only to authenticated students.

## URL
`/en/dashboard/bookings`

## Roles
- Student (authenticated)

## Prerequisites
- Student must be logged in: Bangladesh +880, phone 98976564, OTP 123456
- Expected student name: "Automations Student"
- Sidebar links: My Bookings, Messages, Favorite Teachers, Payment & Wallet, Reviews & Ratings, Settings, Help Center

## Test Scenarios

### SDB-01: Page redirects unauthenticated users to login
**Given** a user is not logged in
**When** the user navigates to `/en/dashboard/bookings`
**Then** the user is redirected to the homepage or login page
**Selectors:**
- redirect url: `/en` or `[role="dialog"]:has-text("Welcome back")`

### SDB-02: Authenticated student sees greeting and booking page
**Given** a student is logged in
**When** the student navigates to `/en/dashboard/bookings`
**Then** "Hello Automations Student" heading and "Manage your upcoming and past sessions" subtitle are visible
**Selectors:**
- greeting: `h1:has-text("Hello Automations Student")`
- subtitle: `p:has-text("Manage your upcoming and past sessions")`

### SDB-03: Sidebar shows all student navigation items
**Given** a student is on the dashboard
**When** the user views the sidebar
**Then** links for My Bookings, Messages, Favorite Teachers, Payment & Wallet, Reviews & Ratings, Settings, Help Center are all present
**Selectors:**
- my bookings link: `a[href="/en/dashboard/bookings"]`
- messages link: `a[href="/en/dashboard/messages"]`
- favorites link: `a[href="/en/dashboard/favorites"]`
- wallet link: `a[href="/en/dashboard/wallet"]`
- reviews link: `a[href="/en/dashboard/reviews"]`
- settings link: `a[href="/en/dashboard/settings"]`
- help center link: `a[href="/en/dashboard/help-center"]`

### SDB-04: Unbooked hours counter is shown
**Given** the student is on the bookings page
**When** the user views the top section
**Then** an "Unbooked X.X hours" button/badge is visible
**Selectors:**
- unbooked button: `button:has-text("Unbooked")`

### SDB-05: Upcoming Sessions and Session History tabs are present
**Given** the student is on the bookings page
**When** the user views the tabs section
**Then** "Upcoming Sessions" and "Session History" tab buttons are visible
**Selectors:**
- upcoming tab: `button:has-text("Upcoming Sessions")`
- history tab: `button:has-text("Session History")`

### SDB-06: Empty state shows Browse & Book CTA
**Given** the student has no bookings
**When** the student views the bookings page
**Then** "Find Your Perfect Teacher" section with "Browse & Book Sessions" button linking to `/en/find-tutors` is shown
**Selectors:**
- cta heading: `h2:has-text("Find Your Perfect Teacher")`
- browse button: `a[href="/en/find-tutors"] button:has-text("Browse & Book Sessions")`
- empty message: `text="Book your first session to get started!"`

### SDB-07: Session History tab switches view
**Given** the student is on the bookings page
**When** the user clicks "Session History" tab
**Then** the view switches to show completed/past sessions (or empty state)
**Selectors:**
- history tab: `button:has-text("Session History")`

### SDB-08: Sidebar logo links back to homepage
**Given** the student is on the dashboard
**When** the user clicks the Mehad logo in the sidebar
**Then** the browser navigates to `/en`
**Selectors:**
- logo link: `a[href="/en"] img[alt="Mehad logo"]`

### SDB-09: Account switcher shows student name and role
**Given** the student is on the dashboard
**When** the user views the bottom of the sidebar
**Then** the account switcher shows "Automations Student" and "Student" role label
**Selectors:**
- student name: `text="Automations Student"`
- student role: `text="Student"`

### SDB-10: Toggle Sidebar button collapses/expands sidebar
**Given** the student dashboard is loaded
**When** the user clicks the "Toggle Sidebar" button
**Then** the sidebar collapses or expands
**Selectors:**
- toggle button: `button:has-text("Toggle Sidebar")`

### SDB-11: Negative — Student dashboard URL (old path) returns 404
**Given** a user navigates to `/en/student/dashboard`
**When** the page loads
**Then** a "Page Not Found" message is displayed (correct path is `/en/dashboard/bookings`)
**Selectors:**
- not found: `h1:has-text("Page Not Found")`
