# Teacher Instructor Profile Edit Spec

## Overview
The Instructor Profile page (`/en/dashboard/instructor-profile`) allows teachers to manage their public profile. It has three tabs: Personal Information, Certificates & Expertise, and Teaching Subjects. A Public Availability toggle controls visibility on the platform. The Personal Information tab shows name, title, bio, location, languages, and has an "Edit Profile" button that opens an edit form.

## URL
`/en/dashboard/instructor-profile`

## Roles
- Teacher (authenticated)

## Prerequisites
- Teacher must be logged in: Bangladesh +880, phone 98976564, OTP 123456
- Teacher name: "Automations Tutor"

## Test Scenarios

### TIP-01: Page loads with Instructor Profile heading
**Given** a teacher is logged in and navigates to `/en/dashboard/instructor-profile`
**When** the page finishes loading
**Then** the "Instructor Profile" heading is visible
**Selectors:**
- heading: `h1:has-text("Instructor Profile")`

### TIP-02: Three profile tabs are shown
**Given** the instructor profile page is loaded
**When** the user views the tab bar
**Then** three tabs are visible: Personal Information, Certificates & Expertise, Teaching Subjects
**Selectors:**
- personal info tab: `[role="tab"]:has-text("Personal Information")`
- certificates tab: `[role="tab"]:has-text("Certificates & Expertise")`
- teaching subjects tab: `[role="tab"]:has-text("Teaching Subjects")`

### TIP-03: Public Availability toggle is present
**Given** the instructor profile page is loaded
**When** the user views the header area
**Then** a "Public Availability" label and a toggle switch are visible
**Selectors:**
- availability label: `text="Public Availability"`
- toggle: `[role="switch"]`

### TIP-04: Personal Information tab shows profile data
**Given** the instructor profile page is loaded and Personal Information tab is active
**When** the user views the tab content
**Then** the "Personal Information" section heading and "Edit Profile" button are visible, plus bio, name, location fields
**Selectors:**
- section heading: `h3:has-text("Personal Information")`
- edit profile button: `button:has-text("Edit Profile")`

### TIP-05: Edit Profile button opens edit form
**Given** the instructor profile page is loaded
**When** the user clicks "Edit Profile"
**Then** an edit form or modal appears with editable fields for name, bio, location, etc.
**Selectors:**
- edit profile button: `button:has-text("Edit Profile")`
- edit form: `[role="dialog"], form, input[name="firstName"]`

### TIP-06: Certificates & Expertise tab is navigable
**Given** the instructor profile page is loaded
**When** the user clicks the "Certificates & Expertise" tab
**Then** the tab panel switches to show certificate/expertise fields
**Selectors:**
- certificates tab: `[role="tab"]:has-text("Certificates & Expertise")`
- panel: `[role="tabpanel"]`

### TIP-07: Teaching Subjects tab is navigable
**Given** the instructor profile page is loaded
**When** the user clicks the "Teaching Subjects" tab
**Then** the tab panel switches to show subject management options
**Selectors:**
- teaching tab: `[role="tab"]:has-text("Teaching Subjects")`
- panel: `[role="tabpanel"]`

### TIP-08: Toggle Public Availability turns tutor on/off
**Given** the instructor profile page is loaded
**When** the user clicks the Public Availability toggle
**Then** the toggle state changes (checked/unchecked) and the profile visibility updates accordingly
**Selectors:**
- toggle: `[role="switch"]`

### TIP-09: Profile saves successfully after editing
**Given** the instructor edit form is open with valid data
**When** the user modifies a field and saves
**Then** a success toast or confirmation message appears
**Selectors:**
- success toast: `[role="alert"], text=/saved|updated|success/i`

### TIP-10: Negative — Empty required field in edit form shows error
**Given** the instructor edit form is open
**When** the user clears a required field (e.g. First Name) and attempts to save
**Then** a validation error is shown for that field
**Selectors:**
- first name input: `input[name="firstName"]`
- error: `[aria-invalid="true"], text=/required|can't be empty/i`

### TIP-11: Negative — Unauthenticated access redirects
**Given** a user is not logged in
**When** the user navigates to `/en/dashboard/instructor-profile`
**Then** the user is redirected to the homepage or login
**Selectors:**
- redirect: `/en` url
