# Spec: Student — Book 1-on-1 Session

**URLs:** `/en/find-tutors` → `/en/tutor/{id}` → `/en/payment`
**Role:** Student (logged in via homepage modal)
**Dynamic dates:** All calendar dates are computed at runtime by `tests/date_helpers.py`.
Use `booking_slot()` (= `availability_slot_monday()`) for the next Monday ≥ 2 days ahead.
**Credentials:** +880 98976564 / OTP 123456

---

## Overview

Students find tutors via the Find Tutors page, view a tutor's profile with an availability calendar, select a date and time slot in a 2-step booking modal, and are redirected to a PayTabs payment page.

---

## Flow 1: Find Tutors Page

**URL:** `/en/find-tutors?page=1&limit=10&sortBy=createdAt&sortOrder=DESC&sort=top`

### Page Structure
- `heading[level=1]` "Find your perfect tutor"
- Filter bar:
  - `combobox` "All Subjects" (I want to learn)
  - `combobox` "All Levels"
  - `combobox` "Any price"
  - `combobox` "Any time"
  - Search: `textbox "Search tutors..."` with search icon
- Result count: e.g., "65 tutors available"
- Sort: `combobox` "Our top picks"
- Tutor cards (each clickable):
  - Avatar/initials + name + "Verified" label
  - Rating (e.g., "0.00"), review count
  - Subject, Student count, Lessons count
  - Languages
  - Bio text
  - "Trial lesson from X SAR" badge
  - Price: X SAR per hour, Trial Lesson: X SAR
  - Action buttons: `button "Book Trial Lesson"`, `button "Message"`, `button "save"`
- `button "Load more"` for pagination

### BDD Scenarios

#### Scenario 1: Search for a tutor by name
```
Given the student is on /en/find-tutors
When the student types "Automations" in the textbox "Search tutors..."
Then the URL updates to include ?search=Automations
And the results show "1 tutors available"
And one card with name "Automations Tutor" is displayed
And the card shows: Subject "Math", Price "100 SAR /hour", Trial Lesson "100 SAR"
And three buttons: "Book Trial Lesson", "Message", "save"
```

#### Scenario 2: Navigate to tutor profile
```
Given the tutor card for "Automations Tutor" is visible
When the student clicks the tutor card
Then the student is navigated to /en/tutor/89?week=YYYY-MM-DD
```

---

## Flow 2: Tutor Profile Page

**URL:** `/en/tutor/{id}?week={YYYY-MM-DD}`

### Page Structure
- Back link: "Back to search"
- Tutor info:
  - Avatar image or initials
  - Name: "Automations Tutor"
  - Location: Bangladesh (flag icon)
  - Rating: "0.0 (0 reviews)", Students: "1", Subject: "Math", Lessons: "0"
  - Buttons: `button "save"`, `button "Message"`
- Stats row: Lessons Taught (0), Average Rating (0.0), Response Rate (100%)
- Session type tabs:
  - `button "1-to-1"` (default active)
  - `button "Group Session"`
- 1-to-1 price section:
  - Radio selector: "Math — 100 SAR per hour" (selected)
- Schedule section:
  - Label: "Choose the time for your first lesson. The timings are displayed in your local timezone."
  - Week nav: `button "Prev week"`, week label, `button "Next week"`
  - Timezone `combobox` defaulting to "Asia/Dhaka"
  - 7-column calendar grid: Sun/Mon/.../Sat headers + date numbers
  - Time slot cells (clickable `generic` elements): e.g., "10:00 AM", "2:00 PM"
  - `button "Book Trial Lesson"` (fixed below schedule)
- About me section: biography, Languages, Subjects, Specialties, Education, Certifications

### BDD Scenarios

#### Scenario 3: Navigate to the week that has availability slots
```
# The teacher adds slots on next_monday, next_tuesday, next_wednesday
# computed by date_helpers — navigate to that week in the tutor profile
Given the student is on /en/tutor/89
When the student clicks "Next week" until the calendar week contains <next_monday_short>
  # Use date_helpers.booking_slot()["date"] to know the target week
Then the calendar column for Monday shows at least one available time slot
```

