# Page: Tutor Signup — Tutor Application Form

**URL (dev):** `https://dev.mehadedu.com/en/tutor-login`
**URL (prod):** `https://mehadedu.com/en/tutor-login`

## Description
Tutor registration flow. Starts at `/en/become-tutor`, clicks "Apply Now", authenticates via OTP on `/en/tutor-login`, then completes a 4-step profile wizard at `/en/tutor/profile` covering personal info, certifications, subjects and expertise. After submission the application enters pending admin review (2–3 business days).

**Production note:** The same phone number may hold both a student and a tutor account — they are separate `userId` records with different `role` values (`student` vs `tutor`). Student login uses the homepage modal; tutor login uses `/en/tutor-login`.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Become a Tutor link | `a[href="/en/become-tutor"]` | Required |
| Apply Now button | `a:has-text("Apply Now"), button:has-text("Apply Now")` | Required |
| Tutor login heading | `h1:has-text("Teacher Login"), h2:has-text("Teacher Login")` | Required |
| Country code button | `button:has-text("+966"), [aria-label="Country code"]` | Required |
| Phone input | `input[type="tel"]` | Required |
| Send Code button | `button:has-text("Send Code")` | Required |
| OTP input | `input[autocomplete="one-time-code"], input[placeholder="000000"]` | Required |
| Continue button | `button:has-text("Continue")` | Required |
| First name input | `input[name="firstName"], input[placeholder*="First"]` | Required |
| Last name input | `input[name="lastName"], input[placeholder*="Last"]` | Required |
| Email input | `input[type="email"]` | Required |
| Bio textarea | `textarea[name="bio"], textarea[placeholder*="bio"]` | Required |
| Language selector | `[data-slot="select-trigger"]:has-text("Language"), button:has-text("Language")` | Required |
| Next button | `button:has-text("Next")` | Required |
| Submit Application button | `button:has-text("Submit Application")` | Required |

## User Flows

### Flow 1: Tutor Login from Become-a-Tutor Page
1. Navigate to https://dev.mehadedu.com/en/become-tutor
2. Click "Apply Now" button
3. Redirects to /en/tutor-login
4. Click country code button "+966"
5. Search for "Bangladesh" and select "+880"
6. Enter phone: 98976564
7. Click "Send Code"
8. Enter OTP: 123456
9. Click "Continue"
→ Expected: Tutor dashboard or signup form opens

### Flow 2: Complete Tutor Registration Form
1. After OTP login, signup form appears
2. Fill First Name (max 30 chars): TestTutor
3. Fill Last Name (max 30 chars): QA
4. Fill Email: testtutor@mehadedu.com
5. Fill Bio (max 500 chars): Experienced math teacher
6. Select Language: English
7. Click "Next" to proceed to education step
8. Fill Highest Degree: B.Sc.
9. Fill University: Test University
10. Fill Graduation Year: 2020
11. Upload Certificate
12. Click "Next" to subject step
13. Select Subject: Math
14. Set Hourly Rate: 50
15. Fill Subject Description
16. Select Experience: 3 years
17. Select Teaching Level: High School
18. Click "Next" to review
19. Click "Submit Application"
→ Expected: Application submitted successfully

### Flow 3: Direct Tutor Login Page
1. Navigate to https://dev.mehadedu.com/en/tutor-login
2. Page shows heading "Teacher Login"
3. Follow OTP login steps
→ Expected: Tutor authenticated

## Requirements
- REQ-01: Become a Tutor link must be visible in homepage header
- REQ-02: Apply Now navigates to /en/tutor-login
- REQ-03: Tutor login page shows heading "Teacher Login"
- REQ-04: OTP flow identical to student login
- REQ-05: First name maximum 30 characters
- REQ-06: Last name maximum 30 characters
- REQ-07: Email must be unique and valid format (max 254 chars)
- REQ-08: Bio maximum 500 characters
- REQ-09: Introduction video maximum 100 MB
- REQ-10: Certificate upload maximum 10 MB (image or PDF)
- REQ-11: Hourly rate between 0 and 10000
- REQ-12: Experience between 1 and 10 years
- REQ-13: All steps validated before proceeding to next

## Edge Cases
| EC-01 | First name over 30 characters | Field rejects or truncates input |
| EC-02 | Duplicate email address | Error: email already in use |
| EC-03 | Invalid email format | Validation error shown |
| EC-04 | Bio over 500 characters | Field rejects or truncates |
| EC-05 | Hourly rate over 10000 | Validation error shown |
| EC-06 | Video file over 100 MB | Upload rejected with error |
| EC-07 | Certificate over 10 MB | Upload rejected with error |
| EC-08 | Empty required fields on Next | Validation errors shown |
| EC-09 | Graduation year not 4 digits | Validation error shown |
| EC-10 | Submit with incomplete form | System prevents submission |

## Test Data
### Valid
| Field | Value |
|---|---|
| name | 98976564 |
| name | 123456 |
| name | TestTutor QA |
| name | testtutor@mehadedu.com |
| name | Experienced math teacher with 3 years of online teaching |

### Invalid
| Field | Value |
|---|---|
| name | abc |
| name | notanemail |
| name | AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA (over 30 chars) |
