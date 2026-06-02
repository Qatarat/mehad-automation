# Teacher Booked Sessions Spec

## Overview
The Booked Sessions page (`/en/dashboard/booked-sessions`) shows all sessions booked with the teacher. It has tabs for Upcoming Sessions and Session History, a keyword search box, and a Filters button. Displays empty state "No upcoming sessions found" when there are no bookings.

## URL
`/en/dashboard/booked-sessions`

## Roles
- Teacher (authenticated)

## Prerequisites
- Teacher must be logged in: Bangladesh +880, phone 98976564, OTP 123456

## Test Scenarios

### TBS-01: Page loads with All Sessions heading
**Given** a teacher is logged in and navigates to `/en/dashboard/booked-sessions`
**When** the page finishes loading
**Then** the "All Sessions" heading area is visible
**Selectors:**
- all sessions: `text="All Sessions", img + text="All Sessions"`

### TBS-02: Upcoming Sessions and Session History tabs are shown
**Given** the booked sessions page is loaded
**When** the user views the tab controls
**Then** "Upcoming Sessions" and "Session History" buttons are visible
**Selectors:**
- upcoming tab: `button:has-text("Upcoming Sessions")`
- history tab: `button:has-text("Session History")`

### TBS-03: Search box is present
**Given** the booked sessions page is loaded
**When** the user views the search bar
**Then** a text input with placeholder "Search sessions..." is visible
**Selectors:**
- search input: `input[placeholder="Search sessions..."]`

### TBS-04: Filters button is present
**Given** the booked sessions page is loaded
**When** the user views the filter controls
**Then** a "Filters" button is visible
**Selectors:**
- filters button: `button:has-text("Filters")`

### TBS-05: Empty state message shown when no sessions
**Given** the teacher has no booked sessions
**When** the teacher views the booked sessions page
**Then** "No upcoming sessions found" message is displayed
**Selectors:**
- empty state: `text="No upcoming sessions found"`

### TBS-06: Session History tab switches content
**Given** the booked sessions page is loaded
**When** the user clicks "Session History"
**Then** the content area shows completed/past session records or an empty state
**Selectors:**
- history tab: `button:has-text("Session History")`

### TBS-07: Filters button opens filter panel
**Given** the booked sessions page is loaded
**When** the user clicks "Filters"
**Then** a filter panel or dropdown opens with filter options
**Selectors:**
- filters button: `button:has-text("Filters")`
- filter panel: `[role="dialog"], [data-state="open"]`

### TBS-08: Keyword search filters sessions in real time
**Given** the teacher has booked sessions
**When** the user types a student name or subject in the search box
**Then** only matching sessions are shown
**Selectors:**
- search input: `input[placeholder="Search sessions..."]`

### TBS-09: Negative — Unauthenticated access redirects
**Given** a user is not logged in
**When** the user navigates to `/en/dashboard/booked-sessions`
**Then** the user is redirected to the homepage or login
**Selectors:**
- redirect: `/en` url
