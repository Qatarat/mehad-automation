# Contact Us Page Spec

**URL:** `https://dev.mehadedu.com/en/contact-us`

## Overview
The Contact Us page provides contact information and a message form for users to reach the Mehad support team. It displays business hours and a "Send us a message" form.

## URL
`/en/contact-us`

## Roles
- Public (unauthenticated)
- Student (authenticated)
- Teacher (authenticated)

## Prerequisites
- No login required to view or submit

## Test Scenarios

### CU-01: Page loads with correct heading
**Given** a user navigates to `https://dev.mehadedu.com/en/contact-us`
**When** the page finishes loading
**Then** the heading "Contact Us" and subtitle are visible
**Selectors:**
- main heading: `h1:has-text("Contact Us")`
- subtitle: `p:has-text("Our support team is always here to help you")`

### CU-02: Contact Information section is shown
**Given** the contact us page is loaded
**When** the user views the left column
**Then** the "Contact Information" heading and business hours note are visible
**Selectors:**
- contact info heading: `h2:has-text("Contact Information")`
- business hours: `p:has-text("business hours"), text="business hours"`

### CU-03: Message form is present
**Given** the contact us page is loaded
**When** the user views the right column
**Then** a "Send us a message" heading is visible along with form fields
**Selectors:**
- form heading: `h2:has-text("Send us a message")`

### CU-04: Negative — Form submission with empty fields shows validation
**Given** the contact us page is loaded
**When** the user attempts to submit the message form without filling required fields
**Then** validation errors are shown for required fields
**Selectors:**
- submit button: `button[type="submit"], button:has-text("Send")`
- error messages: `[aria-invalid="true"], text=/required|please fill/i`

### CU-05: Negative — Invalid email format shows error
**Given** the contact us form is visible
**When** the user enters an invalid email (e.g. "notanemail") and submits
**Then** a validation error is shown for the email field
**Selectors:**
- email input: `input[type="email"]`
- error: `[aria-invalid="true"], text=/valid email/i`