#### Scenario 4: Open booking modal via Book Trial Lesson
```
Given the student can see available Monday slots on the tutor profile calendar
When the student clicks "Book Trial Lesson"
Then a dialog "Book a Session" opens
And shows Step 1 "Date & Time" and Step 2 "reviewAndDetails"
And the modal calendar starts at the current week with days disabled
When the student clicks "Next week" inside the modal until <next_monday_short> is visible
Then Mon, Tue, Wed are enabled (matching the teacher's added slots)
And all time slot buttons for Monday are listed below the calendar
```

#### Scenario 5: Select date and time in booking modal
```
# slot = date_helpers.booking_slot()  (next Monday ≥ 2 days from today)
Given the booking modal shows the week containing <next_monday_short>
When the student clicks the day button for <slot.day_num>   # e.g. "07" or "14"
Then that day button becomes [active]
And the message "Please select a time slot" appears
When the student clicks time button "10:00 AM"
Then button "10:00 AM" becomes [active]
And a summary appears:
  "Selected time: <slot.display_month_day> • 10:00 AM - 10:30 AM"
And the "Continue" button becomes enabled
```

**Note:** Default duration is 0.5 hour (30 min). Duration buttons: "0.5 hour" and "1 hour" are available.

#### Scenario 6: Review and pay
```
# slot = date_helpers.booking_slot()
Given <slot.display> at 10:00 AM is selected in the booking modal
When the student clicks "Continue"
Then Step 2 "Review Your Booking" appears showing:
  - Teacher: Automations Tutor, Subject: Math
  - Duration: 30-minute Session
  - Date: <slot.display>          # e.g. "Monday, July 7, 2026" — computed at runtime
  - Time: 10:00 AM - 10:30 AM
  - Platform Fee: 15 SAR
  - Session Fee: 50 SAR, Total: 50 SAR
  - Promo code textbox "Enter promo code" with disabled "Apply" button
  - Footer: Total Amount 50 SAR + "Confirm & Pay" button [active]
When the student clicks "Confirm & Pay"
Then the student is redirected to /en/payment with params:
  - bookingNumber=DBK-{date}-{id}    # date part changes every run
  - gatewaySlug=paytabs
  - customerName=Automations%20Student
  - customerEmail=automationstudent%40gmail.com
  - customerPhone=%2B88098976564
  - price=50
```

---

## Flow 3: Payment Page

**URL:** `/en/payment?bookingNumber=...&gatewaySlug=paytabs&...&price=50`

### Page Structure
- `heading[level=1]` "Payment"
- Booking Number display: "DBK-20260602-1QYPVO"
- Total Amount: "50 SAR"
- Payment method: `button "Card Supported card types"` [pressed]
  - Shows card type icons
- `iframe` — PayTabs card entry widget
- `button "Pay now"`
- Footer note: "Your card details are encrypted and securely processed."

### BDD Scenario

#### Scenario 7: Payment page structure
```
Given the student clicked "Confirm & Pay" from booking step 2
When the /en/payment page loads
Then the heading "Payment" is shown
And the booking number is displayed (e.g., "DBK-20260602-1QYPVO")
And total amount is "50 SAR"
And a "Card" payment method button is pre-selected
And a PayTabs iframe is rendered for card entry
And a "Pay now" button is visible
And a security note "Your card details are encrypted and securely processed." is shown
```

---

## Real Selectors Observed

| Element | Selector |
|---|---|
| Search tutors input | `textbox[name="Search tutors..."]` |
| Tutor card | `generic[cursor=pointer]` containing tutor name |
| Book Trial Lesson (card) | `button:has-text("Book Trial Lesson")` |
| Message button (card/profile) | `button:has-text("Message")` |
| Save button | `button:has-text("save")` |
| 1-to-1 tab | `button:has-text("1-to-1")` |
| Group Session tab | `button:has-text("Group Session")` |
| Next week (profile calendar) | `button[name="Next week"]` |
| Timezone combobox | `combobox` showing "Asia/Dhaka" |
| Book Trial Lesson (profile) | `button:has-text("Book Trial Lesson")` |
| Modal date buttons | `button[name="08"]` (day number) |
| Modal time buttons | `button[name="10:00 AM"]` |
| Modal Continue | `button:has-text("Continue")` |
| Confirm & Pay | `button:has-text("Confirm & Pay")` |

---

## Empty / Error States

- Calendar shows "No available slots" text when tutor has no availability for that week
- Time selection required: "Please select a time slot" paragraph shown if date selected but no time chosen
- Continue button disabled until both date and time are selected
- Student bookings dashboard shows "No upcoming sessions found" when payment is not completed
