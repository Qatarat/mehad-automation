# Page: Tutor Conversations / Messages

**URL:** `https://dev.mehadedu.com/en/dashboard/messages`

## Description
Tutor messaging dashboard. Shows all conversations with students. Tutors can view chat history, send messages, check unread status, and manage inbox navigation.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Messages heading | `h1:has-text("Messages"), h2:has-text("Message")` | Required |
| Message button in sidebar | `a:has-text("Message"), [data-testid="messages-nav"]` | Required |
| Conversation list | `.conversation-list, [data-testid="conversations"]` | Required |
| Conversation item | `.conversation-item` | Required |
| Chat box | `.chat-box, [data-testid="chat-window"]` | Required |
| Message input | `input[placeholder*="message"], textarea[placeholder*="message"]` | Required |
| Send button | `button:has-text("Send"), button[aria-label*="Send"]` | Required |
| Unread tab | `[role="tab"]:has-text("Unread")` | Optional |
| All tab | `[role="tab"]:has-text("All")` | Optional |
| Unread badge | `.unread-badge, [data-testid="unread-count"]` | Optional |

## User Flows

### Flow 1: View and Send a Message
1. Log in as tutor
2. Click "Message" in sidebar
3. Conversations page loads
4. Click on a conversation with a student
5. Chat history opens
6. Type a message
7. Click Send
→ Expected: Message appears in chat, input clears

### Flow 2: Check Unread Messages
1. Navigate to messages
2. Click "Unread" tab
3. See unread conversations
4. Click conversation
5. Message marked as read
→ Expected: Unread badge decrements

### Flow 3: Switch Conversations
1. Open messages
2. Click conversation 1
3. Click conversation 2
4. Chat view updates to conversation 2
→ Expected: Correct chat history loaded

## Requirements
- REQ-01: Messages accessible from tutor dashboard sidebar
- REQ-02: All conversations displayed in list
- REQ-03: Clicking conversation loads chat history
- REQ-04: Message input accepts text
- REQ-05: Send button works and message appears
- REQ-06: Unread tab shows unread conversations
- REQ-07: Opening unread conversation marks as read
- REQ-08: Special characters in messages handled correctly

## Edge Cases
| EC-01 | Empty message send attempt | Send disabled or blocked |
| EC-02 | XSS in message content | Sanitized before render |
| EC-03 | Switch conversations quickly | No message cross-contamination |
| EC-04 | No conversations exist | Empty state shown |
| EC-05 | Network error during send | Error message shown |

## Test Data
### Valid
| Field | Value |
|---|---|
| name | 98976564 |
| name | 123456 |
| name | Hello student, how can I help? |

### Invalid
| Field | Value |
|---|---|
| name | (empty) |
| name | <script>alert(1)</script> |
