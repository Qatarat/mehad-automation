# Page: Live Virtual Classroom — In-Session Controls

**URL:** `https://dev.mehadedu.com/en/dashboard/sessions`

## Description
`session.md` covers only the entry point (finding a session and clicking "Join Classroom"). This spec covers what happens **inside** the live classroom itself once joined: dual WebRTC video streams (tutor + student), audio mute/unmute, camera on/off, screen share, a collaborative whiteboard, and in-session text chat. The local scratch scripts `capture_whiteboard_drawing_and_settings.cjs` and `test_full_video_call_features.cjs` (in `QA-Projects/Mehad/automation/`) indicate this area has real known-tricky behavior (dual classroom sync, whiteboard persistence) but it was never captured as a spec, so it wasn't part of the generated/CI'd suite at all.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Local video tile | `video[data-testid="local-video"], video:nth-of-type(1)` | Required |
| Remote (peer) video tile | `video[data-testid="remote-video"], video:nth-of-type(2)` | Required |
| Mute/unmute mic button | `button[aria-label*="mute" i]` | Required |
| Camera on/off button | `button[aria-label*="camera" i], button[aria-label*="video" i]` | Required |
| Screen share button | `button[aria-label*="screen" i], button:has-text("Share Screen")` | Required |
| Leave/End call button | `button:has-text("Leave"), button:has-text("End Call")` | Required |
| Whiteboard toggle | `button:has-text("Whiteboard")` | Required |
| Whiteboard canvas | `canvas[data-testid="whiteboard"], canvas` | Required |
| Whiteboard tool palette (pen/eraser/color) | `[data-testid="wb-tools"], button[aria-label*="pen" i]` | Required |
| Whiteboard clear button | `button:has-text("Clear")` | Required |
| Chat panel toggle | `button[aria-label*="chat" i], button:has-text("Chat")` | Required |
| Chat message input | `textarea[placeholder*="message" i], input[placeholder*="message" i]` | Required |
| Chat send button | `button:has-text("Send")` | Required |
| Session timer/countdown | `:text("remaining"), [data-testid="session-timer"]` | Required |
| Connection quality indicator | `[data-testid="connection-quality"], :text("Reconnecting")` | Optional |

## User Flows

### Flow 1: Join and Establish Dual Video
1. As Tutor, join a scheduled classroom (see `session.md` Flow 1)
2. As Student (separate browser/session), join the same classroom
→ Expected: Both participants see their own local video tile and the other participant's remote video tile within a few seconds

### Flow 2: Mute/Unmute Audio
1. Inside the classroom, click the mic mute button
2. Click again to unmute
→ Expected: Icon state toggles; the remote participant's UI reflects the mute state (e.g. a muted icon over the peer's tile)

### Flow 3: Screen Share
1. Click "Share Screen"
2. Select a window/tab in the browser's native picker
→ Expected: Remote participant's video tile switches to show the shared screen content; a "Stop Sharing" control appears for the sharer

### Flow 4: Collaborative Whiteboard Drawing and Sync
1. Tutor opens the Whiteboard
2. Tutor draws a shape/line with the pen tool
→ Expected: The same drawing appears in near-real-time on the Student's whiteboard view (dual-session sync)

### Flow 5: Whiteboard Persistence Across Reconnect
1. Draw on the whiteboard
2. Refresh the browser tab / simulate a brief disconnect
3. Rejoin the same session
→ Expected: Previously drawn whiteboard content is either restored or the loss is clearly communicated — content must not desync between participants (one sees drawing, other doesn't, indefinitely)

### Flow 6: In-Session Chat
1. Open chat panel
2. Send a text message
→ Expected: Message appears in both participants' chat panels with correct sender attribution and timestamp

### Flow 7: Session Auto-Closes at End Time
1. Join a classroom
2. Wait until the scheduled end time passes
→ Expected: Session/call ends automatically for both participants with a clear "Session ended" state, no orphaned open call

## Requirements
- REQ-01: Both participants must see a live local and remote video stream once both have joined
- REQ-02: Mute state is accurately reflected on both the muting user's own UI and the peer's UI
- REQ-03: Screen share replaces the sharer's camera feed on the peer's view and is clearly labeled as a screen share
- REQ-04: Whiteboard drawings sync between participants with acceptable latency (document actual observed latency; flag if it consistently exceeds a few seconds)
- REQ-05: Whiteboard "Clear" affects both participants' views, not just the clicker's
- REQ-06: Chat messages are delivered to the peer and are never lost silently
- REQ-07: Leaving/ending the call cleanly releases camera/mic device permissions (no lingering "in use" indicator after leaving)
- REQ-08: Classroom access is enforced by the underlying booking — a user who never booked this session must not be able to join by guessing the session URL/ID (IDOR/BOLA check)
- REQ-09: Chat message input must escape/sanitize HTML so a message containing a script tag renders as plain text to the recipient, not executable script (XSS check)
- REQ-10: Session must auto-terminate at the scheduled end time for both participants

## Edge Cases
| EC-01 | One participant has camera permission denied by the browser | Clear "camera access denied" messaging shown, call still proceeds audio-only if possible |
| EC-02 | One participant loses network mid-call and reconnects within a short window | Call resumes, video/audio recover, no permanent black screen |
| EC-03 | Screen share started, then the shared window/tab is closed by the OS | Screen share ends gracefully, falls back to camera view or shows sharer's "stopped sharing" state |
| EC-04 | Whiteboard pen tool used with rapid continuous strokes | No dropped segments, no runaway memory growth, no crash |
| EC-05 | Chat message containing an XSS payload (`<script>alert(1)</script>`) | Rendered as literal text in both chat panels, no script execution |
| EC-06 | Chat message that is extremely long (5000+ chars) | Either capped with a max-length limit or wraps/scrolls without breaking layout |
| EC-07 | Attempting to join a session URL/ID for a booking that isn't the current user's | Access denied — no video/audio/whiteboard content leaks to the unauthorized user |
| EC-08 | Both participants draw on the whiteboard simultaneously in the same area | Last-write-wins or merge behavior is consistent — no visual desync between the two views |
| EC-09 | Joining a few minutes early (before scheduled start) vs. a few minutes late | Early join shows an appropriate waiting state; late join still connects successfully if within the session window |
| EC-10 | Mic muted, then attempting to speak | Peer receives no audio while muted (verify local mute actually mutes outgoing audio, not only the UI icon) |

## Test Data
### Valid
| Field | Value |
|---|---|
| name | Automations Tutor |
| name | Automations Student |
| name | Hello, can you see my screen? |

### Invalid
| Field | Value |
|---|---|
| name | <script>alert(1)</script> |
| name | <img src=x onerror=alert(1)> |
