# Teacher Group Sessions Page Spec

## Overview
The Group Sessions page (`/en/dashboard/group-sessions`) is where teachers manage their group session offerings. It shows a "Group Sessions" heading. When no sessions exist, it displays "No group sessions found". Group sessions are created from the Availability Calendar using the "Group sessions" button.

## URL
`/en/dashboard/group-sessions`

## Roles
- Teacher (authenticated)

## Prerequisites
- Teacher must be logged in: Bangladesh +880, phone 98976564, OTP 123456

## Test Scenarios

### TGS-01: Page loads with Group Sessions heading
**Given** a teacher is logged in and navigates to `/en/dashboard/group-sessions`
**When** the page finishes loading
**Then** the "Group Sessions" heading is visible
**Selectors:**
- heading: `h1:has-text("Group Sessions")`

### TGS-02: Empty state shown when no group sessions
**Given** the teacher has no group sessions
**When** the teacher views the group sessions page
**Then** "No group sessions found" message is displayed
**Selectors:**
- empty state: `text="No group sessions found"`

### TGS-03: Group session cards show when sessions exist
**Given** the teacher has created group sessions
**When** the teacher views the group sessions page
**Then** group session cards with course name, date/time, enrolled count, and price are shown
**Selectors:**
- session card: `[class*="session-card"], [data-testid="group-session"]`

### TGS-04: Group sessions created from Availability Calendar
**Given** the teacher is on the Availability Calendar page
**When** the user clicks "Group sessions" button
**Then** a 3-step modal opens for creating a group session
**Selectors:**
- group sessions button: `button:has-text("Group sessions")`
- modal: `[role="dialog"]`

### TGS-05: Navigation to Group Sessions from sidebar works
**Given** the teacher is on any dashboard page
**When** the user clicks the "Group Sessions" sidebar link
**Then** the browser navigates to `/en/dashboard/group-sessions`
**Selectors:**
- group sessions link: `a[href="/en/dashboard/group-sessions"]`

### TGS-06: Negative — Unauthenticated access redirects
**Given** a user is not logged in
**When** the user navigates to `/en/dashboard/group-sessions`
**Then** the user is redirected to the homepage or login
**Selectors:**
- redirect: `/en` url
