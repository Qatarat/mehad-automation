# Page: Tutor Notifications

**URL:** `https://dev.mehadedu.com/en/dashboard/notifications`

## Description
Tutor notification center. Receives notifications from admin about profile approvals, rejections, and updates. Each notification shows what action was taken. Accessible from dashboard notification bar.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Notifications heading | `h1:has-text("Notifications"), h2:has-text("Notifications")` | Required |
| Notification bell icon | `button[aria-label*="notification"], [data-testid="notification-bell"]` | Optional |
| Notification item | `.notification-item, [data-testid="notification"]` | Conditional |
| Notification text | `.notification-text, [data-testid="notification-message"]` | Conditional |
| Notification date | `time, .notification-date` | Optional |
| Mark as read | `button:has-text("Mark as read")` | Optional |
| Empty state | `:has-text("No notifications")` | Conditional |
| Unread badge | `.notification-badge, [data-testid="unread-count"]` | Optional |

## User Flows

### Flow 1: View Notifications
1. Log in as tutor
2. Navigate to dashboard
3. Click notification bell or navigate to /dashboard/notifications
4. Notification list loads
→ Expected: Notifications shown with text and date

### Flow 2: Click a Notification
1. Navigate to notifications
2. Click on a notification
3. Notification details shown
4. Notification marked as read
→ Expected: Unread badge decrements

## Requirements
- REQ-01: Notifications page accessible from tutor dashboard
- REQ-02: Admin profile approvals/rejections trigger notifications
- REQ-03: Each notification shows action description
- REQ-04: Notification can be clicked for details
- REQ-05: Empty state shown when no notifications

## Edge Cases
| EC-01 | No notifications | Empty state message shown |
| EC-02 | Many notifications | List scrollable |
| EC-03 | Notification for profile rejection | Shows specific rejection reason |
| EC-04 | Mark all as read | All unread badges clear |

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
