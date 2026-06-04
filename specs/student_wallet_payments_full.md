# Spec: Student — Wallet & Payments (Full)

**URL:** `/en/dashboard/wallet`
**Role:** Student
**Last verified:** 2026-06-02

---

## Overview

The student wallet/payments page shows recent transactions. It is the student's financial history view. Transactions appear only after successful payment via PayTabs. The page has a simple list structure with a "Recent Transactions" section.

---

## Page Structure

### Sidebar (Student)
- My Bookings, Messages, Favorite Teachers, Payment & Wallet, Reviews & Ratings, Settings, Help Center

### Main Content
- `heading[level=1]` "Payments"
- Section: "Recent Transactions"
- Transaction list or empty state: "No transactions found"

---

## Payment Gateway (MyFatoorah)

> **Note (verified 2026-06-04):** The actual gateway is **MyFatoorah**, not PayTabs.
> The URL slug `gatewaySlug=paytabs` is the internal Mehad identifier; the embedded
> widget loads from `demo.myfatoorah.com` (sandbox — no real charges).
> 3DS uses an ACS emulator with Y/N result dropdown.

**URL pattern:** `/en/payment?bookingNumber=DBK-{date}-{id}&gatewaySlug=paytabs&customerName={name}&customerEmail={email}&customerPhone={phone}&price={amount}[&bookingType=group]`

**Sandbox test cards:**
| Card | Number | CVV | Expiry |
|---|---|---|---|
| Visa (approve) | `4111111111111111` | `100` | `05/28` |
| Mastercard (approve) | `5123456789012346` | `100` | `05/25` |

### Payment Page Structure
- `heading[level=1]` "Payment"
- Info row:
  - "Booking Number": `generic:has-text("DBK-...")` e.g., "DBK-20260604-TRI8FU"
  - "Total Amount": amount + SAR icon
- Payment method selector:
  - `button "Card Supported card types"` [pressed] — card payment (default selected)
  - Card type icons displayed (Visa, Mastercard, etc.)
- `iframe#MFEmbeddedIframe` — MyFatoorah embedded card widget (cross-origin, use `frame_locator`)
  - `textbox "Card Holder Name"` — placeholder "Name on Card"
  - `textbox "Card Number"` — placeholder "Card number" (auto-formats with spaces)
  - `textbox "Expiry Date"` — placeholder "MM / YY"
  - `textbox "Security Code"` — placeholder "CVV"
- `button "Pay now"` — outside iframe, on main page
- After Pay now: `iframe[title="3D Secure"]` > `iframe[name="challengeFrame"]` — ACS emulator
  - Combobox with Y/N options (default: Y = Successful)
  - `button "Submit"` — approves or declines 3DS
- Security note: `generic:has-text("Your card details are encrypted and securely processed.")`

---

## BDD Scenarios

#### Scenario 1: Student wallet with no completed payments
```
Given the student has initiated bookings but not completed PayTabs payment
When the student navigates to /en/dashboard/wallet
Then the heading "Payments" is displayed
And the "Recent Transactions" section is shown
And the text "No transactions found" appears
```

#### Scenario 2: Payment page for 1-on-1 session booking
```
Given the student clicked "Confirm & Pay" from the 1-on-1 booking modal
When the payment page loads at /en/payment?...&price=50
Then the heading "Payment" is shown
And the booking number "DBK-{date}-{id}" is displayed
And the total amount shows "50 SAR"
And the "Card" payment method button is pre-selected [pressed]
And a PayTabs iframe renders for card entry
And a "Pay now" button is visible
And the footer note "Your card details are encrypted and securely processed." is shown
```

#### Scenario 3: Payment page for group session booking
```
Given the student clicked "Confirm & Pay" from the group session enrollment modal
When the payment page loads at /en/payment?...&price=50&bookingType=group
Then the heading "Payment" is shown
And the booking number matches a group booking format
And the total amount shows "50 SAR"
And the page structure is identical to the 1-on-1 payment page
And the URL includes the query param bookingType=group
```

