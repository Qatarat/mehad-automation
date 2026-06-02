# Spec: Messaging — Student ↔ Tutor

**URLs:**
- Student: `/en/dashboard/messages` and `/en/dashboard/messages?user={tutorUserId}`
- Tutor: `/en/dashboard/messages`
**Last verified:** 2026-06-02

---

## Overview

The messaging system allows students and tutors to exchange direct messages. Conversations are initiated from the tutor's public profile page (via the "Message" button) or from the find-tutors listing card. The message thread page shows the conversation list on the left, the chat area in the center, and tutor/student details on the right.

---

## Initiation Paths

### From Tutor Profile
- URL: `/en/tutor/{id}`
- Click `button "Message"` on the tutor profile header
- Redirects to: `/en/dashboard/messages?user={tutorUserId}`
- Example: `/en/dashboard/messages?user=326`

### From Find Tutors Card
- URL: `/en/find-tutors`
- Click `button "Message"` on a tutor card
- Same redirect behavior

---

## Page Structure — Student Messages

**URL:** `/en/dashboard/messages`

### Sidebar
- Standard student sidebar (My Bookings, Messages, Favorite Teachers, Payment & Wallet, Reviews & Ratings, Settings, Help Center)

### Main Area
- `heading[level=1]` "Messages"
- Left panel — Conversation List:
  - Search: `textbox "Search conversations..."`
  - Filter tabs: "All", "Unread (N)", "Archived"
  - Conversation rows: avatar + tutor name + timestamp + message preview + unread badge count
- Center panel — Chat Area:
  - `heading[level=2]` "Direct chat"
  - Message bubbles with timestamp
  - Sent messages appear on the right with "You" avatar
  - Received messages appear on the left with tutor avatar
  - Input row: attachment icon + `textbox "Your message"` + send button
- Right panel — Details:
  - `heading[level=2]` "Details"
  - Tutor avatar, name, "Tutor" label, rating, price
  - `button "Share"`, `button "Archive"`
  - 3-step process guide: "Select time" → "Make a payment" → "Join lesson in Mehad classroom"
  - `button "Book Trial Lesson"`

---

## Page Structure — Tutor Messages

**URL:** `/en/dashboard/messages`

### Conversation List Features
- Filter tabs: All, Unread (N), Archived
- Search: `textbox "Search Conversations"` (note: capital C vs student version)
- Conversation rows show:
  - Student/system avatar or initials
  - Conversation name (student name or group session name)
  - Timestamp
  - Message preview
  - Unread badge

---

## BDD Scenarios

#### Scenario 1: Student initiates new conversation from tutor profile
```
Given the student is logged in and on /en/tutor/89
When the student clicks the "Message" button
Then the browser navigates to /en/dashboard/messages?user=326
And the left panel shows a conversation entry for "Automations Tutor"
And the preview shows "No messages yet"
And the center panel shows "Direct chat"
And the message textbox is empty and enabled
And the send button is disabled (no text yet)
```

#### Scenario 2: Student sends a message
```
Given the student is on /en/dashboard/messages?user=326
When the student clicks the message textbox "Your message"
And types "Hello teacher, I just booked a session - QA test"
Then the send button becomes enabled
When the student clicks the send button
Then the message appears in the center panel as a sent bubble at the current time
And the conversation list preview updates to show the message text
And the timestamp shows e.g. "1:48 PM"
```

#### Scenario 3: Tutor sees incoming message with unread badge
```
Given the student sent a message to the tutor
When the tutor logs in and navigates to /en/dashboard/messages
Then the sidebar "Messages" link shows a badge count of "1"
And the conversation list shows "Automations Student" with unread badge "1"
And the preview shows "Hello teacher, I just booked a session - QA test"
And the timestamp shows "1:48 PM"
```

#### Scenario 4: Empty conversations state
```
Given the student has no conversations yet
When the student navigates to /en/dashboard/messages
Then the center panel shows:
  - An empty state icon
  - Heading "No conversation selected"
  - Text "Select a conversation from the list to start chatting"
And the left panel shows no conversation rows
```

#### Scenario 5: Tutor has system/group conversation
```
Given the tutor is on /en/dashboard/messages
Then the conversation list also shows group session threads
And one thread is titled "QA Math Group Session" (system message)
And its preview shows "Hello from teacher - QA test message"
```

---

## Real Selectors Observed

| Element | Selector |
|---|---|
| Messages page heading | `h1:has-text("Messages")` |
| Search conversations (student) | `textbox[placeholder="Search conversations..."]` |
| Search conversations (tutor) | `textbox[placeholder="Search Conversations"]` |
| Filter tab All | `generic:has-text("All")[cursor=pointer]` |
| Filter tab Unread | `generic:has-text("Unread")` + badge sibling |
| Filter tab Archived | `generic:has-text("Archived")` |
| Conversation row | `generic[cursor=pointer]` in left panel |
| Message textbox | `textbox[name="Your message"]` |
| Send button | Icon-only `button` next to message textbox (enabled when text present) |
| Direct chat heading | `h2:has-text("Direct chat")` |
| Sent message bubble | `paragraph` inside right-aligned bubble with timestamp |
| Details panel heading | `h2:has-text("Details")` |
| Share button | `button:has-text("Share")` |
| Archive button | `button:has-text("Archive")` |
| Book Trial Lesson (details panel) | `button:has-text("Book Trial Lesson")` |

---

## Empty / Error States

- No conversations: center panel shows "No conversation selected" with descriptive text
- No messages in conversation: conversation preview shows "No messages yet"
- Send button disabled when message textbox is empty
- Unread count badge shows "0" when all messages read
