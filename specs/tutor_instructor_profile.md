# Page: Tutor Instructor Profile

**URL:** `https://dev.mehadedu.com/en/dashboard/instructor-profile`

**URL (dev):** `https://dev.mehadedu.com/en/dashboard/instructor-profile`
**URL (prod):** `https://mehadedu.com/en/dashboard/instructor-profile`

## Description
Tutor's public instructor profile management. Three sections: Personal Information, Certificates & Expertise, and Teaching Subjects. New teachers complete a 4-step APPLICATION wizard at `/en/tutor/profile` — after admin approval (2–3 business days), the same data is accessible and editable at this dashboard page. Updates to the dashboard profile also require admin review.

## Two-Phase New Teacher Setup

### Phase 1 — Application Wizard (`/en/tutor/profile`)
Accessed via `/en/become-tutor` → "Apply Now" → `/en/tutor-login` OTP login.

| Step | Page | Key Fields |
|------|------|-----------|
| 1 | Personal Information | First Name*, Last Name*, Email*, Bio* (500 chars), Languages*, Timezone (auto), Intro Video (optional) |
| 2 | Educational Certifications | Highest Degree*, University/Institution*, Graduation Year* (4 digits), Certificate* (PDF/JPG/PNG, max 10MB) |
| 3 | Subjects & Expertise | Subject Name* (dropdown), Hourly Rate* (SAR), About This Subject* (500 chars), Years of Experience* (1–10), Target Students* (Primary/Middle/High School/University), Additional Experience (optional) |
| 4 | Review | Read-only summary of all steps; "Submit Application" button |

**Post-submit state:** "Application Submitted — pending management review. 2–3 business days."

### Phase 2 — Post-Approval Dashboard (`/en/dashboard/instructor-profile`)
After admin approves, the tutor dashboard unlocks full menus. The instructor profile page shows three tabs with the submitted data (editable). The **Public Availability** toggle controls whether the profile is visible to students.

**Critical:** Even after approval, the tutor must still set availability at `/en/dashboard/availability` before students can see bookable slots.

## Public Profile
Once approved and visible: `https://mehadedu.com/en/tutor/{tutor_profile_id}`
Note: `tutor_profile_id` ≠ `userId`. The mapping is resolved via `GET /api/v1/public/tutors/{id}`.

## Dual-Role Accounts (Production)
The same phone number can hold both a student account and a tutor account. Student login uses the homepage modal; tutor login uses `/en/tutor-login`. Each role has a separate `userId` and `role` field in localStorage.

**Observed production accounts:**
| Phone | userId | Role | Notes |
|-------|--------|------|-------|
| +880 1316314566 | 514 | student | Created 2026-06-03 |
| +880 1316314566 | 615 | tutor | Created 2026-06-06; tutor profile ID 301 |

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Instructor Profile link | `a:has-text("Instructor Profile"), [data-testid="instructor-profile"]` | Required |
| Personal Info tab | `[role="tab"]:has-text("Personal Information"), button:has-text("Personal")` | Required |
| Certificates tab | `[role="tab"]:has-text("Certificates"), button:has-text("Certificate")` | Required |
| Teaching Subjects tab | `[role="tab"]:has-text("Teaching Subjects"), button:has-text("Subject")` | Required |
| Bio textarea | `textarea[name="bio"], textarea[placeholder*="bio"]` | Required |
| Add Certificate button | `button:has-text("Add Certificate")` | Optional |
| Degree input | `input[name="degree"], input[placeholder*="Degree"]` | Optional |
| University input | `input[name="university"]` | Optional |
| Graduation year input | `input[name="graduationYear"], input[placeholder*="Year"]` | Optional |
| Subject select | `select[name="subject"], [placeholder*="Subject"]` | Optional |
| Hourly rate input | `input[name="hourlyRate"], input[placeholder*="rate"]` | Optional |
| About subject textarea | `textarea[name="aboutSubject"]` | Optional |
| Experience select | `select[name="experience"]` | Optional |
| Teaching level select | `select[name="teachingLevel"]` | Optional |
| Save/Update button | `button:has-text("Save"), button:has-text("Update")` | Required |
| Pending status | `:has-text("Pending"), .pending-badge` | Conditional |

## User Flows

### Flow 1: Update Personal Information
1. Navigate to Instructor Profile
2. Click "Personal Information" tab
3. Update bio (max 500 chars)
4. Click Save
→ Expected: Saved, set to pending admin approval

### Flow 2: Add Certificate
1. Click "Certificates" tab
2. Click "Add Certificate"
3. Fill degree, university, graduation year
4. Upload certificate file (max 10MB)
5. Click Save
→ Expected: Certificate saved, pending review

### Flow 3: Update Teaching Subjects
1. Click "Teaching Subjects" tab
2. Select subject from dropdown
3. Set hourly rate (0-10000)
4. Fill about subject (max 500 chars)
5. Select experience (1-10 years)
6. Select teaching level
7. Click Save
→ Expected: Subject info saved, pending approval

## Requirements
- REQ-01: Instructor profile has Personal Info, Certificates, and Teaching Subjects sections
- REQ-02: Bio maximum 500 characters
- REQ-03: Experience field maximum 1000 characters
- REQ-04: About Subject maximum 500 characters
- REQ-05: Hourly rate between 0 and 10000
- REQ-06: Certificate upload maximum 10 MB
- REQ-07: Changes set to pending status until admin approves
- REQ-08: Graduation year must be 4-digit number

## Edge Cases
| EC-01 | Bio over 500 chars | Field truncated or validation error |
| EC-02 | Hourly rate over 10000 | Validation error shown |
| EC-03 | Certificate file over 10 MB | Upload rejected |
| EC-04 | Graduation year non-numeric | Validation error |
| EC-05 | Empty required subject fields | Validation error on save |

## Test Data
### Valid
| Field | Value |
|---|---|
| name | 98976564 |
| name | 123456 |
| name | Experienced math teacher with 3 years online |
| name | 50 |
| name | 2020 |

### Invalid
| Field | Value |
|---|---|
| name | 99999 |
| name | A (500+ chars) |
| name | abcd |
