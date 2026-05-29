# Page: Student Reviews and Ratings

**URL:** `https://dev.mehadedu.com/en/dashboard/reviews`

## Description
Student review and rating system. After completing a session, students can rate their tutor and leave feedback. Review is triggered from My Bookings > Complete Session, or directly from the Reviews page.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Reviews heading | `h1:has-text("Review"), h2:has-text("Reviews and Ratings")` | Required |
| Completed sessions list | `.completed-sessions, [data-testid="completed-list"]` | Required |
| Rate tutor prompt | `[role="dialog"]:has-text("Rate"), .review-modal` | Conditional |
| Star rating | `[aria-label*="star"], .star-rating button` | Conditional |
| Review text area | `textarea[placeholder*="feedback"], textarea[placeholder*="review"]` | Conditional |
| Submit review button | `button:has-text("Submit"), button:has-text("Submit Review")` | Conditional |
| Tutor name in review | `.tutor-name, [data-testid="tutor-name"]` | Required |
| Review date | `time, .review-date` | Optional |
| Rating display | `.rating-value, [aria-label*="rating"]` | Optional |

## User Flows

### Flow 1: Submit Review After Session
1. Navigate to My Bookings
2. Find completed session
3. Click "Complete Session"
4. Review prompt/modal appears
5. Select star rating (1-5)
6. Write feedback text
7. Click "Submit Review"
→ Expected: Review saved, appears on Reviews page

### Flow 2: View Reviews Page
1. Navigate to https://dev.mehadedu.com/en/dashboard/reviews
2. Page shows all submitted reviews with tutor name, date, rating
→ Expected: Review history visible

## Requirements
- REQ-01: Reviews page shows all submitted tutor reviews
- REQ-02: Review submission requires star rating
- REQ-03: Written feedback is optional
- REQ-04: Review is linked to specific tutor and session
- REQ-05: Only completed sessions can be reviewed
- REQ-06: Review appears on tutor profile after submission
- REQ-07: Cannot review the same session twice

## Edge Cases
| EC-01 | Review without star rating | Submit blocked |
| EC-02 | Review same session twice | System prevents duplicate |
| EC-03 | Review incomplete session | Not available |
| EC-04 | Very long review text | Character limit applied |
| EC-05 | Review with XSS in text | Input sanitized |

## Test Data
### Valid
| Field | Value |
|---|---|
| name | 98976564 |
| name | 123456 |
| name | 5 |
| name | Great tutor! |

### Invalid
| Field | Value |
|---|---|
| name | (empty) |
| name | <script>alert(1)</script> |
