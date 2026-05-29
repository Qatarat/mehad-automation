# Page: Student Find Group Course and Enroll

**URL:** `https://dev.mehadedu.com/en/find-tutors?session=group`

## Description
Group course search and enrollment workflow. Students find group sessions via Find Tutors > Group Session dropdown, filter by subject/price/time, and enroll with payment.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Find Tutors button | `button:has-text("Find Tutors")` | Required |
| Group Session menu item | `[role="menuitem"]:has-text("Group Session")` | Required |
| Group session heading | `h1:has-text("Find your perfect tutor"), h1:has-text("group")` | Required |
| Subject filter | `select, [placeholder*="All Subjects"], [aria-label*="Subject"]` | Optional |
| Price filter | `[placeholder*="Any price"], [aria-label*="price"]` | Optional |
| Time filter | `[placeholder*="Any time"], [aria-label*="time"]` | Optional |
| Tutor name search | `input[placeholder*="Search"]` | Optional |
| Course card | `.course-card, [data-testid="course-card"]` | Required |
| Enroll Now button | `button:has-text("Enroll Now")` | Required |
| Course name | `.course-name, h3:has-text("course")` | Required |
| Course price | `.price, [data-testid="price"]` | Required |
| Booking modal | `[role="dialog"]:has-text("Book Group Session")` | Conditional |
| Continue button | `[role="dialog"] button:has-text("Continue")` | Required |
| Confirm and Pay button | `button:has-text("Confirm & Pay")` | Required |

## User Flows

### Flow 1: Enroll in Group Session
1. Navigate to https://dev.mehadedu.com/en
2. Login as student (phone 98976564, OTP 123456)
3. Click "Find Tutors" in header
4. Click "Group Session" from dropdown
5. Filter by subject (e.g., Math)
6. Browse group session cards
7. Click "Enroll Now" on desired session
8. "Book Group Session" modal opens
9. Click "Continue"
10. Click "Confirm & Pay"
11. Fill payment: 4111 1111 1111 1111, 05/28, CVV 100
12. Click "Pay Now"
13. Click "Submit" in confirmation modal
→ Expected: Enrolled, redirect to My Bookings

### Flow 2: Filter Group Sessions
1. Navigate to group sessions page
2. Select subject: Math
3. Select price range
4. Sessions filtered accordingly
→ Expected: Only matching sessions shown

### Flow 3: Prevent Duplicate Enrollment
1. Enroll in a group session
2. Navigate back to group sessions
3. Find the same session
4. Try to enroll again
→ Expected: System prevents duplicate enrollment

## Requirements
- REQ-01: Group Session accessible from Find Tutors dropdown
- REQ-02: Group sessions page shows available courses
- REQ-03: Subject, price, and time filters work correctly
- REQ-04: Each course card shows tutor details and session info
- REQ-05: Enroll Now opens booking modal
- REQ-06: Booking modal has Continue and Confirm & Pay steps
- REQ-07: Payment completes enrollment
- REQ-08: Enrolled course appears in My Bookings
- REQ-09: Duplicate enrollment is prevented
- REQ-10: Fully booked sessions show enrollment disabled

## Edge Cases
| EC-01 | Duplicate enrollment attempt | Error: already enrolled |
| EC-02 | Session fully booked | Enroll Now disabled |
| EC-03 | No sessions match filters | Empty state shown |
| EC-04 | Payment fails | Enrollment not confirmed |
| EC-05 | Close booking modal before payment | Enrollment not created |

## Test Data
### Valid
| Field | Value |
|---|---|
| name | 98976564 |
| name | 123456 |
| name | 4111 1111 1111 1111 |
| name | 05/28 |
| name | 100 |

### Invalid
| Field | Value |
|---|---|
| name | 0000 0000 0000 0000 |
| name | 000000 |
