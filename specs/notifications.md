# Page: Notifications Management — Super Admin

**URL:** `https://dev.mehadedu.com/en/super-admin-login`

## Description
Super Admin notifications page for managing tutor profile change requests. Admin can view All/Unread notifications, open tutor details, and Approve or Reject profile change submissions.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Notifications link | `a:has-text("Notifications"), [data-testid="notifications-nav"]` | Required |
| All tab | `[role="tab"]:has-text("All")` | Required |
| Unread tab | `[role="tab"]:has-text("Unread")` | Required |
| Notification item | `.notification-item, [data-testid="notification"]` | Conditional |
| Tutor name in notification | `.tutor-name, [data-testid="tutor"]` | Optional |
| View button | `button:has-text("View")` | Required |
| Approve button | `[role="dialog"] button:has-text("Approve")` | Conditional |
| Reject button | `[role="dialog"] button:has-text("Reject")` | Conditional |
| Reject reason input | `textarea[placeholder*="reason"], input[placeholder*="reason"]` | Conditional |
| Approval card | `.approval-card, [data-testid="approval-block"]` | Optional |

## User Flows

### Flow 1: View and Approve Tutor Profile Change
1. Login as super admin
2. Navigate to Notifications
3. Click "Unread" tab
4. Click on a tutor profile change notification
5. Tutor profile page opens
6. Click "View" on approval request
7. Modal shows submitted changes
8. Click "Approve"
→ Expected: Changes approved, publicly visible

### Flow 2: Reject Profile Change
1. Navigate to notification
2. Click "View"
3. Review submitted info
4. Click "Reject"
5. Enter rejection reason
6. Submit
→ Expected: Tutor notified of rejection, changes not public

## Requirements
- REQ-01: Notifications page shows All and Unread tabs
- REQ-02: Profile change notifications appear when tutor submits update
- REQ-03: Clicking notification opens tutor profile
- REQ-04: View button shows approval modal with Approve/Reject
- REQ-05: Approved changes become publicly visible
- REQ-06: Rejected changes include reason for tutor
- REQ-07: Rejected changes not visible to students

## Edge Cases
| EC-01 | No notifications | Empty state shown |
| EC-02 | Approve without reviewing | Should still work |
| EC-03 | Reject without reason | Validation error |
| EC-04 | Unread badge updates on read | Badge decrements |

## Test Data
### Valid
| Field | Value |
|---|---|
| name | 98976564 |
| name | 123456 |
| name | Missing required documents |

### Invalid
| Field | Value |
|---|---|
| name | (empty for rejection) |
