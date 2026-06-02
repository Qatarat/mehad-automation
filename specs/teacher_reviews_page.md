# Teacher Reviews Page Spec

## Overview
The Teacher Reviews page (`/en/dashboard/reviews`) shows a review summary with Average Rating, Total Reviews, and 5-Star Reviews percentage. A Rating Distribution section shows star-by-star breakdown. A search box and star filter buttons (All, 5★, 4★, 3★, 2★, 1★) allow filtering. Shows "No reviews found" when empty.

## URL
`/en/dashboard/reviews`

## Roles
- Teacher (authenticated)

## Prerequisites
- Teacher must be logged in: Bangladesh +880, phone 98976564, OTP 123456

## Test Scenarios

### TRV-01: Reviews page loads with Reviews heading
**Given** a teacher is logged in and navigates to `/en/dashboard/reviews`
**When** the page finishes loading
**Then** the "Reviews" heading area is visible
**Selectors:**
- reviews heading: `text="Reviews"`

### TRV-02: Three summary metric cards are shown
**Given** the reviews page is loaded
**When** the user views the summary section
**Then** Average Rating, Total Reviews, and 5-Star Reviews cards are visible with values
**Selectors:**
- average rating: `h3:has-text("Average Rating")`
- total reviews: `h3:has-text("Total Reviews")`
- five star: `h3:has-text("5-Star Reviews")`

### TRV-03: Rating Distribution section is shown with 5 star rows
**Given** the reviews page is loaded
**When** the user views the rating distribution
**Then** rows for 5★, 4★, 3★, 2★, 1★ are shown each with a count
**Selectors:**
- distribution heading: `h3:has-text("Rating Distribution")`
- five star row: `text="5★"`
- one star row: `text="1★"`

### TRV-04: Search box filters reviews by keyword
**Given** the reviews page is loaded
**When** the user types text into the search box
**Then** only reviews matching the keyword are shown
**Selectors:**
- search input: `input[placeholder="Search reviews..."]`

### TRV-05: Star filter buttons narrow displayed reviews
**Given** the reviews page is loaded
**When** the user clicks "5★" filter button
**Then** only 5-star reviews are shown
**Selectors:**
- all filter: `button:has-text("All")`
- five star filter: `button:has-text("5★")`
- four star filter: `button:has-text("4★")`
- three star filter: `button:has-text("3★")`
- two star filter: `button:has-text("2★")`
- one star filter: `button:has-text("1★")`

### TRV-06: Empty state shown when no reviews match
**Given** the teacher has no reviews
**When** the teacher views the reviews page
**Then** "No reviews found" message is displayed
**Selectors:**
- empty state: `p:has-text("No reviews found")`

### TRV-07: Review items show reviewer name, rating stars, date, and comment
**Given** the teacher has at least one review
**When** the user views the reviews list
**Then** each review card shows reviewer name, star rating, date, and review text
**Selectors:**
- review card: `[class*="review-card"], [data-testid="review"]`

### TRV-08: Negative — Unauthenticated access redirects
**Given** a user is not logged in
**When** the user navigates to `/en/dashboard/reviews`
**Then** the user is redirected to the homepage or login
**Selectors:**
- redirect: `/en` url
