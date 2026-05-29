# Page: Tutor Earnings and Payout

**URL:** `https://dev.mehadedu.com/en/dashboard/earnings`

## Description
Tutor's earnings overview and payout management. Shows total earnings, available balance (withdrawable), and pending earnings (awaiting course completion). Also shows completed payouts approved by admin.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Earnings heading | `h1:has-text("Earning"), h2:has-text("Earnings")` | Required |
| Available Balance | `:has-text("Available Balance"), [data-testid="available-balance"]` | Required |
| Pending Earnings | `:has-text("Pending Earnings"), [data-testid="pending-earnings"]` | Required |
| Total Earnings | `:has-text("Total Earnings"), [data-testid="total-earnings"]` | Required |
| Complete Payouts section | `:has-text("Complete Payouts"), [data-testid="complete-payouts"]` | Required |
| Payout amount | `.payout-amount, [data-testid="payout-amount"]` | Required |
| Withdraw button | `button:has-text("Withdraw"), button:has-text("Request Payout")` | Conditional |
| Earnings list | `.earnings-list, [data-testid="earnings-list"]` | Required |
| Payout status | `:has-text("Approved"), :has-text("Pending")` | Conditional |

## User Flows

### Flow 1: View Earnings Overview
1. Navigate to https://dev.mehadedu.com/en/dashboard/earnings
2. Page shows Available Balance, Pending Earnings, Total Earnings
3. Complete Payouts section shows approved payments
→ Expected: All earnings sections displayed with correct amounts

### Flow 2: Verify Pending Earnings After Group Session
1. Create group session (students enrolled)
2. Navigate to Earnings page
3. Pending Earnings shows session revenue
4. After course completion, amount moves to Available Balance
→ Expected: Earnings lifecycle correctly tracked

### Flow 3: Verify Available Balance After 1-to-1 Session
1. Complete a 1-to-1 session
2. Navigate to Earnings page
3. Available Balance increases by session price
→ Expected: Available Balance updated

## Requirements
- REQ-01: Earnings page loads at /en/dashboard/earnings
- REQ-02: Available Balance shows withdrawable amount
- REQ-03: Pending Earnings shows revenue awaiting course completion
- REQ-04: Pending earnings move to Available Balance after course completes
- REQ-05: Complete Payouts shows all admin-approved payments
- REQ-06: Earnings are accurate and up-to-date
- REQ-07: 1-to-1 session earnings go to Available Balance
- REQ-08: Group session earnings appear in Pending Earnings until completion

## Edge Cases
| EC-01 | No sessions completed yet | All balances show zero |
| EC-02 | Pending earnings before course end | Amount stays in Pending |
| EC-03 | After course completion | Pending moves to Available |
| EC-04 | Admin approves payout | Appears in Complete Payouts |
| EC-05 | Page refresh | Balances remain accurate |

## Test Data
### Valid
| Field | Value |
|---|---|
| name | 98976564 |
| name | 123456 |
| name | positive number after session |

### Invalid
| Field | Value |
|---|---|
| name | 000 |
| name | 000 |
