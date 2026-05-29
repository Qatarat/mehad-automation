# Page: Student Favorite Teachers

**URL:** `https://dev.mehadedu.com/en/dashboard/favorites`

## Description
Student's saved favorite tutors list. Students add tutors via heart icon on tutor cards, view their favorites list, remove tutors, and quick-book from this page.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Favorite Teachers heading | `h1:has-text("Favorite Teachers"), h2:has-text("Favorites")` | Required |
| Tutor card | `.tutor-card, [data-testid="tutor-card"]` | Required |
| Tutor name | `.tutor-name, [data-testid="name"]` | Required |
| Heart/favorite icon | `button[aria-label*="favorite"], button[aria-label*="bookmark"]` | Required |
| Book Lesson button | `button:has-text("Book Lesson")` | Required |
| Browse more tutors | `button:has-text("Browse"), a:has-text("Browse more")` | Optional |
| Empty state | `:has-text("No favorites"), :has-text("no favorite")` | Conditional |
| Rating display | `.rating, [aria-label*="rating"]` | Optional |
| Hourly rate | `.price, :has-text("per hour")` | Optional |

## User Flows

### Flow 1: View Favorite Tutors
1. Navigate to https://dev.mehadedu.com/en/dashboard/favorites
2. Page shows list of saved tutors
3. Each card shows profile, name, badge, rating, language, rate
→ Expected: Favorites list displayed correctly

### Flow 2: Remove Tutor from Favorites
1. Navigate to favorites page
2. Click heart/bookmark icon on tutor card (filled = active)
3. Confirmation or immediate removal
→ Expected: Tutor removed, heart icon toggles to empty

### Flow 3: Book Lesson from Favorites
1. Navigate to favorites
2. Click "Book Lesson" on tutor card
3. Redirects to tutor profile/booking flow
→ Expected: Booking flow starts for that tutor

### Flow 4: Toggle Favorite State
1. Click heart to add tutor
2. Heart becomes filled
3. Click again to remove
4. Heart becomes empty
→ Expected: State toggles correctly, no duplicates

## Requirements
- REQ-01: Favorites page accessible to authenticated students at /dashboard/favorites
- REQ-02: Saved tutors listed with name, rating, rate, languages
- REQ-03: Heart icon toggles favorite state
- REQ-04: Removed tutor disappears from list
- REQ-05: Favorite state persists after page refresh
- REQ-06: Book Lesson initiates booking flow
- REQ-07: Empty state shows when no tutors saved
- REQ-08: Browse more tutors links to find-tutors page

## Edge Cases
| EC-01 | No favorites saved | Empty state message shown |
| EC-02 | Toggle heart rapidly | No duplicate entries, state correct |
| EC-03 | Remove last favorite | Empty state shown |
| EC-04 | Unauthenticated access | Redirects to login |
| EC-05 | Tutor becomes inactive | Card shows appropriate state |

## Test Data
### Valid
| Field | Value |
|---|---|
| name | 98976564 |
| name | 123456 |

### Invalid
| Field | Value |
|---|---|
| name | 000000 |
