# Page: Request-a-Tutor Wizard (8-Step Parent Funnel)

**URL:** `https://dev.mehadedu.com/en/dashboard/create-request`

## Description
CORRECTED 2026-09-17 after live verification (logged in as Parent, dev.mehadedu.com) — the previous version of this spec assumed an "11-Step" wizard per dashboard.html's QA matrix. The real, live wizard is **8 steps**, reached via the Parent dashboard's "Request a Tutor" button (top-right of `/en/dashboard/my-requests`), not a homepage CTA — it requires an authenticated Parent session with at least one child added first (`parent_dashboard.md`), and is not a public/unauthenticated funnel as previously assumed. This is **distinct from `become_tutor.md`**, which is the tutor-side application funnel.

**CRITICAL BUG FOUND (P0, live-verified, reproducible):** Step 3 ("Which subjects do you need?") renders **completely empty** — no subject cards, "Next" stays permanently disabled — for every curriculum tested (reproduced on both "Saudi National Curriculum" and "International Curricula"). No JS console error was thrown; the page does not visibly attempt a failing network call either, suggesting the subjects list for these curricula may simply be empty/unconfigured server-side rather than a frontend crash. **As currently observed, no parent can complete a tutor request on the dev environment at all** — this blocks the platform's entire core conversion funnel. This needs developer investigation (check subject-to-curriculum mapping data) rather than a QA-side fix. Steps 4-8 below are documented from the wizard's step-progress labels only (visible in the top-right corner as each step's title, e.g. "Curriculum", "Subjects") since they could not be reached without a subject selection — **re-verify steps 4-8 once the Step 3 bug is fixed.**

Also found live: the curriculum list (Step 2) includes at least two entries that look like leftover test/seed data mixed into production: a "Science" card with description **"Here is just for testing"**, and a "Test Curiculam" card (sic, misspelled) with description **"This is just for test purpose"**. These should be removed or hidden from the live curriculum list; regression-guard test cases below assert they eventually disappear.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Entry CTA (Parent dashboard) | `a:has-text("Request a Tutor"), button:has-text("Request a Tutor")` | Required — top-right of My Requests page |
| Step progress bar | `text=/Step \\d of 8/` | Required |
| Step 1 heading | `h1:has-text("Who is the lesson for?"), h2:has-text("Who is the lesson for?")` | Required |
| Learner selection card | `:text("AutoKid")` (or any provisioned child's name) | Required — clicking selects that child |
| Empty-state (no children) | `text="No learners are available on this parent account."` | Required when Manage Child has zero children |
| Step 2 heading | `h1:has-text("Which curriculum are you studying?")` | Required |
| Curriculum card | `:text("Saudi National Curriculum"), :text("International Curricula"), :text("Qiyas Tests"), :text("English Foundation & Development"), :text("University Level"), :text("Additional Languages"), :text("Arts & Extra Skills")` | Required |
| Stale test-data curriculum cards (bug regression guard) | `:text("Here is just for testing"), :text("This is just for test purpose")` | Should NOT exist once BUG fixed |
| Step 3 heading | `h1:has-text("Which subjects do you need?")` | Required |
| Subject card (currently never renders — bug) | `[data-testid="subject-card"]` | **Currently always empty — see bug above** |
| Back button | `button:has-text("Back")` | Required on steps 2-8 |
| Next button | `button:has-text("Next")` | Required; disabled until the current step's selection is made |

## User Flows

### Flow 1: Complete the Wizard End-to-End (currently blocked — see bug)
1. Log in as Parent, add a child via Manage Child if none exists
2. From `/en/dashboard/my-requests`, click "Request a Tutor"
3. Step 1 "Who is the lesson for?": select the child learner card, click Next
4. Step 2 "Which curriculum are you studying?": select a curriculum (e.g. "Saudi National Curriculum"), click Next
5. Step 3 "Which subjects do you need?": select a subject, click Next
→ **Currently blocked here**: no subjects render, Next stays disabled, flow cannot proceed. Expected once fixed: at least one subject card appears and is selectable, advancing to Step 4.
6. Steps 4-8 (grade/level, schedule, session mode, contact/review, submit — exact labels TBD, re-derive once Step 3 is fixed)
→ Expected end state: confirmation screen shows a REQ-ID (e.g. `REQ-1660`, format confirmed real via Admin's Teaching Requests list), request appears in Admin's Teaching Requests queue with status "Under Review" or "Waiting for Customer Decision"

### Flow 2: Learner Selection Blocks Progress When No Children Exist
1. Log in as a Parent account with zero children added
2. Click "Request a Tutor"
→ Expected: Step 1 shows "No learners are available on this parent account." and a hint to select a learner; Next stays disabled — confirmed live, works correctly

### Flow 3: Navigate Back and Forth Without Losing Data
1. Start the wizard, select a learner and a curriculum (steps 1-2)
2. Click "Back" once
3. Click "Next" again
→ Expected: Previously selected curriculum stays selected (checkmark badge persists) — confirmed live, works correctly for steps 1-2

### Flow 4: Regression Guard — Stale Test Curricula Should Not Appear
1. Log in as Parent, reach Step 2 of the wizard
2. Inspect every curriculum card's title and description text
→ Expected (once fixed): no card reads "Here is just for testing" or "This is just for test purpose" / "Test Curiculam"

## Requirements
- REQ-01: Wizard requires an authenticated Parent session and at least one added child — it is NOT a public/unauthenticated homepage funnel
- REQ-02: Step progress indicator ("Step N of 8") accurately reflects current step
- REQ-03: "Back" never loses previously entered data for the step being returned to (confirmed working for steps 1-2)
- REQ-04: "Next" is disabled until the current step's required selection is made
- REQ-05 (BLOCKED — see bug): Step 3 must render at least one subject option for every curriculum offered in Step 2; a curriculum with zero mapped subjects should not be selectable in Step 2 at all, or Step 3 should show a clear "no subjects available, contact support" state instead of a silent empty screen
- REQ-06: Successful submission returns a unique, non-guessable REQ-ID matching the real `REQ-####` format seen in Admin's Teaching Requests (e.g. `REQ-1660`)
- REQ-07: The subject list offered must be filtered/relevant to the previously selected curriculum
- REQ-08: Every curriculum card shown to real users must be genuine production data — no "for testing" / "test purpose" placeholder entries
- REQ-09: Wizard must be fully usable in both English (LTR) and Arabic (RTL) layouts
- REQ-10: Page must not show 500/404 at any step, including directly reloading mid-wizard

## Edge Cases
| EC-01 | Click Next without selecting a learner on Step 1 | Blocked — Next stays disabled (confirmed live) |
| EC-02 | Reload the browser mid-wizard (e.g. at Step 2) | Wizard either restores state or restarts cleanly at Step 1, no crash |
| EC-03 | Select every curriculum in Step 2 one at a time and check Step 3 | **Currently: empty for all tested (Saudi National Curriculum, International Curricula) — P0 regression to re-test after fix** |
| EC-04 | Select the "Here is just for testing" / "Test Curiculam" cards specifically | Should not exist in production once fixed; if still present, flag as unresolved |
| EC-05 | Go back from Step 2 to Step 1 and select a different child | Step 2's curriculum selection state should reset or stay consistent with the new learner, not silently carry over stale data |
| EC-06 | Direct navigation to `/en/dashboard/create-request` while logged out | Redirected to login, no wizard content leaks |
| EC-07 | Direct navigation to `/en/dashboard/create-request` while logged in as Student, Tutor, Child, or Admin (not Parent) | Blocked — 403/redirect, this route is Parent-only |
| EC-08 | XSS payload in any free-text field encountered in later steps (`<img src=x onerror=alert(1)>`) | Rendered as literal text everywhere it later appears (Admin Teaching Requests list, notifications), no script execution |
| EC-09 | SQL injection payload in any free-text field (`' OR 1=1--`) | Rejected or safely escaped, no 500, no data leakage |

## Test Data
### Valid
| Field | Value |
|---|---|
| name | Saudi National Curriculum |
| name | International Curricula |
| name | Qiyas Tests |
| name | English Foundation & Development |
| name | University Level |
| name | Additional Languages |
| name | Arts & Extra Skills |

### Invalid
| Field | Value |
|---|---|
| name | ' OR 1=1-- |
| name | <img src=x onerror=alert(1)> |
| name | Here is just for testing |
| name | This is just for test purpose |