#### Scenario 4: Transaction appears after successful payment (expected behavior)
```
Given the student completed card payment via PayTabs
When the payment gateway redirects back to the platform with success
Then the booking status changes to confirmed
And the booking appears in /en/dashboard/bookings under "Upcoming Sessions"
And a transaction entry appears in /en/dashboard/wallet "Recent Transactions" showing:
  - Session or booking reference
  - Amount: 50 SAR
  - Date and time
  - Status: "Completed" or "Paid"
```

---

## Booking Dashboard (Student)

**URL:** `/en/dashboard/bookings`

### Page Structure
- `heading[level=1]` "Hello {studentName}"
- Subtitle: "Manage your upcoming and past sessions"
- Balance button: `button "Unbooked 0.0 hours"` — shows unused booked hours
- Sub-tabs:
  - `button "Upcoming Sessions"` — lists future confirmed bookings
  - `button "Session History"` — lists past sessions
- Empty state card when no bookings:
  - Heading: "Find Your Perfect Teacher"
  - Text: "Browse 500+ qualified teachers and book your trial lesson"
  - `link "Browse & Book Sessions"` → `/en/find-tutors`
- Session list (when bookings exist — expected):
  - Session card with tutor name, subject, date, time, status

### BDD Scenario

#### Scenario 5: Empty bookings state
```
Given the student has not completed payment for any session
When the student navigates to /en/dashboard/bookings
Then the heading "Hello Automations Student" is shown
And "Manage your upcoming and past sessions" paragraph is shown
And "Unbooked 0.0 hours" button is shown
And the tabs "Upcoming Sessions" and "Session History" are shown
And the "Find Your Perfect Teacher" card is shown
And "No upcoming sessions found" text appears
And "Book your first session to get started!" paragraph appears
```

---

## Real Selectors Observed

| Element | Selector |
|---|---|
| Wallet page heading | `h1:has-text("Payments")` |
| Recent Transactions label | `generic:has-text("Recent Transactions")` |
| Empty transactions state | `generic:has-text("No transactions found")` |
| Payment page heading | `h1:has-text("Payment")` |
| Booking number display | `generic:has-text("Booking Number")` sibling showing "DBK-..." |
| Total Amount display | `generic:has-text("Total Amount")` |
| Card payment button | `button:has-text("Card")` |
| Pay now button | `button:has-text("Pay now")` |
| PayTabs iframe | `iframe` |
| Bookings heading | `h1:has-text("Hello")` |
| Unbooked hours | `button:has-text("Unbooked")` |
| Upcoming Sessions tab | `button:has-text("Upcoming Sessions")` |
| Session History tab | `button:has-text("Session History")` |
| Browse & Book button | `button:has-text("Browse & Book Sessions")` |
| No sessions text | `generic:has-text("No upcoming sessions found")` |

---

## Empty / Error States

- "No transactions found" — when no payments have been completed
- "No upcoming sessions found" — when no bookings are confirmed
- Payment iframe may fail to load if PayTabs is not configured for the dev environment
- Booking number format: `DBK-{YYYYMMDD}-{6-char-id}`, e.g., `DBK-20260602-1QYPVO`
- `bookingType=group` is appended to the URL for group session payments

---

## Auth Flow Reference (Student Login)

**Entry:** Homepage `/en` → `button:has-text("Log In")` → dialog "Welcome back"

1. Click country code `button "Country code"` → listbox "Country codes" appears
2. Select `option "Bangladesh +880"`
3. Fill `textbox "50 123 4567"` with `98976564`
4. Validation text: "Valid phone number" (with green icon) appears
5. Click `button "Send Code"` (enabled after valid phone)
6. Toast: "Verification code sent successfully"
7. OTP textbox `textbox "000000"` becomes active
8. Fill OTP with `123456`
9. Click `button "Continue"` (enabled after OTP filled)
10. Toast: "Logged in successfully!"
11. Dialog closes, page shows "Automations Student" in nav header
