# Student Profile Page Spec

## Overview
The Student Profile page (`/en/dashboard/profile`) displays the student's name, role, avatar, contact information (email, location, phone, member since date). An "Edit Profile" button opens an edit form. A "Change Avatar" button allows profile picture updates. Accessible from Settings > Edit Profile.

## URL
`/en/dashboard/profile`

## Roles
- Student (authenticated)

## Prerequisites
- Student must be logged in: Bangladesh +880, phone 98976564, OTP 123456
- Test student: name "Automations Student", email "automationstudent@gmail.com", location "Bangladesh", phone "+88098976564", member since "May 2026"

## Test Scenarios

### SPR-01: Profile page loads with student name
**Given** a student is logged in and navigates to `/en/dashboard/profile`
**When** the page finishes loading
**Then** "My Profile" heading is shown and "Automations Student" name is visible
**Selectors:**
- page heading: `h1:has-text("My Profile")`
- student name: `h2:has-text("Automations Student")`
- role label: `text="Student Account"`

### SPR-02: Profile info section shows all fields
**Given** the student profile page is loaded
**When** the user views the profile information section
**Then** Email, Location, Phone, and Member Since fields are all displayed with values
**Selectors:**
- email label: `text="Email"`
- email value: `text="automationstudent@gmail.com"`
- location label: `text="Location"`
- phone label: `text="Phone"`
- member since label: `text="Member Since"`

### SPR-03: Change Avatar button is visible
**Given** the student profile page is loaded
**When** the user views the avatar area
**Then** a "Change Avatar" button overlaid on the profile image is visible
**Selectors:**
- change avatar button: `button:has-text("Change Avatar")`
- profile avatar: `img[alt="Profile Avatar"]`

### SPR-04: Edit Profile button opens edit form or modal
**Given** the student profile page is loaded
**When** the user clicks "Edit Profile"
**Then** an edit form or modal appears allowing profile fields to be changed
**Selectors:**
- edit profile button: `button:has-text("Edit Profile")`

### SPR-05: Profile accessible from Settings > Edit Profile
**Given** the student is on the Settings page (`/en/dashboard/settings`)
**When** the user clicks the "Edit Profile" list item
**Then** the browser navigates to `/en/dashboard/profile`
**Selectors:**
- settings url: `/en/dashboard/settings`
- edit profile item: `li:has-text("Edit Profile")`
- profile heading: `h1:has-text("My Profile")`

### SPR-06: Negative — Unauthenticated access redirects
**Given** a user is not logged in
**When** the user navigates to `/en/dashboard/profile`
**Then** the user is redirected to the homepage or shown a login prompt
**Selectors:**
- redirect: `/en` url or login modal
