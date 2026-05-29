# Page: Student Find Tutor Workflow

**URL:** `https://dev.mehadedu.com/en/find-tutors`

## Description
Student workflow for finding and booking tutors. Includes both 1-to-1 and group session discovery. Students use the "Find Tutors" header dropdown, apply filters, view tutor profiles, and proceed to booking.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Find Tutors button | `button:has-text("Find Tutors"), nav button:has-text("Find Tutors")` | Required |
| One-to-one option | `[role="menuitem"]:has-text("1-to-1"), a:has-text("1 to 1")` | Required |
| Group Session option | `[role="menuitem"]:has-text("Group Session"), a:has-text("Group Session")` | Required |
| Find tutors heading | `h1:has-text("Find your perfect tutor")` | Required |
| Subject filter | `select[aria-label*="Subject"], [placeholder*="All Subjects"]` | Optional |
| Level filter | `select[aria-label*="Level"], [placeholder*="All Levels"]` | Optional |
| Price filter | `select[aria-label*="price"], [placeholder*="Any price"]` | Optional |
| Time filter | `select[aria-label*="time"], [placeholder*="Any time"]` | Optional |
| Search input | `input[placeholder*="Search tutors"]` | Optional |
| Tutor card | `.tutor-card, [data-testid="tutor-card"]` | Required |
| Book Trial Lesson | `button:has-text("Book Trial Lesson")` | Required |
| Enroll Now button | `button:has-text("Enroll Now")` | Required — group sessions |
| Tutor count | `:has-text("tutors available")` | Required |
| Load more button | `button:has-text("Load more")` | Optional |

## User Flows

### Flow 1: Find and Book 1-to-1 Session
1. Navigate to https://dev.mehadedu.com/en
2. Authenticate as student (phone 98976564, OTP 123456)
3. Click "Find Tutors" in header
4. Click "1 to 1 session" from dropdown
5. Page navigates to /en/find-tutors
6. Select subject from filter dropdown
7. View tutor cards with ratings and prices
8. Click "Book Trial Lesson" on a tutor card
9. Tutor profile opens with slot calendar
10. Click available time slot
11. Click "Continue"
12. Click "Confirm & Pay"
→ Expected: Payment form opens

### Flow 2: Find and Enroll in Group Session
1. Navigate to homepage
2. Click "Find Tutors" in header
3. Click "Group Session" from dropdown
4. Group session listing page opens
5. Select subject from "I want to learn" dropdown
6. Browse filtered results
7. Click "Enroll Now" on a session
8. Group booking modal opens
9. Click "Continue"
10. Click "Confirm & Pay"
→ Expected: Payment form opens

### Flow 3: Filter Tutors
1. Navigate to /en/find-tutors
2. Select subject: Math
3. Select level: High School
4. Select price range
5. Click "Find a Teacher" or filter auto-applies
→ Expected: Tutor list filtered by criteria

## Requirements
- REQ-01: Find Tutors button in header shows dropdown with 1-to-1 and Group Session options
- REQ-02: /en/find-tutors shows heading "Find your perfect tutor"
- REQ-03: Subject, level, price, time filters are present and functional
- REQ-04: Tutor count is displayed (e.g., "64 tutors available")
- REQ-05: Each tutor card shows name, rating, subjects, price
- REQ-06: Book Trial Lesson leads to tutor profile with slot calendar
- REQ-07: Enroll Now on group session opens booking modal
- REQ-08: Group session filter includes "I want to learn" subject dropdown
- REQ-09: Load more button loads additional tutors
- REQ-10: Search input filters tutors by name

## Edge Cases
| EC-01 | No tutors match filters | Empty state message shown |
| EC-02 | All filters applied at once | Results updated correctly |
| EC-03 | Student tries to enroll same group session twice | System prevents duplicate |
| EC-04 | Tutor has no available slots | Booking button disabled or unavailable |
| EC-05 | Group session fully booked | Enroll button disabled |
| EC-06 | Search with special characters | No crash, empty or relevant results |
| EC-07 | Load more at end of list | No more results message or no button |

## Test Data
### Valid
| Field | Value |
|---|---|
| name | 98976564 |
| name | 123456 |
| name | Math |
| name | Saymon |

### Invalid
| Field | Value |
|---|---|
| name | <script>alert(1)</script> |
| name | abc |
