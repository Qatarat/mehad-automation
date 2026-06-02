# Spec: Tutor Availability Calendar — Full Flow

**URL:** `/en/dashboard/availability`
**Role:** Tutor (logged in via `/en/tutor-login`)
**Credentials:** +880 98976564 (staging) / OTP 123456 (staging) | production: PROD_TEST_PHONE + Twilio OTP

> **Dynamic dates:** All dates in scenarios are computed at runtime by `tests/date_helpers.py`.
> Tests use the **next available Monday/Tuesday/Wednesday** (≥ 2 days from today) so they
> pass every month without any date changes.

---

## Overview

The Availability Calendar is the tutor's primary landing page after login. It displays a monthly calendar view with existing availability slots and provides controls to add new slots and manage group sessions.

---

## Page Structure

### Header
- `img[alt="Mehad logo"]` — Mehad logo linking to `/en`
- `button[name="Toggle Sidebar"]` — collapses/expands the left sidebar
- Page title section: icon + text "Availability Calendar"
- Action buttons row:
  - `button` "Group sessions" — opens Group Session creation wizard (3-step modal)
  - `button` "Add Availability Time" — opens slot creation modal

### Sidebar Navigation (Tutor)
- `link[href="/en/dashboard/availability"]` "Availability Calendar"
- `link[href="/en/dashboard/booked-sessions"]` "Booked Sessions"
- `link[href="/en/dashboard/group-sessions"]` "Group Sessions"
- `link[href="/en/dashboard/messages"]` "Messages" (with unread badge count)
- `link[href="/en/dashboard/earnings"]` "Earnings & Payouts"
- `link[href="/en/dashboard/reviews"]` "Reviews"
- `link[href="/en/dashboard/notifications"]` "Notifications" (with unread badge count)
- `link[href="/en/dashboard/instructor-profile"]` "Instructor Profile"
- `link[href="/en/dashboard/help-center"]` "Help Center"
- `button[name="Switch language"]` — toggles AR/EN
- `button[name="Open account switcher"]` — shows tutor name + "Tutor" role label, opens dropdown with "My Profile" and "Logout"

### Calendar Body
- Month navigation: `button` "Prev month" (disabled for current/past) + month label (e.g., "June 2026") + `button` "Next month"
- Timezone selector: `combobox` defaulting to "Asia/Dhaka"
- Day-of-week headers: Sun Mon Tue Wed Thu Fri Sat
- 30-day grid of clickable `generic` cells — each cell shows date number + slot summary or "No slots"
- Cells with slots show time range text (e.g., "10:00 AM - 12:00 PM") and an edit icon

---

## Feature: Add Availability Time

### BDD Scenarios

#### Scenario 1: Open the Add Availability modal
```
Given the tutor is on /en/dashboard/availability
When the tutor clicks the "Add Availability Time" button
Then a dialog titled "Add Availability" opens
And the dialog contains:
  - "From" date input (date picker)
  - "To" date input (date picker)
  - Day-of-week toggle buttons: S M T W T F S
  - "Start Time" combobox (30-minute increments from 12:00 AM to 11:30 PM)
  - "End Time" combobox (30-minute increments, only times after selected start time enabled)
  - "Apply" button (initially disabled)
  - "Cancel" button
```

#### Scenario 2: Set date range and select days
```
Given the Add Availability dialog is open
# date_helpers.availability_slot_monday() gives the next Monday ≥ 2 days from today
When the tutor sets "From" to <next_monday_input>   # e.g. "2026-07-07" computed at runtime
And sets "To" to <next_monday_input>                 # same date (single-day slot)
And clicks the "M" day button (Monday)
Then the "M" button becomes [active]
And the "Apply" button becomes enabled
```

**Observed behavior:** Selecting a single date does NOT always auto-activate the corresponding day button. The user must explicitly click the day-of-week button to enable Apply.

#### Scenario 3: Select start and end times
```
Given date range and day are selected
When the tutor opens the "Start Time" combobox
Then options appear in 30-minute increments from "12:00 AM" to "11:30 PM"
When the tutor selects "10:00 AM"
And opens the "End Time" combobox
Then only times after "10:00 AM" are enabled (e.g. "10:30 AM" through "11:30 PM")
When the tutor selects "12:00 PM"
Then the end time shows "12:00 PM"
```

#### Scenario 4: Apply creates slots
```
Given start time "10:00 AM" and end time "12:00 PM" are set with day M selected
When the tutor clicks "Apply"
Then the dialog closes
And a success toast appears
And the calendar cell for <next_monday_short> (e.g. "Jul 7")
    shows "10:00 AM - 12:00 PM" with an edit icon
```

#### Scenario 5: View slot details (Day Slots dialog)
```
Given the calendar has a slot on <next_monday_short>
When the tutor clicks that calendar cell
Then a dialog opens showing:
  - Date label: e.g., "Mon <next_monday_short> <year>" with timezone
  - Slot row: time range, type label "oneToOneShort"
  - Edit icon button (pencil)
  - Delete icon button (trash)
```

#### Scenario 6: Delete a slot
```
Given the Day Slots dialog is open for a date with a slot
When the tutor clicks the delete (trash) icon button
Then the slot is removed from the dialog and from the calendar cell
```

---

## Real Selectors Observed

| Element | Selector / Ref Pattern |
|---|---|
| Add Availability button | `button:has-text("Add Availability Time")` |
| Group sessions button | `button:has-text("Group sessions")` |
| From date input | `input[type="date"]` (first, in dialog) |
| To date input | `input[type="date"]` (second, in dialog) |
| Day-of-week buttons | `button` inside day-toggle row (S M T W T F S) |
| Start Time combobox | `[role=combobox]` (first in dialog time section) |
| End Time combobox | `[role=combobox]` (second in dialog time section) |
| Apply button | `button:has-text("Apply")` |
| Cancel button | `button:has-text("Cancel")` |
| Calendar cell | `generic[cursor=pointer]` containing date number and slot text |
| Timezone combobox | `combobox` showing "Asia/Dhaka" |

---

## Empty / Error States

- Calendar cell with no slots shows "No slots"
- "Apply" button stays disabled until both date range, at least one day, and both times are set
- End Time combobox disables options earlier than the selected Start Time
- Navigating to previous months is blocked (prev month button disabled for past months)

---

## Slot Pattern (all computed dynamically at runtime)
| Slot | Day | Computed by | Start | End |
|---|---|---|---|---|
| 1-on-1 Mon  | Next Monday ≥ 2 days from today    | `availability_slot_monday()`    | 10:00 AM | 12:00 PM |
| 1-on-1 Tue  | Next Tuesday ≥ 2 days from today   | `availability_slot_tuesday()`   | 2:00 PM  | 4:00 PM  |
| 1-on-1 Wed  | Next Wednesday ≥ 2 days from today | `availability_slot_wednesday()` | 6:00 PM  | 8:00 PM  |
| Group session Mon | Monday ≥ 8 days from today   | `group_session_date()`          | 10:00 AM | 12:00 PM |

> Import helpers: `from tests.date_helpers import availability_slot_monday, group_session_date`
