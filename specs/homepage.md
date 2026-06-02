# Homepage Spec

## Overview
The Mehad homepage is the public landing page for Saudi Arabia's #1 education platform. It features a hero section with a tutor search widget, a subject browser, how-it-works steps, top teachers carousel, student testimonials, and a CTA banner. The header contains the primary navigation, language switcher, and Log In button.

## URL
`/en`

## Roles
- Public (unauthenticated)
- Student (authenticated — Log In replaced by avatar)

## Prerequisites
- No login required for public view
- Student credentials: Bangladesh +880, phone 98976564, OTP 123456

## Test Scenarios

### HP-01: Page loads successfully
**Given** a user navigates to `https://dev.mehadedu.com/en`
**When** the page finishes loading
**Then** the page title contains "Mehad" and the hero heading "Learn with the Best Teachers in Saudi Arabia" is visible
**Selectors:**
- hero heading: `h1:has-text("Learn with the Best Teachers")`
- page title: document title should contain "Mehad"

### HP-02: Header nav links are present
**Given** the homepage is loaded
**When** the user inspects the header navigation
**Then** links for Home, Find Tutors, Become a Tutor, How It Works, About Us are visible
**Selectors:**
- nav: `nav`
- home link: `nav a[href="/en"]`
- find tutors button: `nav button:has-text("Find Tutors")`
- become tutor link: `nav a[href="/en/become-tutor"]`
- how it works link: `nav a[href="/en/how-mehad-works"]`
- about us link: `nav a[href="/en/about-us"]`

### HP-03: Log In button opens login modal
**Given** the homepage is loaded and user is not authenticated
**When** the user clicks the "Log In" button in the header
**Then** a dialog with heading "Welcome back" and subtitle "Sign in to continue" appears
**Selectors:**
- log in button: `button[data-variant="default"]:has-text("Log In")`
- modal dialog: `[role="dialog"]`
- modal heading: `[role="dialog"] h2:has-text("Welcome back")`
- modal subtitle: `[role="dialog"] p:has-text("Sign in to continue")`

### HP-04: Hero search widget has all four filters
**Given** the homepage is loaded
**When** the user views the hero search section
**Then** dropdowns for Subject, Level, Available Time, and Price Range are visible, plus a "Find a Teacher" button
**Selectors:**
- subject dropdown: `[data-section="hero"] combobox, combobox:has-text("Select subject")`
- level dropdown: `combobox:has-text("Select Level")`
- available time dropdown: `combobox:has-text("Select availability")`
- price range dropdown: `combobox:has-text("Select Price Range")`
- find teacher button: `button:has-text("Find a Teacher")`

### HP-05: Find a Teacher button navigates to find-tutors
**Given** the homepage hero section is visible
**When** the user clicks "Find a Teacher"
**Then** the browser navigates to `/en/find-tutors` (with optional query params)
**Selectors:**
- find teacher button: `button:has-text("Find a Teacher")`

### HP-06: Most Requested Subjects section shows subject cards
**Given** the homepage is loaded
**When** the user scrolls to the subjects section
**Then** at least 5 subject cards are visible with links to `/en/find-tutors?subjectId=X`
**Selectors:**
- section heading: `h2:has-text("Most Requested Subjects")`
- subject links: `a[href*="find-tutors?subjectId"]`
- physics link: `a[href="/en/find-tutors?subjectId=3"]`
- math link: `a[href="/en/find-tutors?subjectId=2"]`

### HP-07: Top Teachers section shows tutor cards with View All link
**Given** the homepage is loaded
**When** the user views the Our Top Teachers section
**Then** at least one tutor card is shown with a "View All" link to `/en/find-tutors`
**Selectors:**
- section heading: `h2:has-text("Our Top Teachers")`
- view all link: `a[href="/en/find-tutors"]:has-text("View All")`
- tutor card: `a[href*="/en/tutor/"]`

### HP-08: Tutor card links navigate to profile
**Given** the Top Teachers section is visible
**When** the user clicks a tutor card (e.g. Mr.Saymon)
**Then** the browser navigates to `/en/tutor/3`
**Selectors:**
- mr saymon card: `a[href="/en/tutor/3"]`

### HP-09: Student testimonials carousel is displayed
**Given** the homepage is loaded
**When** the user scrolls to the reviews section
**Then** the "What Our Students Say" heading and at least one testimonial are visible
**Selectors:**
- testimonials heading: `h2:has-text("What Our Students Say")`
- pause button: `button:has-text("pauseAutoplay"), button[aria-label*="pause"]`

### HP-10: CTA banner has Find tutor and Become tutor links
**Given** the homepage is loaded
**When** the user views the bottom CTA banner
**Then** "Find your tutor" link to /en/find-tutors and "Become a tutor" link to /en/become-tutor are both visible
**Selectors:**
- cta heading: `h2:has-text("Start Learning Today")`
- find tutor btn: `a[href="/en/find-tutors"] button`
- become tutor btn: `a[href="/en/become-tutor"] button`

### HP-11: Footer has all navigation sections
**Given** the homepage is loaded
**When** the user inspects the footer
**Then** sections EXPLORE, COMPANY, POLICIES are visible with correct links
**Selectors:**
- explore heading: `footer h3:has-text("EXPLORE"), h3:has-text("EXPLORE")`
- privacy policy link: `a[href="/en/privacy-policy"]`
- terms link: `a[href="/en/terms-conditions"]`
- refund link: `a[href="/en/refund-policy"]`
- cookie link: `a[href="/en/cookie-policy"]`

### HP-12: Language switcher toggles AR/EN
**Given** the homepage is loaded
**When** the user clicks the "العربية" (AR) button
**Then** the page language switches to Arabic (RTL layout)
**Selectors:**
- arabic button: `button:has-text("العربية")`
- english button: `button:has-text("English")`

### HP-13: Authenticated student sees avatar instead of Log In
**Given** a student is logged in
**When** the user navigates to the homepage
**Then** the header shows the student avatar/name instead of "Log In" button
**Selectors:**
- student avatar button: `button:has-text("Automations Student")`

### HP-14: Negative — No 404 or 500 errors on page load
**Given** any user navigates to `/en`
**When** the page finishes loading
**Then** no 404 or 500 error appears in the page title or content
**Selectors:**
- page title: `title`

### HP-15: Negative — Find tutors without filters returns results
**Given** the homepage hero search widget
**When** the user clicks "Find a Teacher" without selecting any filters
**Then** the page navigates to `/en/find-tutors` and shows tutor listings
**Selectors:**
- find teacher button: `button:has-text("Find a Teacher")`
- tutor count: `text=/\d+ tutors available/`
