# Spec: Student — Enroll in Group Session

**URL:** `/en/tutor/{id}` → Group Session tab → Enroll → `/en/payment`
**Role:** Student
**Last verified:** 2026-06-02

---

## Overview

Students enroll in group sessions via the tutor's public profile page. The "Group Session" tab shows available batches; clicking "Enroll in this batch" opens a 2-step booking modal that redirects to PayTabs on confirmation.

---

## Entry Point

1. Navigate to `/en/tutor/89` (Automations Tutor profile)
2. Click `button "Group Session"` tab

---

## BDD Scenarios

#### Scenario 1: Switch to Group Session tab on tutor profile
```
Given the student is on /en/tutor/89
And the "1-to-1" tab is active by default
When the student clicks the "Group Session" button
Then the tab becomes [active]
And the section heading "Group Courses" appears
And a group session card is displayed showing:
  - Heading: "QA Math Group Session"
  - Price: "50 SAR per student"
  - Timeframe: "Jun 15 - Jun 15" with calendar icon
  - Sessions: "1 Sessions"
  - Enrollment: "0 / 10 Students" + "0% Filled"
  - Schedule: "Monday · 10:00 AM – 12:00 PM"
And a button "Enroll in this batch" is shown below the card
```

#### Scenario 2: Open group session enrollment modal
```
Given the Group Session tab is active and shows "QA Math Group Session"
When the student clicks "Enroll in this batch"
Then a dialog "Book Group Session" opens
And the header shows: "Book Group Session" + "Automations Tutor - Math"
And Step 1 "Select Sessions" is active
And Step 2 "Review Details" is inactive
And the session card shows:
  - Thumbnail image
  - Heading: "QA Math Group Session"
  - Dates: "Jun 15 - Jun 15, 2026"
  - Time: "10:00 AM • 1 classes"
  - Day: "Mon"
  - Availability: "10 seats left (0/10)"
  - Price: "50 SAR" with a selected indicator (checkmark icon)
And a note: "After completing payment, you'll schedule all your lessons."
And a "Continue" button
```

#### Scenario 3: Proceed to Step 2 review
```
Given the enrollment modal is on Step 1 with the session card visible
When the student clicks "Continue"
Then the modal advances to Step 2 "Review Your Package"
And Step 1 shows a checkmark (completed)
And the review screen shows:
  - Heading: "Review Your Package"
  - Sub-heading: "Please confirm all details are correct"
  - Tutor card: Avatar + "Automations Tutor" + "Math"
  - Section: "Group Session Details"
    - Topic: "QA Math Group Session"
    - Timeframe: "Jun 15, 2026 - Jun 15, 2026" + "Monday 10:00 AM - 12:00 PM"
    - Duration: "2 hours"
  - Info note: "After completing payment, you'll schedule all your 1 session with Automations Tutor at times that work for both of you."
  - Payment Summary section:
    - "Group Session": 50 SAR
    - "Total Amount": 50 SAR
  - Promo code row: textbox "Enter promo code" + disabled "Apply" button
  - Note: "Have a promo code? Apply it above to get a discount"
  - Security note with heading "Secure Payment" — "Your payment is encrypted and secure"
  - Footer: Total Amount 50 SAR + "Confirm & Pay" button [active]
```

#### Scenario 4: Confirm and redirect to payment
```
Given the enrollment modal shows Step 2 review with correct details
When the student clicks "Confirm & Pay"
Then the student is redirected to /en/payment with params:
  - bookingNumber=DBK-{date}-{id}
  - gatewaySlug=paytabs
  - customerName=Automations%20Student
  - customerEmail=automationstudent%40gmail.com
  - customerPhone=%2B88098976564
  - price=50
  - bookingType=group
```

**Note:** The `bookingType=group` query param differentiates group bookings from 1-to-1 on the payment page.

---

## Group Session Card Data (Observed)

| Field | Value |
|---|---|
| Name | QA Math Group Session |
| Price | 50 SAR per student |
| Timeframe | Jun 15 - Jun 15, 2026 |
| Day | Monday |
| Time | 10:00 AM – 12:00 PM |
| Duration | 2 hours |
| Sessions | 1 |
| Capacity | 0 / 10 (0% filled) |

---

## Real Selectors Observed

| Element | Selector |
|---|---|
| Group Session tab | `button:has-text("Group Session")` |
| Group Courses heading | `generic:has-text("Group Courses")` |
| Session title | `h3:has-text("QA Math Group Session")` |
| Enroll button | `button:has-text("Enroll in this batch")` |
| Dialog title | `h2:has-text("Book Group Session")` |
| Step 1 label | `generic:has-text("Select Sessions")` |
| Step 2 label | `generic:has-text("Review Details")` |
| Continue button | `button:has-text("Continue")` |
| Confirm & Pay | `button:has-text("Confirm & Pay")` |
| Promo input | `textbox[placeholder="Enter promo code"]` |

---

## Empty / Error States

- No group sessions: The "Group Session" tab shows empty state if the tutor has not created any group sessions
- Seats filled: When "0/10 Students" shows "10/10", the Enroll button is expected to be disabled or show "Full"
- Payment not completed: Session does not appear in student's bookings dashboard until PayTabs payment succeeds
