# Page: Testimonials Management — Super Admin

**URL:** `https://dev.mehadedu.com/en/super-admin-login`

## Description
Super Admin content management for testimonials displayed on the landing page. Testimonials have Active/Inactive status. Active testimonials appear on public landing page in testimonial section.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Content Management link | `a:has-text("Content Management"), [data-testid="content-nav"]` | Required |
| Testimonials option | `a:has-text("Testimonials"), [role="menuitem"]:has-text("Testimonials")` | Required |
| Testimonials heading | `h1:has-text("Testimonials"), h2:has-text("Testimonials")` | Required |
| Create Testimonial button | `button:has-text("Create Testimonial"), button[aria-label*="create"]` | Required |
| Search input | `input[placeholder*="Search"]` | Optional |
| Status filter | `select[aria-label*="Status"], [placeholder*="Active"]` | Optional |
| Testimonial list | `table, [data-testid="testimonials-list"]` | Required |
| Avatar upload | `input[type="file"]` | Optional |
| Name input | `input[name="name"], input[placeholder*="Name"]` | Required |
| Role input | `input[name="role"], input[placeholder*="Role"]` | Optional |
| Rating selector | `.star-rating, [aria-label*="rating"]` | Optional |
| Comment textarea | `textarea[name="comment"]` | Required |
| Status toggle | `[role="switch"]` | Required |
| Create button | `button:has-text("Create"), button[type="submit"]` | Required |
| Edit option | `[role="menuitem"]:has-text("Edit")` | Optional |
| Delete option | `[role="menuitem"]:has-text("Delete")` | Optional |

## User Flows

### Flow 1: Create Active Testimonial
1. Navigate to Content Management > Testimonials
2. Click "Create Testimonial"
3. Upload avatar (max 2 MB)
4. Fill Name (max 32 chars): Ahmed Student
5. Fill Role (max 32 chars): Student
6. Set Rating: 5 stars
7. Enter Comment: Great platform for learning
8. Toggle Status: Active
9. Click "Create"
10. Navigate to landing page
11. Verify testimonial appears in testimonial section

### Flow 2: Create Inactive Testimonial
1. Create testimonial with Status: Inactive
2. Navigate to landing page
3. Verify testimonial NOT visible

### Flow 3: Edit Testimonial
1. Find testimonial in list
2. Click action > Edit
3. Update comment
4. Save
5. Landing page reflects update

## Requirements
- REQ-01: Testimonials page accessible from Content Management menu
- REQ-02: Name field max 32 characters
- REQ-03: Role field max 32 characters
- REQ-04: Avatar max 2 MB
- REQ-05: Active testimonials visible on landing page
- REQ-06: Inactive testimonials hidden from public
- REQ-07: Delete removes testimonial permanently

## Edge Cases
| EC-01 | Name over 32 chars | Validation error |
| EC-02 | Avatar over 2 MB | Upload rejected |
| EC-03 | Create with Inactive status | Not shown on landing page |
| EC-04 | Delete active testimonial | Removed from landing page |

## Test Data
### Valid
| Field | Value |
|---|---|
| name | Test Student |
| name | Ahmed Learner |
| name | Sara Teacher |

### Invalid
| Field | Value |
|---|---|
| name | empty_name |
| name | name_over_thirtytwo_characters_long |
