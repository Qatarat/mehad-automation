# Page: Tutor Reviews

**URL:** `https://dev.mehadedu.com/en/dashboard/reviews`

## Description
Tutor's reviews and ratings overview. Shows overall average rating, total review count, star distribution, and individual student reviews. Filterable by student name and star rating.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Reviews heading | `h1:has-text("Reviews"), h2:has-text("Reviews")` | Required |
| Average rating display | `.average-rating, [data-testid="avg-rating"]` | Required |
| Total reviews count | `:has-text("Total Reviews"), .total-reviews` | Required |
| Five star count | `:has-text("5 star"), .five-star-count` | Optional |
| Student name filter | `input[placeholder*="student"], input[placeholder*="Search"]` | Optional |
| Star rating filter | `select[aria-label*="star"], [placeholder*="Star"]` | Optional |
| Review item | `.review-item, [data-testid="review"]` | Conditional |
| Reviewer name | `.reviewer-name` | Optional |
| Review text | `.review-text, .feedback` | Optional |
| Star display | `.star-rating, [aria-label*="stars"]` | Optional |

## User Flows

### Flow 1: View Reviews Overview
1. Log in as tutor
2. Navigate to Reviews in sidebar
3. Page shows average rating, total reviews, 5-star count
→ Expected: Review statistics displayed correctly

### Flow 2: Filter Reviews by Student Name
1. Navigate to Reviews page
2. Type student name in search/filter input
3. Reviews filtered to show only that student's reviews
→ Expected: Filtered results shown

### Flow 3: Filter Reviews by Star Rating
1. Navigate to Reviews
2. Select "5 stars" from rating dropdown
3. Only 5-star reviews shown
→ Expected: Rating-filtered results

## Requirements
- REQ-01: Reviews page shows overall average rating
- REQ-02: Total review count is accurate
- REQ-03: 5-star count and percentage displayed
- REQ-04: Filter by student name narrows results
- REQ-05: Star rating filter shows correct distribution
- REQ-06: Average rating calculated correctly from all reviews

## Edge Cases
| EC-01 | No reviews yet | Empty state or zero values shown |
| EC-02 | Filter with no matches | Empty state shown |
| EC-03 | Long student name in filter | Handles gracefully |
| EC-04 | XSS in filter input | Sanitized |

## Test Data
### Valid
| Field | Value |
|---|---|
| name | 98976564 |
| name | 123456 |
| name | Test Student |

### Invalid
| Field | Value |
|---|---|
| name | <script>alert(1)</script> |
