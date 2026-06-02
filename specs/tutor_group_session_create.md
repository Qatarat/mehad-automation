# Spec: Tutor Group Session — Create Flow

**URL:** `/en/dashboard/availability` (button in page header triggers creation)
**Role:** Tutor
**Dynamic dates:** All dates computed by `tests/date_helpers.group_session_date()` — always the next Monday that is ≥ 8 days away so it never conflicts with the 1-on-1 slot Monday.

---

## Overview

Group sessions are created via a 3-step wizard modal launched from the "Group sessions" button on the Availability Calendar page. The `/en/dashboard/group-sessions` page itself only lists existing sessions; it has no create button.

---

## Entry Point

- Navigate to `/en/dashboard/availability`
- Click `button:has-text("Group sessions")` in the page header
- The 3-step wizard dialog opens with title "Create Group Session"

---

## Wizard Steps

### Step 1: Session Info

**Fields observed:**
- `textbox` "Session Name" — free text, e.g., "QA Math Group Session"
- `textbox` "Subject" — **read-only**, auto-filled by system based on tutor's subjects (observed value: "Math")
- `textbox` or `combobox` "Level" — e.g., "Middle School"
- `textarea` "Description" — optional description

**Behavior:**
- Subject field is `readonly` and cannot be typed into; attempting fill causes timeout
- Continue/Next button becomes enabled once required fields are filled

### Step 2: Schedule

**Fields observed:**
- "From" date picker — calendar input
- "To" date picker — calendar input (must be >= From date)
- Day-of-week toggle: S M T W T F S buttons
- "Start Time" combobox — 30-minute increments 12:00 AM to 11:30 PM
- "End Time" combobox — 30-minute increments, only times after start time enabled
- "Max Students" numeric input — e.g., 10

**Behavior:**
- Day-of-week selection is required and independent from date range selection
- Both date range AND explicit day button click required to enable Apply/Next

### Step 3: Pricing

**Fields observed:**
- "Price per Student" numeric input (SAR)
- Summary preview of session details
- "Create" / "Submit" button

---

## BDD Scenarios

#### Scenario 1: Open group session creation wizard
```
Given the tutor is on /en/dashboard/availability
When the tutor clicks the "Group sessions" button
Then a dialog opens with title "Create Group Session"
And the wizard shows Step 1 indicator active
And Step 2 and Step 3 indicators are visible but inactive
```

#### Scenario 2: Fill Step 1 session info
```
Given the Create Group Session dialog is on Step 1
When the tutor enters "QA Math Group Session" in the Session Name textbox
And the Subject field shows "Math" (read-only, auto-set)
And the tutor enters description text
And clicks "Next"
Then the wizard advances to Step 2 (Schedule)
```

#### Scenario 3: Fill Step 2 schedule
```
# Use group_session_date() — next Monday ≥ 8 days from today
Given the wizard is on Step 2
When the tutor sets From date to <group_session_input>  # e.g. "2026-07-14", computed at runtime
And sets To date to <group_session_input>               # same date (single-week session)
And clicks the "M" day button to select Monday
And selects Start Time "10:00 AM"
And selects End Time "12:00 PM"
And sets Max Students to "10"
And clicks "Next"
Then the wizard advances to Step 3 (Pricing)
```

#### Scenario 4: Fill Step 3 pricing and submit
```
Given the wizard is on Step 3
When the tutor enters "50" in the Price per Student field
And clicks the "Create" button
Then the dialog closes
And a success toast appears
And the group session "QA Math Group Session" appears in the list at /en/dashboard/group-sessions
```

#### Scenario 5: View group sessions list
```
Given the tutor navigates to /en/dashboard/group-sessions
Then the page shows a list of created group sessions
And each row shows: session name, subject, schedule, enrollment status (e.g. "0 / 10 Students"), price
And there is no "Create" button on this page (creation only via Availability Calendar)
```

---

## Group Session Data (Observed)

| Field | Value |
|---|---|
| Name | QA Math Group Session |
| Subject | Math |
| Timeframe | <group_session_short> - <group_session_short>, <year>  (computed: next Monday ≥ 8 days) |
| Day | Monday |
| Time | 10:00 AM – 12:00 PM |
| Duration | 2 hours |
| Price | 50 SAR per student |
| Max Students | 10 |
| Sessions count | 1 |

---

## Real Selectors Observed

| Element | Selector / Pattern |
|---|---|
| Group sessions button (entry) | `button:has-text("Group sessions")` on availability page |
| Session Name input | `textbox[name="Session Name"]` |
| Subject input (readonly) | `textbox` with `[readonly]` attribute, value "Math" |
| Day-of-week M button | `button` inside day-toggle row |
| Start Time combobox | `[role=combobox]` (first time picker) |
| End Time combobox | `[role=combobox]` (second time picker) |
| Max Students input | `input[type="number"]` |
| Price input | `input[type="number"]` in step 3 |

---

## Error / Edge States

- Subject field is readonly — filling it causes no change; do not attempt to type in it
- Day button must be clicked explicitly even if date is set to that day
- "QA Math Group Session" shows on tutor profile under "Group Session" tab with "Enroll in this batch" button visible to students
- Empty state on `/en/dashboard/group-sessions`: "No group sessions found" when none exist
