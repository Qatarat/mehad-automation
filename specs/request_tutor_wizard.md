# Page: Request-a-Tutor Wizard (11-Step Onboarding Funnel)

**URL:** `https://dev.mehadedu.com/en`

## Description
The "Book Your Spot Now" / "Find Tutors" CTA on the homepage starts a multi-step tutor-request wizard used by Parents/Students to describe what tutoring they need: account type, curriculum, subject, schedule, and a final review step that issues a request ID (REQ-ID) for Admin to assign a tutor against. This is **distinct from `become_tutor.md`**, which is the tutor-side application funnel — this spec covers the customer-side request funnel, previously undocumented despite being the platform's primary conversion flow (dashboard.html QA matrix lists it as "11-Step Tutor Request Wizard" with 45+ related test cases). Exact step order/copy must be confirmed against the live wizard on first run and this spec updated with the true step sequence if it differs.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Entry CTA (homepage) | `button:has-text("Book Your Spot Now"), button:has-text("Find Tutors")` | Required |
| Wizard container | `[role="dialog"], main:has-text("Step")` | Required |
| Step progress indicator | `:text("Step"), [role="progressbar"]` | Required |
| Account type selector (Parent/Student/Myself) | `button:has-text("Parent"), button:has-text("Student")` | Required — step 1 |
| Curriculum selector (MoE / British IGCSE / American SAT-AP / IB / IELTS / Coding) | `select[name*="curriculum" i], button:has-text("IGCSE")` | Required |
| Subject selector | `select[name*="subject" i], input[placeholder*="Subject" i]` | Required |
| Grade/level selector | `select[name*="grade" i]` | Required |
| Schedule/availability picker | `input[type="date"], [data-testid="schedule-picker"]` | Required |
| Session type (1-on-1 / Group / Online / In-person) | `button:has-text("1-on-1"), button:has-text("Online")` | Required |
| Contact details step (name/phone) | `input[type="tel"], input[name*="name" i]` | Required |
| Back button | `button:has-text("Back")` | Required on steps 2-11 |
| Next/Continue button | `button:has-text("Next"), button:has-text("Continue")` | Required |
| Review/Summary step | `:text("Review"), :text("Summary")` | Required — final step before submit |
| Submit request button | `button:has-text("Submit"), button:has-text("Request Tutor")` | Required |
| REQ-ID confirmation | `:text("REQ-"), :text("Request ID")` | Required — shown on success |

## User Flows

### Flow 1: Complete the Wizard End-to-End (Happy Path)
1. Navigate to homepage
2. Click "Book Your Spot Now" (or "Find Tutors")
3. Step 1: Select account type "Parent"
4. Step 2: Select curriculum "American SAT/AP"
5. Step 3: Select subject "Math"
6. Step 4: Select grade/level
7. Step 5: Select session type "Online" and "1-on-1"
8. Step 6: Pick preferred schedule/availability
9. Step 7-10: Fill any remaining contact/preference steps, using "Next" to advance
10. Step 11: Review summary screen
11. Click "Submit"
→ Expected: Confirmation screen shows a REQ-ID (e.g. `REQ-XXXXX`), request appears later in Admin's lead queue

### Flow 2: Navigate Back and Forth Without Losing Data
1. Start the wizard, complete steps 1-3
2. Click "Back" twice
3. Click "Next" twice again
→ Expected: Previously entered selections (curriculum, subject) persist — not reset

### Flow 3: Abandon Mid-Wizard and Resume
1. Start the wizard, complete steps 1-4
2. Close the wizard / navigate away
3. Reopen the wizard from the homepage CTA
→ Expected: Either resumes from a saved draft state, or cleanly restarts at step 1 — must not throw an error or show a corrupted partial state

### Flow 4: Submit With All 6 Curricula (Data Coverage)
1. Run the full wizard once per curriculum: MoE, British IGCSE, American SAT/AP, IB, IELTS, Coding
→ Expected: Each curriculum's subject list is relevant to that curriculum (e.g. Coding curriculum should not show "IELTS Speaking" as a subject) and each run produces a unique REQ-ID

## Requirements
- REQ-01: Wizard is reachable from the homepage without requiring login for the first N steps (public funnel), and only requires auth/contact info at or before the final submit step
- REQ-02: Step progress indicator accurately reflects current step out of total steps
- REQ-03: "Back" never loses previously entered data for the step being returned to
- REQ-04: "Next"/"Continue" is disabled until the current step's required field(s) are filled
- REQ-05: Final Review step shows every selection made in prior steps (curriculum, subject, schedule, session type, contact) for user confirmation before submit
- REQ-06: Successful submission returns a unique, non-guessable REQ-ID
- REQ-07: The subject list offered must be filtered/relevant to the previously selected curriculum
- REQ-08: Submitting the wizard while a required field is missing must not be possible via direct API call either (server-side validation, not just client-side)
- REQ-09: Wizard must be fully usable in both English (LTR) and Arabic (RTL) layouts
- REQ-10: Page must not show 500/404 at any step, including directly reloading mid-wizard

## Edge Cases
| EC-01 | Click Submit without completing any step | Blocked — Next/Submit stays disabled or shows validation |
| EC-02 | Reload the browser mid-wizard (e.g. at step 5) | Wizard either restores state or restarts cleanly, no crash |
| EC-03 | Rapidly double-click Submit on the review step | Only one request/REQ-ID is created, not duplicates |
| EC-04 | Enter contact phone with letters ("abc12345") | Rejected, numeric-only enforced |
| EC-05 | Enter contact phone with SQL injection payload (`' OR 1=1--`) | Rejected as invalid phone format, no 500, no injection |
| EC-06 | Select a curriculum, then a subject, then go Back and change curriculum | Previously selected subject is cleared or re-validated against the new curriculum, not silently kept invalid |
| EC-07 | Choose a schedule date in the past | Rejected with validation error |
| EC-08 | Choose a schedule date with an impossible value (`32/13/2099`) | Rejected with validation error |
| EC-09 | Leave the wizard open/idle for an extended period, then submit | Either session/draft still valid, or a clear "session expired, please restart" message — no silent failure |
| EC-10 | Submit the same request twice in two tabs concurrently | Both either succeed with distinct REQ-IDs or the second is clearly flagged as a duplicate — no silent data corruption |
| EC-11 | XSS payload in any free-text contact/notes field (`<img src=x onerror=alert(1)>`) | Rendered as literal text everywhere it later appears (Admin lead queue, confirmation email/SMS), no script execution |
| EC-12 | Switch language to Arabic mid-wizard | Layout flips to RTL correctly, no untranslated English strings mixed into Arabic UI, no step data lost |

## Test Data
### Valid
| Field | Value |
|---|---|
| name | Math |
| name | Physics |
| name | English |
| name | Arabic |
| name | Coding |
| name | 501234567 |
| name | 966501234567 |

### Invalid
| Field | Value |
|---|---|
| name | abc12345 |
| name | ' OR 1=1-- |
| name | <img src=x onerror=alert(1)> |
| name | 32/13/2099 |
| name | 00/00/0000 |
