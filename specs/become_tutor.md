# Become a Tutor Page Spec

**URL:** `https://dev.mehadedu.com/en/become-tutor`

## Overview
The Become a Tutor landing page is a public marketing page that explains the benefits of teaching on Mehad, the 4-step process, requirements, and has a CTA "Apply Now" button that navigates to `/en/tutor-login` to start the registration flow.

## URL
`/en/become-tutor`

## Roles
- Public (unauthenticated)

## Prerequisites
- No login required

## Test Scenarios

### BT-01: Page loads with correct heading
**Given** a user navigates to `https://dev.mehadedu.com/en/become-tutor`
**When** the page finishes loading
**Then** the heading "Become a tutor on Mehad" is visible
**Selectors:**
- main heading: `h1:has-text("Become a tutor on Mehad")`

### BT-02: Why Choose Mehad section has four benefit cards
**Given** the become a tutor page is loaded
**When** the user views the "Why choose Mehad?" section
**Then** four benefit cards are shown: Earn Good Income, Flexible Schedule, Global Students, Professional Growth
**Selectors:**
- section heading: `h2:has-text("Why choose Mehad?")`
- earn income: `text="Earn Good Income"`
- flexible schedule: `text="Flexible Schedule"`
- global students: `text="Global Students"`
- professional growth: `text="Professional Growth"`

### BT-03: How to become a tutor section has four numbered steps
**Given** the become a tutor page is loaded
**When** the user views the process section
**Then** four numbered steps are shown: Create Your Account, Set Your Schedule, Receive Requests, Start Teaching
**Selectors:**
- steps heading: `h2:has-text("How to become a tutor")`
- step 1: `text="Create Your Account"`
- step 2: `text="Set Your Schedule"`
- step 3: `text="Receive Requests"`
- step 4: `text="Start Teaching"`

### BT-04: Requirements section is visible
**Given** the become a tutor page is loaded
**When** the user views the requirements section
**Then** requirements including "Teaching experience or relevant degree" are listed
**Selectors:**
- requirements heading: `h2:has-text("Requirements")`
- teaching experience: `text="Teaching experience or relevant degree"`

### BT-05: Apply Now button navigates to tutor-login
**Given** the become a tutor page is loaded
**When** the user clicks "Apply Now"
**Then** the browser navigates to `/en/tutor-login`
**Selectors:**
- apply now link: `a[href="/en/tutor-login"]`
- apply now button: `a[href="/en/tutor-login"] button:has-text("Apply Now")`

### BT-06: Negative — No broken links or 500 errors
**Given** a user navigates to `/en/become-tutor`
**When** the page loads
**Then** no 404 or 500 error appears in the page title or body
**Selectors:**
- page title: `title`
