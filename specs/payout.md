# Page: Super Admin Payout Management

**URL:** `https://dev.mehadedu.com/en/dashboard/payout`

## Description
Super Admin payout management. Shows Total Help, Pending Payouts, Total Payouts cards. Admin approves tutor payout requests. Approved payouts update tutor's available balance.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Payout heading | `h1:has-text("Payout"), h2:has-text("Payouts")` | Required |
| Total Help card | `:has-text("Total Help"), [data-testid="total-help"]` | Required |
| Pending Payouts card | `:has-text("Pending Payouts"), [data-testid="pending-payouts"]` | Required |
| Total Payouts card | `:has-text("Total Payouts"), [data-testid="total-payouts"]` | Required |
| Pending payouts table | `table, [data-testid="payout-list"]` | Required |
| Tutor name column | `th:has-text("Tutor"), td` | Required |
| Payout amount | `.payout-amount, [data-testid="amount"]` | Required |
| Status column | `th:has-text("Status"), .status-badge` | Required |
| Approve button | `button:has-text("Approve")` | Required |
| Three dot menu | `button[aria-label*="actions"]` | Optional |
| View Session Details | `[role="menuitem"]:has-text("View Session Details")` | Optional |
| Manual Trigger button | `button:has-text("Manual Trigger")` | Optional |

## User Flows

### Flow 1: Approve Payout Request
1. Login as super admin
2. Navigate to Payout section
3. Find pending payout in table
4. Click "Approve"
→ Expected: Status changes to Paid, tutor balance updated

### Flow 2: View Session Details
1. Find payout request
2. Click three-dot menu
3. Click "View Session Details"
4. Full breakdown shown
→ Expected: Sessions, fees, and date breakdown visible

### Flow 3: View Payout Dashboard Stats
1. Navigate to payout page
2. View Total Help, Pending Payouts, Total Payouts cards
→ Expected: Accurate statistics displayed

## Requirements
- REQ-01: Payout page shows 3 summary cards
- REQ-02: Pending payouts list shows tutor name, sessions, amount, date range, fees, status
- REQ-03: Approve changes status from Pending to Paid
- REQ-04: Approval updates tutor's available balance
- REQ-05: Manual Trigger button creates test payout requests
- REQ-06: Session details modal shows full breakdown

## Edge Cases
| EC-01 | Approve already-approved payout | Error or button disabled |
| EC-02 | No pending payouts | Empty state in list |
| EC-03 | View details for old payout | Historical data shown |

## Test Data
### Valid
| Field | Value |
|---|---|
| name | 98976564 |
| name | 123456 |

### Invalid
| Field | Value |
|---|---|
| name | 000000 |
