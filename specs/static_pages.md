# Static Public Pages Spec

## Overview
These are informational static pages accessible to all users without login. They include How It Works, About Us, FAQs, Pricing, Subjects directory, Privacy Policy, Terms & Conditions, Refund Policy, and Cookie Policy.

## Roles
- Public (unauthenticated)

## Prerequisites
- No login required

## Test Scenarios

### SP-01: How It Works page loads
**Given** a user navigates to `https://dev.mehadedu.com/en/how-mehad-works`
**When** the page finishes loading
**Then** the page loads without errors and shows explanatory content
**Selectors:**
- url: `/en/how-mehad-works`
- no 404: `title:not(:has-text("404"))`

### SP-02: About Us page loads
**Given** a user navigates to `https://dev.mehadedu.com/en/about-us`
**When** the page finishes loading
**Then** the page loads without a 404 or 500 error
**Selectors:**
- url: `/en/about-us`

### SP-03: FAQs page loads and shows accordion
**Given** a user navigates to `https://dev.mehadedu.com/en/faqs`
**When** the page finishes loading
**Then** an FAQ section with expandable questions is shown
**Selectors:**
- url: `/en/faqs`
- faq items: `[role="button"], details, [data-state]`

### SP-04: Pricing page loads
**Given** a user navigates to `https://dev.mehadedu.com/en/pricing`
**When** the page finishes loading
**Then** the page loads without errors and shows pricing information
**Selectors:**
- url: `/en/pricing`

### SP-05: Subjects page loads
**Given** a user navigates to `https://dev.mehadedu.com/en/subjects`
**When** the page finishes loading
**Then** the page loads without errors and shows a list of subjects
**Selectors:**
- url: `/en/subjects`

### SP-06: Privacy Policy page loads
**Given** a user navigates to `https://dev.mehadedu.com/en/privacy-policy`
**When** the page finishes loading
**Then** the page loads and shows privacy policy content
**Selectors:**
- url: `/en/privacy-policy`
- heading: `h1, h2`

### SP-07: Terms & Conditions page loads
**Given** a user navigates to `https://dev.mehadedu.com/en/terms-conditions`
**When** the page finishes loading
**Then** the page loads and shows terms content
**Selectors:**
- url: `/en/terms-conditions`

### SP-08: Refund Policy page loads
**Given** a user navigates to `https://dev.mehadedu.com/en/refund-policy`
**When** the page finishes loading
**Then** the page loads and shows refund policy content
**Selectors:**
- url: `/en/refund-policy`

### SP-09: Cookie Policy page loads
**Given** a user navigates to `https://dev.mehadedu.com/en/cookie-policy`
**When** the page finishes loading
**Then** the page loads and shows cookie policy content
**Selectors:**
- url: `/en/cookie-policy`

### SP-10: Footer links on homepage navigate to correct static pages
**Given** the homepage is loaded
**When** the user clicks footer policy links
**Then** each link navigates to the correct page without 404
**Selectors:**
- privacy link: `a[href="/en/privacy-policy"]`
- terms link: `a[href="/en/terms-conditions"]`
- refund link: `a[href="/en/refund-policy"]`
- cookie link: `a[href="/en/cookie-policy"]`
- subjects link: `a[href="/en/subjects"]`
- pricing link: `a[href="/en/pricing"]`

### SP-11: Footer Blog and Careers links exist
**Given** the homepage is loaded
**When** the user inspects the COMPANY section of the footer
**Then** Blog and Careers links are visible
**Selectors:**
- blog link: `a[href="/en/blog"]`
- careers link: `a[href="/en/careers"]`

### SP-12: Negative — Non-existent page shows 404
**Given** a user navigates to a non-existent URL like `/en/nonexistent-page-xyz`
**When** the page loads
**Then** a "Page Not Found" or 404 message is displayed
**Selectors:**
- not found heading: `h1:has-text("Page Not Found"), text=/404/`
