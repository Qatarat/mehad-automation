# Spec: Tutor — Earnings & Payouts (Full)

**URL:** `/en/dashboard/earnings`
**Role:** Tutor
**Last verified:** 2026-06-02

---

## Overview

The Earnings & Payouts page shows the tutor's financial summary including total earnings, available balance, pending earnings, and completed payouts. It has two sub-tabs: "Earnings" (transaction history) and "Payout" (withdrawal history/request).

---

## Page Structure

### Sidebar (Tutor)
- Availability Calendar, Booked Sessions, Group Sessions, Messages (with unread badge), Earnings & Payouts, Reviews, Notifications (with unread badge), Instructor Profile, Help Center

### Main Content

#### Stats Cards Row
Four summary cards:
1. "Total Earnings" — shows SAR amount (e.g., "0.00")
2. "Available Balance" — shows SAR amount (e.g., "0.00")
3. "Pending Earnings" — shows SAR amount (e.g., "0.00")
4. "Completed Payouts" — shows SAR amount (e.g., "0.00")

Each card has an icon, label paragraph, and amount `heading[level=3]`.

#### Sub-tabs
- `button "Earnings"` — shows earnings transaction list
- `button "Payout"` — shows payout/withdrawal list

#### Earnings Tab Content
- `heading[level=3]` "Recent Earnings"
- Transaction list or empty state: "No earnings yet."

#### Payout Tab Content (expected)
- Payout request button
- Payout history list or empty state

---

## BDD Scenarios

#### Scenario 1: Earnings page initial state (no completed sessions)
```
Given the tutor has no completed/paid sessions
When the tutor navigates to /en/dashboard/earnings
Then the heading "Earnings & Payouts" is displayed
And four summary cards are shown:
  - Total Earnings: 0.00 SAR
  - Available Balance: 0.00 SAR
  - Pending Earnings: 0.00 SAR
  - Completed Payouts: 0.00 SAR
And two buttons are visible: "Earnings" and "Payout"
And the "Recent Earnings" section shows "No earnings yet."
```

#### Scenario 2: Earnings tab selected (default)
```
Given the tutor is on /en/dashboard/earnings
Then the "Earnings" tab is active by default
And "Recent Earnings" heading is visible
And "No earnings yet." text is shown when no transactions exist
```

#### Scenario 3: Switch to Payout tab
```
Given the tutor is on /en/dashboard/earnings
When the tutor clicks the "Payout" button
Then the tab switches to Payout view
And payout history or empty state is shown
```

#### Scenario 4: Earnings appear after a completed session (expected behavior)
```
Given the student completed payment and a session was conducted
When the session is marked complete by the system
Then the tutor's "Total Earnings" increases by the session fee
And a transaction appears in "Recent Earnings" showing:
  - Student name
  - Session date
  - Amount in SAR
  - Status label (e.g., "Completed")
And "Pending Earnings" may show the amount before release period
```

#### Scenario 5: Sidebar notification badge
```
Given the tutor is logged in
When the student sends a message
Then the sidebar "Messages" link shows a badge "1"
And "Notifications" link shows a badge "1" for system notifications
```

---

## Notifications Page

**URL:** `/en/dashboard/notifications`

### Page Structure
- `heading[level=1]` "Notifications"
- Sub-heading: "Notifications"
- `button "Mark all as read"` with icon
- `tablist`:
  - `tab "All"` [selected]
  - `tab "Unread N"` with count badge
- `tabpanel "All"`:
  - Notification rows: icon + message text + timestamp

### Observed Notification
- Type: "Languages Update Approved"
- Date: May 4, 10:05 PM
- Body: "Your languages update has been approved"

---

## Booked Sessions Page

**URL:** `/en/dashboard/booked-sessions`

### Page Structure
- Section header: icon + "All Sessions"
- Sub-tabs:
  - `button "Upcoming Sessions"`
  - `button "Session History"`
- Search: `textbox "Search sessions..."` + `button "Filters"`
- Session list or empty state: "No upcoming sessions found"

---

## Real Selectors Observed

| Element | Selector |
|---|---|
| Earnings page heading | `h1:has-text("Earnings & Payouts")` |
| Total Earnings card | `p:has-text("Total Earnings")` + sibling `h3` |
| Available Balance card | `p:has-text("Available Balance")` + sibling `h3` |
| Pending Earnings card | `p:has-text("Pending Earnings")` + sibling `h3` |
| Completed Payouts card | `p:has-text("Completed Payouts")` + sibling `h3` |
| Earnings tab | `button:has-text("Earnings")` |
| Payout tab | `button:has-text("Payout")` |
| Recent Earnings heading | `h3:has-text("Recent Earnings")` |
| Empty earnings state | `generic:has-text("No earnings yet.")` |
| Notifications heading | `h1:has-text("Notifications")` |
| Mark all read | `button:has-text("Mark all as read")` |
| All tab | `tab[name="All"]` |
| Unread tab | `tab:has-text("Unread")` |
| Booked Sessions search | `textbox[placeholder="Search sessions..."]` |
| Filters button | `button:has-text("Filters")` |
| Upcoming Sessions tab | `button:has-text("Upcoming Sessions")` |
| Session History tab | `button:has-text("Session History")` |

---

## Empty / Error States

- "No earnings yet." — when no sessions have been paid and completed
- "No upcoming sessions found" on Booked Sessions when no confirmed bookings exist
- All earnings summary values show "0.00" when no transactions
