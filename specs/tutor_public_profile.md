# Tutor Public Profile Spec

## Overview
The public tutor profile page shows full tutor details: header with name, bio, stats (lessons taught, average rating, response rate), booking widget (1-to-1 and Group Session tabs), subject/price selector, weekly availability calendar with timezone switcher, introduction video, about section (languages, subjects with details, specialties, education, certifications), and student reviews.

## URL
`/en/tutor/{id}`

## Roles
- Public (unauthenticated)
- Student (authenticated)

## Prerequisites
- No login required to view
- Test tutor profile: `/en/tutor/3` (Mr.Saymon, Algebra/Math)
- Student credentials: Bangladesh +880, phone 98976564, OTP 123456

## Test Scenarios

### TP-01: Profile page loads with tutor name visible
**Given** a user navigates to `https://dev.mehadedu.com/en/tutor/3`
**When** the page finishes loading
**Then** the tutor name "Mr.Saymon" is displayed in the profile header
**Selectors:**
- tutor name heading: `h3:has-text("Mr.Saymon"), h2:has-text("Mr.Saymon")`
- back link: `text="Back to search"`

### TP-02: Profile stats section shows three metrics
**Given** the tutor profile page is loaded
**When** the user views the stats bar
**Then** Lessons Taught, Average Rating, and Response Rate are displayed with values
**Selectors:**
- lessons taught: `text="Lessons Taught"`
- average rating: `text="Average Rating"`
- response rate: `text="Response Rate"`

### TP-03: Booking widget has 1-to-1 and Group Session tabs
**Given** the tutor profile page is loaded
**When** the user inspects the booking widget
**Then** two tabs "1-to-1" and "Group Session" are visible
**Selectors:**
- one-to-one tab: `button:has-text("1-to-1")`
- group session tab: `button:has-text("Group Session")`

### TP-04: Subject radio buttons show subjects and prices
**Given** the tutor profile is loaded and "1-to-1" tab is active
**When** the user views the subject section
**Then** radio buttons for each subject with SAR price per hour are displayed
**Selectors:**
- algebra radio: `input[type="radio"] + * :has-text("Algebra")`
- math radio: `input[type="radio"] + * :has-text("Math")`

### TP-05: Weekly availability calendar is shown
**Given** the tutor profile is loaded
**When** the user views the schedule section
**Then** a weekly calendar showing Mon-Sat columns with date numbers is visible, plus Prev week / Next week navigation buttons
**Selectors:**
- schedule heading: `text="Schedule"`
- prev week button: `button:has-text("Prev week"), button[aria-label*="Prev"]`
- next week button: `button:has-text("Next week"), button[aria-label*="Next"]`
- week range: `text=/\w+ \d+ – \w+ \d+/`

### TP-06: Timezone dropdown is present and functional
**Given** the tutor profile is loaded
**When** the user inspects the timezone selector
**Then** a combobox showing the current timezone (e.g. "Asia/Dhaka") is visible
**Selectors:**
- timezone combobox: `combobox:has-text("Asia/")`

### TP-07: Book Trial Lesson button is visible
**Given** the tutor profile is loaded
**When** the user views the booking widget
**Then** a "Book Trial Lesson" button is visible below the calendar
**Selectors:**
- book trial button: `button:has-text("Book Trial Lesson")`

### TP-08: Save (favorite) and Message buttons are present
**Given** the tutor profile is loaded
**When** the user views the top action buttons
**Then** a "save" button and a "Message" button are visible
**Selectors:**
- save button: `button:has-text("save")`
- message button: `button:has-text("Message")`

### TP-09: About Me section shows bio, languages, subjects, education, certifications
**Given** the tutor profile is loaded
**When** the user scrolls to the About section
**Then** all subsections (About me, Languages, Subjects, Specialties, Education, Certifications) are present
**Selectors:**
- about me heading: `text="About me"`
- languages section: `text="Languages"`
- subjects section: `text="Subjects"`
- specialties section: `text="Specialties / Expertise"`
- education section: `text="Education"`
- certifications section: `text="Certifications"`

### TP-10: Student Reviews section shows rating summary
**Given** the tutor profile is loaded
**When** the user scrolls to the Student Reviews section
**Then** the average rating and review count are shown
**Selectors:**
- reviews heading: `text="Student Reviews"`
- rating display: `text=/\d+\.\d+/` (numeric rating)

### TP-11: Negative — Book Trial Lesson when unauthenticated opens login
**Given** a user is not logged in and views a tutor profile
**When** the user clicks "Book Trial Lesson"
**Then** the login modal appears with "Welcome back" heading
**Selectors:**
- book trial button: `button:has-text("Book Trial Lesson")`
- login modal: `[role="dialog"] h2:has-text("Welcome back")`

### TP-12: Negative — Message when unauthenticated opens login modal
**Given** a user is not logged in and views a tutor profile
**When** the user clicks "Message"
**Then** the login modal appears
**Selectors:**
- message button: `button:has-text("Message")`
- login modal: `[role="dialog"]`

### TP-13: Negative — Invalid tutor ID shows 404 or redirect
**Given** a user navigates to a tutor profile with a non-existent ID (e.g. `/en/tutor/99999`)
**When** the page loads
**Then** a 404 or "not found" message is displayed, or user is redirected
**Selectors:**
- not found: `text=/not found|404/i`
