# Page: Student Hero Section — Homepage Search

**URL:** `https://dev.mehadedu.com/en`

## Description
The homepage hero section provides quick tutor search filters. Students select subject, level, available time, and price range, then click "Find a Teacher" to navigate to filtered tutor listing.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Hero heading | `h1:has-text("Learn with the Best")` | Required |
| Subject dropdown | `select[aria-label*="subject"], [placeholder="Select subject"]` | Optional |
| Level dropdown | `select[aria-label*="level"], [placeholder="Select Level"]` | Optional |
| Availability dropdown | `select[aria-label*="availability"], [placeholder="Select availability"]` | Optional |
| Price range dropdown | `select[aria-label*="price"], [placeholder="Select Price Range"]` | Optional |
| Find a Teacher button | `button:has-text("Find a Teacher")` | Required |
| Stats badge | `:has-text("1,200 Certified Teachers")` | Optional |
| Top tutors section | `:has-text("Our Top Teachers")` | Optional |
| Subject badge | `.subject-badge, :has-text("Most Requested Subjects")` | Optional |

## User Flows

### Flow 1: Find Tutor via Hero Search
1. Navigate to https://dev.mehadedu.com/en
2. Select subject: Math
3. Select level: High School
4. Select available time
5. Select price range
6. Click "Find a Teacher"
→ Expected: Navigates to /en/find-tutors with applied filters

### Flow 2: Search Without Filters
1. Navigate to homepage
2. Click "Find a Teacher" without selecting any filter
→ Expected: Navigates to /en/find-tutors showing all tutors

### Flow 3: Click Subject Badge
1. Navigate to homepage
2. Scroll to "Most Requested Subjects"
3. Click "Math" subject badge
→ Expected: Navigates to /en/find-tutors?subjectId=X

## Requirements
- REQ-01: Hero section is visible on homepage
- REQ-02: Subject, Level, Availability, Price Range dropdowns are present
- REQ-03: Find a Teacher button navigates to /en/find-tutors
- REQ-04: Applied filters pass as query parameters to find-tutors
- REQ-05: No login required to use hero search
- REQ-06: Subject badges in STUDY SUBJECTS section link to filtered results

## Edge Cases
| EC-01 | Click Find a Teacher with no filters | All tutors shown |
| EC-02 | Select conflicting filters | Results shown or empty state |
| EC-03 | Page loads without JavaScript | Graceful degradation |
| EC-04 | Direct navigation to /en | Hero section visible |

## Test Data
### Valid
| Field | Value |
|---|---|
| name | Math |
| name | Physics |
| name | Algebra |

### Invalid
| Field | Value |
|---|---|
| name | empty_filter |
