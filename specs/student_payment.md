# Page: Student Payment

**URL:** `https://dev.mehadedu.com/en/dashboard/wallet`

## Description
Payment flow for booking sessions. Students enter card details to pay for 1-to-1 or group sessions. Uses Stripe or similar payment processor. Test card: 4111 1111 1111 1111.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Payment modal | `[role="dialog"], .payment-modal` | Required |
| Card holder name input | `input[placeholder*="Card Holder"], input[name*="cardHolder"]` | Required |
| Card number input | `input[placeholder*="Card Number"], input[name*="cardNumber"]` | Required |
| Expiry date input | `input[placeholder*="Expir"], input[name*="expiry"]` | Required |
| Security code input | `input[placeholder*="Security Code"], input[placeholder*="CVV"], input[name*="cvv"]` | Required |
| Pay Now button | `button:has-text("Pay Now")` | Required |
| Submit button | `button:has-text("Submit")` | Required — confirmation modal |
| Confirm and Pay button | `button:has-text("Confirm & Pay"), button:has-text("Confirm and Pay")` | Required |
| Continue button | `button:has-text("Continue")` | Required — booking steps |
| Success message | `:has-text("success"), :has-text("Payment successful")` | Conditional |
| Wallet heading | `h1:has-text("Wallet"), h2:has-text("Wallet")` | Required |

## User Flows

### Flow 1: Complete Group Session Payment
1. Click "Enroll Now" on a group session
2. "Book Group Session" modal opens
3. Click "Continue"
4. Click "Confirm & Pay"
5. Payment modal opens
6. Fill Card Holder Name: Test User
7. Fill Card Number: 4111 1111 1111 1111
8. Fill Expiry Date: 05/28
9. Fill Security Code: 100
10. Click "Pay Now"
11. Confirmation modal appears
12. Click "Submit"
→ Expected: Payment success, auto-redirect to My Bookings after 3 seconds

### Flow 2: Complete 1-to-1 Session Payment
1. Select time slot on tutor profile
2. Click "Continue"
3. Click "Confirm & Pay"
4. Fill payment details (card 4111 1111 1111 1111, 05/28, CVV 100)
5. Click "Pay Now"
6. Click "Submit" in confirmation modal
→ Expected: Payment success, redirect to My Bookings

### Flow 3: View Wallet Page
1. Navigate to /en/dashboard/wallet
2. Wallet page loads with payment history
→ Expected: Payment records shown

## Requirements
- REQ-01: Payment modal shows card holder name, card number, expiry, security code fields
- REQ-02: Card number field formatted for credit card input
- REQ-03: Expiry date field accepts MM/YY format
- REQ-04: CVV/security code field is masked
- REQ-05: Pay Now button triggers payment processing
- REQ-06: Confirmation modal appears before final charge
- REQ-07: Successful payment redirects to My Bookings after 3 seconds
- REQ-08: Payment history visible in wallet page
- REQ-09: Invalid card number shows error message
- REQ-10: Expired card shows error message

## Edge Cases
| EC-01 | Invalid card number (1234) | Payment rejected with error |
| EC-02 | Expired card (01/20) | Payment rejected with error |
| EC-03 | Wrong CVV | Payment rejected or flagged |
| EC-04 | Empty card holder name | Validation error shown |
| EC-05 | Double-click Pay Now | Only one payment attempt |
| EC-06 | Close modal during payment | Payment not processed |
| EC-07 | Network error during payment | User-friendly error message |
| EC-08 | Pay with valid test card 4111111111111111 | Payment succeeds |

## Test Data
### Valid
| Field | Value |
|---|---|
| name | Test User |
| name | Visa Cardholder |
| name | Master Card |

### Invalid
| Field | Value |
|---|---|
| name | empty_holder |
| name | invalid_card |
