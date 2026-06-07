# Teacher Notifications Spec

**URL:** `https://dev.mehadedu.com/en/dashboard/notifications`

## Overview
The Notifications page (`/en/dashboard/notifications`) shows all notifications for the teacher with All and Unread tabs. Each notification has an icon, title, date, and description. A "Mark all as read" button clears the unread count. The sidebar shows a numeric badge on the Notifications link when there are unread notifications.

## URL
`/en/dashboard/notifications`

## Roles
- Teacher (authenticated)

## Prerequisites
- Teacher must be logged in: Bangladesh +880, phone 98976564, OTP 123456
- Test data: At least 1 notification ("Languages Update Approved", May 4)

## Test Scenarios

### TN-01: Notifications page loads with heading
**Given** a teacher is logged in and navigates to `/en/dashboard/notifications`
**When** the page finishes loading
**Then** the "Notifications" heading is visible
**Selectors:**
- heading: `h1:has-text("Notifications")`

### TN-02: All and Unread tabs are shown
**Given** the notifications page is loaded
**When** the user views the tab controls
**Then** "All" tab and "Unread" tab (with count badge) are visible
**Selectors:**
- all tab: `[role="tab"]:has-text("All")`
- unread tab: `[role="tab"]:has-text("Unread")`
- unread badge: `[role="tab"]:has-text("Unread") [class*="badge"], [role="tab"]:has-text("Unread") span`

### TN-03: Mark all as read button is present
**Given** the notifications page is loaded
**When** the user views the top action area
**Then** a "Mark all as read" button is visible
**Selectors:**
- mark all read: `button:has-text("Mark all as read")`

### TN-04: Notification items show title, date, and description
**Given** the notifications page has at least one notification
**When** the user views the notification list
**Then** each item shows a title (e.g. "Languages Update Approved"), timestamp, and description text
**Selectors:**
- notification item: `[role="tabpanel"] > div, [role="tabpanel"] li`
- notification title: `p:has-text("Languages Update Approved")`
- notification date: `text="May 4, 10:05 PM"`
- notification description: `p:has-text("Your languages update has been approved")`

### TN-05: Unread tab shows only unread notifications
**Given** the notifications page is loaded
**When** the user clicks the "Unread" tab
**Then** only notifications that have not been read are shown
**Selectors:**
- unread tab: `[role="tab"]:has-text("Unread")`
- unread panel: `[role="tabpanel"][aria-labelledby*="unread"]`

### TN-06: Mark all as read clears unread badge in sidebar
**Given** the teacher has unread notifications
**When** the user clicks "Mark all as read"
**Then** the notification badge in the sidebar disappears or shows 0
**Selectors:**
- mark all read: `button:has-text("Mark all as read")`
- sidebar badge: `a[href="/en/dashboard/notifications"] button`

### TN-07: Clicking a notification marks it as read
**Given** the notifications page shows an unread notification
**When** the user clicks on the notification item
**Then** the notification is marked as read (visual change: bold removed or color change)
**Selectors:**
- unread item: `[role="tabpanel"] > div[class*="unread"]`

### TN-08: Sidebar badge shows correct unread count
**Given** the teacher has at least 1 unread notification
**When** the user views the sidebar
**Then** the Notifications link shows a badge with the unread count (e.g. "1")
**Selectors:**
- sidebar notification badge: `a[href="/en/dashboard/notifications"] button:has-text("1")`

### TN-09: Negative — Empty All tab shows empty state
**Given** the teacher has no notifications at all
**When** the user views the All tab
**Then** an empty state message is displayed
**Selectors:**
- empty state: `text=/no notifications|nothing here/i`

### TN-10: Negative — Unauthenticated access redirects
**Given** a user is not logged in
**When** the user navigates to `/en/dashboard/notifications`
**Then** the user is redirected to the homepage or login
**Selectors:**
- redirect: `/en` url
