# Page: Promo Code Management

**URL:** `https://dev.mehadedu.com/en/dashboard/promo-codes`

## Description
Super Admin manages promo codes for student discounts. Codes offer percentage or fixed discounts with usage limits and expiry dates. Active codes usable at checkout; disabled codes cannot be applied.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Promo Codes heading | `h1:has-text("Promo Code"), h2:has-text("Promo")` | Required |
| Create Promo Code button | `button:has-text("Create Promo Code")` | Required |
| Search input | `input[placeholder*="Search"], input[placeholder*="Promo Code"]` | Optional |
| Promo code table | `table, [data-testid="promo-list"]` | Required |
| Code name | `.code-name, [data-testid="code"]` | Required |
| Status toggle | `[role="switch"], input[type="checkbox"]` | Required |
| Action button | `button[aria-label*="actions"]` | Required |
| Edit option | `[role="menuitem"]:has-text("Edit")` | Optional |
| Delete option | `[role="menuitem"]:has-text("Delete")` | Optional |
| Code name input | `input[name="code"], input[placeholder*="Promo Code Name"]` | Required in modal |
| Discount type select | `select[name="discountType"], [placeholder*="Discount Type"]` | Required |
| Discount value input | `input[name="discountValue"], input[placeholder*="Discount Value"]` | Required |
| Usage limit input | `input[name="usageLimit"]` | Optional |
| Expiry date picker | `input[type="date"], [placeholder*="Expiry"]` | Optional |
| Create button | `button:has-text("Create")` | Required |

## User Flows

### Flow 1: Create Promo Code
1. Navigate to Promo Codes
2. Click "Create Promo Code"
3. Fill Promo Code Name: SAVE10
4. Select Discount Type: Percentage
5. Enter Discount Value: 10
6. Set Usage Limit: 100
7. Set Expiry Date
8. Toggle Status: Active
9. Click "Create"
→ Expected: Code created, appears in list

### Flow 2: Apply Promo Code at Checkout
1. Student at checkout
2. Enter promo code: SAVE10
3. Click "Apply"
→ Expected: Discount applied to final price

### Flow 3: Disable Promo Code
1. Find promo code in list
2. Toggle status to Disable
→ Expected: Code no longer usable by students

## Requirements
- REQ-01: Create Promo Code button opens creation modal
- REQ-02: Code name must be unique
- REQ-03: Discount type: Percentage or Fixed Amount
- REQ-04: Active codes apply discount at checkout
- REQ-05: Disabled codes cannot be used
- REQ-06: Expired codes are blocked
- REQ-07: Code stops working after usage limit reached

## Edge Cases
| EC-01 | Invalid promo code at checkout | Error: invalid code |
| EC-02 | Expired promo code | Error: code expired |
| EC-03 | Disabled code at checkout | Error: code not active |
| EC-04 | Code used past usage limit | Error: limit reached |
| EC-05 | Percentage over 100% | Validation error |
| EC-06 | Negative discount value | Validation error |

## Test Data
### Valid
| Field | Value |
|---|---|
| name | SAVE10 |
| name | DISCOUNT20 |
| name | PROMO5 |

### Invalid
| Field | Value |
|---|---|
| name | empty_code |
| name | negative_discount |
