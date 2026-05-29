# Page: Student Messages

**URL:** `https://dev.mehadedu.com/en/dashboard/messages`

## Description
In-app messaging between students and tutors. Three-panel layout: conversation list (left), chat window (center), tutor details (right). Students can send messages, archive conversations, and book lessons.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Messages heading | `h1:has-text("Messages"), h2:has-text("Messages")` | Required |
| Conversation list | `.conversation-list, [data-testid="conversations"]` | Required |
| Search conversations | `input[placeholder*="Search Conversations"]` | Optional |
| All tab | `[role="tab"]:has-text("All")` | Required |
| Unread tab | `[role="tab"]:has-text("Unread")` | Optional |
| Archived tab | `[role="tab"]:has-text("Archived")` | Optional |
| Conversation item | `.conversation-item, [data-testid="conversation"]` | Required |
| Chat window | `.chat-window, [data-testid="chat"]` | Required |
| Message input | `input[placeholder*="message"], textarea[placeholder*="message"]` | Required |
| Send button | `button:has-text("Send"), button[aria-label*="Send"]` | Required |
| Archive button | `button:has-text("Archive")` | Optional |
| Book Lesson button | `button:has-text("Book Lesson")` | Optional |

## User Flows

### Flow 1: Send a Message
1. Navigate to https://dev.mehadedu.com/en/dashboard/messages
2. Click on a conversation (e.g., Test Tutor)
3. Chat window opens showing message history
4. Type message in input field
5. Click "Send" button or press Enter
→ Expected: Message appears in chat, input clears

### Flow 2: Search Conversations
1. Navigate to messages page
2. Type tutor name in search input
3. Conversation list filters in real time
→ Expected: Only matching conversations shown

### Flow 3: Archive Conversation
1. Select a conversation
2. Click "Archive" button in details panel
3. Conversation moves to Archived tab
→ Expected: Not visible in All tab, visible in Archived

## Requirements
- REQ-01: Messages page loads with three-panel layout
- REQ-02: Conversation list shows all active conversations
- REQ-03: Clicking conversation loads chat history
- REQ-04: Message input accepts text input
- REQ-05: Send button enabled only when message text exists
- REQ-06: Sent message appears immediately in chat
- REQ-07: Search filters conversation list in real time
- REQ-08: Archive moves conversation to archived tab
- REQ-09: Empty message cannot be sent
- REQ-10: Messages page requires authentication

## Edge Cases
| EC-01 | Send empty message | Send button disabled |
| EC-02 | XSS in message text | Message sanitized |
| EC-03 | Very long message | Handled without crash |
| EC-04 | Network error during send | Error message shown |
| EC-05 | Archive conversation | Moves to Archived tab |
| EC-06 | Search with no match | Empty state shown |
| EC-07 | Unauthenticated access | Redirects to login |

## Test Data
### Valid
| Field | Value |
|---|---|
| name | 98976564 |
| name | 123456 |
| name | Hello, I have a question about the lesson |

### Invalid
| Field | Value |
|---|---|
| name | (empty) |
| name | <script>alert(1)</script> |
