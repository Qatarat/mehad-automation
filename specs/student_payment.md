# Page: Student Payment

**URL:** `https://dev.mehadedu.com/en/payment`

**URL (dev):** `https://dev.mehadedu.com/en/payment?bookingNumber=...`
**URL (prod):** `https://mehadedu.com/en/payment?bookingNumber=...`

## Description
Payment flow for booking sessions. Students fill card details inside a MyFatoorah embedded iframe to pay for 1-to-1 or group sessions.

**Gateway:** MyFatoorah (slug in URL is `paytabs` but the actual widget is MyFatoorah)

### Dev Environment
**MyFatoorah host:** `demo.myfatoorah.com` — **NO real charges (sandbox)**
**Test card:** `4111 1111 1111 1111` · CVV `100` · Expiry `05/28`
**3DS:** ACS Emulator iframe auto-approves with "Y = Successful" (sandbox only)

### Production Environment
**MyFatoorah host:** `sa.myfatoorah.com` — **LIVE gateway — real charges apply**
**Test card:** `4111 1111 1111 1111` is **rejected** by the live gateway (no real charge, clean failure)
**Error handling:** On payment failure, redirects to `/en/payment/result?status=failed&bookingNumber=...`
**3DS:** Not shown for declined cards; appears for cards that pass authorization
**To test success on prod:** Use a real Visa/MC card or a card pre-approved by MyFatoorah SA for test mode

### Payment URL Parameters
```
/en/payment?bookingNumber=BK-YYYYMMDD-XXXXXX
           &gatewaySlug=paytabs
           &customerName=...
           &customerEmail=...
           &customerPhone=...
           &price=100
```
- `bookingNumber` format on prod: `BK-YYYYMMDD-XXXXXX` (e.g. `BK-20260606-KTFE91`)
- `bookingNumber` format on dev: `DBK-YYYYMMDD-XXXXXX` (e.g. `DBK-20260101-ABC123`)

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Payment heading | `h1:has-text("Payment")` | Required |
| Booking number display | `generic:has-text("DBK-")` | Required |
| Total amount display | `generic:has-text("Total Amount")` | Required |
| Card payment button | `button:has-text("Card")` | Pre-selected |
| MyFatoorah iframe | `iframe#MFEmbeddedIframe` | Cross-origin, use frame_locator |
| Card holder name input | inside iframe — placeholder "Name on Card" | Required |
| Card number input | inside iframe — placeholder "Card number" | Required |
| Expiry date input | inside iframe — placeholder "MM / YY" | Required |
| CVV input | inside iframe — placeholder "CVV" | Required |
| Pay now button | `button:has-text("Pay now")` | Outside iframe |
| 3DS outer iframe | `iframe[title="3D Secure"]` | Appears after Pay now |
| 3DS inner iframe | `iframe[name="challengeFrame"]` | ACS Emulator |
| 3DS result dropdown | inside challengeFrame — combobox | Default: Y = Successful |
| 3DS submit button | inside challengeFrame — `button:has-text("Submit")` | Click to approve |

## User Flows

### Flow 1: Complete 1-to-1 Session Payment (sandbox)
1. Log in as student
2. Navigate to tutor profile (e.g. `/en/tutor/89`)
3. Click "Book Trial Lesson"
4. Navigate calendar to a week with available slots
5. Click a day with slots, then click a time slot (e.g. 10:00 AM)
6. Click "Continue"
7. Click "Confirm & Pay"
8. Page redirects to `/en/payment?bookingNumber=DBK-...`
9. MyFatoorah iframe loads with card form
10. Fill: Name = "Test User", Card = `4111111111111111`, Expiry = `05/28`, CVV = `100`
11. Click "Pay now"
12. 3DS ACS emulator iframe appears — "Y = Successful" is pre-selected
13. Click "Submit" inside the ACS emulator
14. → Expected: Payment succeeds, redirect to `/en/dashboard/bookings`

### Flow 2: View Wallet after Payment
1. Navigate to `/en/dashboard/wallet`
2. → Expected: Transaction record appears under "Recent Transactions"

### Flow 3: View Empty Wallet
1. Navigate to `/en/dashboard/wallet` before completing any payment
2. → Expected: "No transactions found" shown

## Requirements
- REQ-01: Payment page shows booking number, total amount in SAR
- REQ-02: "Card" payment method is pre-selected by default
- REQ-03: MyFatoorah iframe renders card holder name, card number, expiry, CVV fields
- REQ-04: Card number auto-formats with spaces (4111 1111 1111 1111)
- REQ-05: Pay now button outside the iframe triggers payment processing
- REQ-06: 3DS ACS emulator iframe appears in sandbox environment
- REQ-07: After 3DS approval, payment completes and redirects to My Bookings
- REQ-08: Payment history visible in wallet page after successful payment
- REQ-09: Invalid card number shows error inside the iframe
- REQ-10: Expired card shows error inside the iframe

## Edge Cases
| EC-01 | Invalid card number (1234) | Payment rejected with error in iframe |
| EC-02 | Expired card (01/20) | Payment rejected with error in iframe |
| EC-03 | Wrong CVV | Payment rejected or 3DS failure |
| EC-04 | Empty card holder name | Validation error in iframe |
| EC-05 | 3DS result = N (Not Authenticated) | Payment declined, error shown |
| EC-06 | Close page during processing | Payment not processed |
| EC-07 | Navigate back after Pay now | Warning or payment cancelled |
| EC-08 | Pay with valid sandbox card 4111111111111111 | Payment succeeds in sandbox |

## Test Data
### Sandbox Test Cards (MyFatoorah demo)
| Card Type | Number | CVV | Expiry | Expected Result |
|---|---|---|---|---|
| Visa (success) | `4111111111111111` | `100` | `05/28` | Payment approved |
| Mastercard (success) | `5123456789012346` | `100` | `05/25` | Payment approved |
| Visa (decline) | `4000000000000002` | `100` | `05/28` | Payment declined |

### Booking Used for Testing
| Field | Value |
|---|---|
| Tutor | Automations Tutor (profile ID 89) |
| Student | Automations Student (phone +880 **98765432**, OTP 123456) |
| Price | 100 SAR |
| Available days | Mon / Tue / Wed / Sat (Asia/Dhaka) |
| Booking number format | `DBK-YYYYMMDD-XXXXXX` |

## Automation Notes
- Student login uses phone `98765432` (student account), **not** `98976564` (tutor account).
- `book_slot_via_ui` navigates `/en/tutor/89`, handles both Trial and Package dialogs.
- Duration "1 hour" is selected before slot-picking so time ranges show correctly.
- "Next week" navigation uses `button:has-text("Next week")` (not aria-label).
- 3DS ACS emulator at `demo.myfatoorah.com` — `iframe[title="3D Secure"]` → inner `iframe[name="challengeFrame"]`.
