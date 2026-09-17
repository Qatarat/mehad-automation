# Page: Parent Checkout — Saudi Payments, VAT & Invoices

**URL:** `https://dev.mehadedu.com/en/dashboard/checkout`

## Description
`student_payment.md` covers the Student role's payment UI. This spec covers the same checkout surface from the **Parent** role, who is typically the actual payer for a child's sessions on this platform (dashboard.html's "Saudi Payments & Checkout" feature: Mada, Visa/Mastercard, Apple Pay, 15% Saudi VAT, ZATCA e-invoices) — previously untested from the Parent's own account/session.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Checkout summary panel | `[data-testid="checkout-summary"], :text("Order Summary")` | Required |
| Child selector (whose session is being paid) | `select[name*="child" i]` | Required |
| Base price line item | `:text("Subtotal"), :text("Price")` | Required |
| VAT line item | `:text("VAT"), :text("15%")` | Required |
| Total (price + VAT) | `:text("Total")` | Required |
| Payment method: Mada | `button:has-text("Mada"), input[value="mada"]` | Required |
| Payment method: Visa/Mastercard | `button:has-text("Visa"), button:has-text("Mastercard")` | Required |
| Payment method: Apple Pay | `button:has-text("Apple Pay")` | Required — must only appear on supported browsers/devices |
| Card number field | `input[placeholder*="Card Number" i]` | Required |
| Card expiry field | `input[placeholder*="MM/YY" i], input[placeholder*="Expiry" i]` | Required |
| Card CVV field | `input[placeholder*="CVV" i]` | Required |
| Promo code input | `input[placeholder*="promo" i], input[placeholder*="coupon" i]` | Required |
| Apply promo button | `button:has-text("Apply")` | Required |
| Pay/Confirm button | `button:has-text("Pay"), button:has-text("Confirm Payment")` | Required |
| Invoice/receipt download | `button:has-text("Invoice"), button:has-text("Receipt")` | Required — after successful payment |

## User Flows

### Flow 1: Complete Checkout With Mada
1. Log in as Parent, initiate a booking/checkout for a child (see `parent_dashboard.md` Flow 3)
2. On checkout, select payment method "Mada"
3. Enter valid test card details
4. Click "Pay"
→ Expected: Payment succeeds, total charged = base price + 15% VAT, invoice/receipt available immediately

### Flow 2: Verify 15% VAT Calculation
1. Reach checkout with a known base price (e.g. SAR 100)
→ Expected: VAT line item shows SAR 15.00 (exactly 15%), Total shows SAR 115.00 — matching Saudi tax law

### Flow 3: Apply a Valid Promo Code
1. On checkout, enter a valid promo code
2. Click "Apply"
→ Expected: Discount is applied to the subtotal BEFORE VAT is recalculated (verify VAT is computed on the post-discount amount, matching ZATCA rules, not the pre-discount amount)

### Flow 4: Apple Pay Visibility by Platform
1. Load checkout on a non-Apple browser/device (e.g. Chrome on Windows/Android emulation)
→ Expected: Apple Pay option is hidden (regression guard — this exact bug was previously found and fixed on the mobile Try On product per TC-017/BUG-04; verify Mehad's own checkout doesn't have the same defect)

### Flow 5: Download Invoice After Payment
1. Complete a successful payment
2. Click "Invoice"/"Receipt"
→ Expected: Downloaded/rendered invoice itemizes base price, VAT amount, VAT rate (15%), total, and a ZATCA-compliant structure if applicable (QR code / tax number, if the platform implements e-invoicing)

## Requirements
- REQ-01: VAT is always calculated as exactly 15% of the (post-discount, if any) subtotal
- REQ-02: Total charged always equals subtotal minus discount plus VAT — verify the arithmetic, not just that a total is shown
- REQ-03: Apple Pay is only offered on platforms/browsers that actually support it
- REQ-04: A successful payment always produces a retrievable invoice/receipt
- REQ-05: Card fields (number/expiry/CVV) validate format before allowing submission
- REQ-06: A Parent can only pay for/see checkout for their own linked children, never another family's booking (IDOR check)
- REQ-07: Failed payment (declined card) must not create a booking or invoice, and must show a clear retry path
- REQ-08: Promo code validation happens server-side too — an invalid/expired code cannot be forced through by resubmitting the same request
- REQ-09: Page title must not contain 500 or 404 anywhere in checkout

## Edge Cases
| EC-01 | Submit checkout with empty card fields | Pay button disabled or inline validation errors |
| EC-02 | Card number with letters instead of digits | Rejected, numeric-only enforced |
| EC-03 | Expired card expiry date (e.g. 01/20) | Rejected with a clear "card expired" style error |
| EC-04 | CVV with wrong length (2 digits or 5 digits) | Rejected with inline validation |
| EC-05 | Apply an invalid/nonexistent promo code (`FAKEPROMO`) | Clear "invalid code" error, no discount applied |
| EC-06 | Apply an expired promo code | Clear "expired" error, no discount applied |
| EC-07 | Apply the same valid promo code twice in one checkout | Only applied once, no stacking/double discount |
| EC-08 | Promo code field with XSS payload (`<IMG SRC=x>`) or SQLi (`' OR 1=1--`) | Rejected as invalid code format, no script execution, no 500 |
| EC-09 | Network failure/timeout right after clicking Pay | No duplicate charge on retry; either payment is confirmed idempotently or clearly shown as failed with no booking created |
| EC-10 | Double-click Pay button rapidly | Only one payment/booking is created, not two |
| EC-11 | Attempt checkout for a child that does not belong to the logged-in parent (manipulated child ID in request) | Blocked — 403, no cross-family payment possible |
| EC-12 | Session/currency shown for a Saudi-based checkout | Amounts display in SAR with correct formatting, not a default/wrong currency |

## Test Data
### Valid
| Field | Value |
|---|---|
| name | Mada |
| name | Visa |
| name | 100.00 |
| name | 15.00 |
| name | 115.00 |

### Invalid
| Field | Value |
|---|---|
| name | FAKEPROMO |
| name | ' OR 1=1-- |
| name | <IMG SRC=x> |
| name | 01/20 |
| name | abcd |
