# Spec: Student — Reviews & Ratings

**URL:** `/en/dashboard/reviews`
**Role:** Student
**Last verified:** 2026-06-02

---

## Overview

The Reviews & Ratings page in the student dashboard shows reviews the student has submitted for tutors. Reviews can only be left after a completed session. No review form is available if no sessions have been completed.

---

## Page Structure

### Sidebar
- Standard student sidebar: My Bookings, Messages, Favorite Teachers, Payment & Wallet, Reviews & Ratings, Settings, Help Center

### Main Content
- `heading[level=1]` "Reviews & Ratings"
- Filter controls row:
  - `combobox` "All ratings" — filters by star rating (All, 5 stars, 4 stars, etc.)
  - `combobox` "Newest" — sorts by date (Newest, Oldest)
  - `combobox` "10" — items per page (10, 25, 50)
- Review list area:
  - When no reviews: shows text "No reviews found."
  - When reviews exist: each row shows tutor info, star rating, review text, date

---

## BDD Scenarios

#### Scenario 1: Student with no completed sessions sees empty state
```
Given the student has no completed sessions
When the student navigates to /en/dashboard/reviews
Then the heading "Reviews & Ratings" is displayed
And three filter comboboxes are shown: "All ratings", "Newest", "10"
And the main content area shows "No reviews found."
And there is no "Write a Review" button or form visible
```

#### Scenario 2: Filter controls are present even with no reviews
```
Given the student is on /en/dashboard/reviews with no reviews
Then the combobox "All ratings" is visible and selectable
And the combobox "Newest" is visible and selectable
And the combobox "10" is visible and selectable
```

#### Scenario 3: Student reviews appear after completed session (expected behavior)
```
Given the student has completed a 1-on-1 session with a tutor
When the student navigates to /en/dashboard/reviews
Then a review form or trigger is available for that session
When the student selects 5 stars and enters review text
And clicks submit
Then the review appears in the list with:
  - Tutor name and avatar
  - 5 filled star icons
  - Review text
  - Session date
```

**Note:** Review submission form was not reachable in live testing as payment was not completed (dev PayTabs sandbox). The page only shows "No reviews found." when no sessions are completed.

---

## Tutor Profile — Public Reviews Section

**URL:** `/en/tutor/{id}`

The tutor profile shows received reviews under an "About me" section. When no reviews exist:
- Star rating shows "0.0"
- Review count shows "(0 reviews)"
- Text: "No reviews yet."

When reviews exist (observed on platform homepage from other tutors):
- Star icons rendered as `img` elements (filled/empty)
- Review text as `paragraph`
- Reviewer name and role/institution label

---

## Real Selectors Observed

| Element | Selector |
|---|---|
| Reviews page heading | `h1:has-text("Reviews & Ratings")` |
| All ratings filter | `combobox` (first, showing "All ratings") |
| Newest filter | `combobox` (second, showing "Newest") |
| Per-page filter | `combobox` (third, showing "10") |
| Empty state text | `generic:has-text("No reviews found.")` |
| Tutor profile rating | `generic:has-text("0.0")` + `generic:has-text("(0 reviews)")` |

---

## Empty / Error States

- "No reviews found." when student has no completed sessions or has not yet submitted any reviews
- Review form/button not visible without completed sessions
- Tutor public profile shows "No reviews yet." when tutor has received no ratings
