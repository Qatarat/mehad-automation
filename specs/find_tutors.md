# Find Tutors Page Spec

**URL:** `https://dev.mehadedu.com/en/find-tutors`

## Overview
The Find Tutors page is the public tutor directory. It lists all approved tutors with search, filter, sort, and pagination (Load more). Each tutor card shows rating, subject, student count, lesson count, languages, bio excerpt, price, and action buttons (Book Trial Lesson, Message, Save). When unauthenticated, Book Trial Lesson and Message trigger the login modal.

## URL
`/en/find-tutors`

## Roles
- Public (unauthenticated)
- Student (authenticated)

## Prerequisites
- No login required to browse
- Student credentials: Bangladesh +880, phone 98976564, OTP 123456
- URL auto-appends query params: `?page=1&limit=10&sortBy=createdAt&sortOrder=DESC&sort=top`

## Test Scenarios

### FT-01: Page loads and shows tutor count
**Given** a user navigates to `https://dev.mehadedu.com/en/find-tutors`
**When** the page finishes loading
**Then** the heading "Find your perfect tutor" and a tutor count like "65 tutors available" are visible
**Selectors:**
- heading: `h1:has-text("Find your perfect tutor")`
- tutor count: `text=/\d+ tutors available/`

### FT-02: Filter bar has all four filters
**Given** the find tutors page is loaded
**When** the user inspects the filter bar
**Then** dropdowns for Subject, Level, Price, and Available times are visible plus a keyword search box
**Selectors:**
- subject dropdown: `combobox:has-text("All Subjects")`
- level dropdown: `combobox:has-text("All Levels")`
- price dropdown: `combobox:has-text("Any price")`
- time dropdown: `combobox:has-text("Any time")`
- search box: `input[placeholder="Search tutors..."]`

### FT-03: Sort dropdown is present and defaults to Our top picks
**Given** the find tutors page is loaded
**When** the user inspects the sort control
**Then** a sort dropdown showing "Our top picks" is visible
**Selectors:**
- sort label: `text="Sort by:"`
- sort dropdown: `combobox:has-text("Our top picks")`

### FT-04: Each tutor card has required elements
**Given** the find tutors page is loaded
**When** the user views any tutor card
**Then** the card shows tutor name, rating, review count, subject, student count, lesson count, language list, bio snippet, price, and three action buttons
**Selectors:**
- tutor name: `.text-xl, .font-bold, h3`
- rating: `img[alt="SAR"] ~ *` (price context)
- book trial button: `button:has-text("Book Trial Lesson")`
- message button: `button:has-text("Message")`
- save button: `button:has-text("save")`

### FT-05: Load more button fetches additional tutors
**Given** the find tutors page shows 10 tutors initially
**When** the user clicks the "Load more" button
**Then** additional tutor cards are appended to the list
**Selectors:**
- load more button: `button:has-text("Load more")`

### FT-06: Filtering by subject narrows results
**Given** the find tutors page is loaded
**When** the user selects a subject from the Subject dropdown (e.g. "Math")
**Then** only tutors teaching that subject are shown and the URL reflects the filter
**Selectors:**
- subject dropdown: `combobox:has-text("All Subjects")`

### FT-07: Keyword search filters tutors by name
**Given** the find tutors page is loaded
**When** the user types a tutor name into the search box
**Then** only matching tutors are shown
**Selectors:**
- search input: `input[placeholder="Search tutors..."]`

### FT-08: Tutor card click navigates to tutor profile
**Given** the find tutors page shows tutor cards
**When** the user clicks on a tutor card body (not a button)
**Then** the browser navigates to `/en/tutor/{id}`
**Selectors:**
- tutor card container: `[cursor=pointer]` (clickable container wrapping each card)

### FT-09: Negative — Book Trial Lesson when unauthenticated opens login modal
**Given** a user is not logged in and on the find tutors page
**When** the user clicks "Book Trial Lesson" on any tutor card
**Then** the login modal opens with heading "Welcome back"
**Selectors:**
- book trial button: `button:has-text("Book Trial Lesson")`
- login modal: `[role="dialog"] h2:has-text("Welcome back")`

### FT-10: Negative — Message button when unauthenticated opens login modal
**Given** a user is not logged in and on the find tutors page
**When** the user clicks "Message" on any tutor card
**Then** the login modal opens
**Selectors:**
- message button: `button:has-text("Message")`
- login modal: `[role="dialog"]`

### FT-11: Negative — Save button when unauthenticated opens login modal
**Given** a user is not logged in and on the find tutors page
**When** the user clicks the "save" (heart/bookmark) button on any tutor card
**Then** the login modal opens
**Selectors:**
- save button: `button:has-text("save")`
- login modal: `[role="dialog"]`

### FT-12: Subject filter via URL query param works
**Given** a user navigates to `/en/find-tutors?subjectId=2`
**When** the page loads
**Then** only tutors for Math (subjectId=2) are shown and the subject dropdown reflects "Math"
**Selectors:**
- heading: `h1:has-text("Find your perfect tutor")`
- tutor list: `text=/\d+ tutors available/`

### FT-13: Negative — No tutors match search term
**Given** the find tutors page is loaded
**When** the user types a name that matches no tutor (e.g. "zzznomatch")
**Then** an empty state or "0 tutors available" message is displayed
**Selectors:**
- search input: `input[placeholder="Search tutors..."]`
- empty state: `text=/0 tutors|no tutors|no results/i`
