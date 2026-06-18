# Spec: End-to-End Data Flow Consistency

**URL (student bookings):** `https://dev.mehadedu.com/en/dashboard/bookings`
**URL (student wallet):** `https://dev.mehadedu.com/en/dashboard/wallet`
**URL (tutor earnings):** `https://dev.mehadedu.com/en/dashboard/earnings`
**URL (tutor calendar):** `https://dev.mehadedu.com/en/dashboard/availability`
**URL (tutor booked sessions):** `https://dev.mehadedu.com/en/dashboard/booked-sessions`
**URL (admin sessions):** `https://dev.mehadedu.com/en/admin/sessions`

## Description

Validates that all transactional data (bookings, payments, sessions, earnings) flows
correctly between Student, Tutor, and Super Admin modules using real database records.
No mock or hardcoded data is permitted in any dashboard.

## Core Business Rule

Only **completed** live classes trigger:
- final earnings calculation and payout updates
- recording availability
- report and admin panel updates

## User Flows

### Flow 1: Tutor creates a real one-to-one availability slot
1. Login as an approved tutor with a completed instructor profile.
2. Open the tutor availability calendar.
3. Create a future availability slot with subject, date, start time, end time, duration, and price.
4. Verify the slot appears on the tutor calendar with status `available`.
5. Open the public tutor profile as a student-facing user.
6. Verify the same slot is visible for booking with the same tutor, subject, date, time, duration, and price.

### Flow 2: Tutor creates a real group course or class
1. Login as an approved tutor.
2. Open the course or group-session creation page.
3. Submit a course with real title, subject, description, schedule, capacity, price, and meeting duration.
4. Verify the course appears in the tutor course list with a system-generated course ID.
5. Login as a student and search for the same subject or tutor.
6. Verify the course appears in the student listing with matching tutor, schedule, capacity, and price.

### Flow 3: Student purchases a class or slot using real records
1. Login as a real student account.
2. Open the tutor profile or course listing created in the previous flow.
3. Select an available one-to-one slot or group course.
4. Confirm booking details and proceed to payment.
5. Complete payment in the dev sandbox gateway only; live production cards must not be faked.
6. Capture the booking ID, payment reference, amount, tutor name, student name, and session type.
7. Verify the booking appears in Student My Bookings, Tutor Booked Sessions, and Super Admin Sessions.

### Flow 4: Complete a class and verify post-completion data
1. Move the booked class through the real application completion path: live classroom completion, student completion action, tutor completion action, or authorized admin completion action.
2. Verify the session status becomes `Completed` in Student My Bookings history.
3. Verify the tutor calendar slot changes from `booked` to `completed`.
4. Verify tutor earnings are created only after completion.
5. Verify Super Admin Sessions shows the same booking ID with status `Completed`.
6. Verify reports include the completed session without counting cancelled or unpaid bookings as earnings.

### Flow 5: Verify reports and reject fake data
1. Open the generated automation report after the run.
2. Verify every displayed pass/fail row maps to a real executed test result artifact.
3. Verify booking IDs, payment IDs, and session IDs are preserved in the report evidence.
4. Fail the run if the report contains placeholder pass rows, fake booking IDs, mock names, or invalid screenshots.

## Data Flow Map

```
Student books slot
  → Booking ID created (consistent across modules)
  → Appears in: Student My Bookings + Tutor Booked Sessions + Admin Sessions

Student pays
  → Transaction record created
  → Appears in: Student Wallet/Payment History

Session runs live
  → Tutor calendar slot status: booked → completed
  → Recording generated and stored

Session completed
  → Recording visible in Student My Booking History
  → Earnings added to Tutor Earnings & Payouts
  → Admin Sessions updated with recording link + completed status
  → Reports module updated
```

## Module: Student Payment & Transactions (DF-01)

**URL:** `https://dev.mehadedu.com/en/dashboard/wallet`

### Requirements
- REQ-DF01-01: Wallet shows real payment records only — no placeholder rows
- REQ-DF01-02: Each transaction row has: amount, source (course/session name), tutor name, timestamp, status
- REQ-DF01-03: Transaction status values: `Paid`, `Pending`, `Failed`, `Refunded`
- REQ-DF01-04: Booking ID in transaction matches booking ID in My Bookings
- REQ-DF01-05: Empty state shown when no transactions exist (not a mock row)

### Selectors
| Element | Selector |
|---|---|
| Wallet heading | `h1:has-text("Wallet"), h2:has-text("Payment"), h2:has-text("Transactions")` |
| Transaction list | `[data-testid="transaction-list"], .transaction-list, table` |
| Transaction row | `[data-testid="transaction-row"], tr, .transaction-item` |
| Amount cell | `[data-testid="amount"], td:has-text("SAR"), .amount` |
| Source/session name | `[data-testid="source"], .transaction-source` |
| Tutor name | `[data-testid="tutor-name"], .tutor-name` |
| Timestamp | `time, [data-testid="timestamp"], .transaction-date` |
| Status badge | `[data-testid="status"], .status-badge` |
| Empty state | `:has-text("No transactions"), :has-text("No payments")` |

## Module: Student Bookings (DF-02)

**URL:** `https://dev.mehadedu.com/en/dashboard/bookings`

### Requirements
- REQ-DF02-01: Booking appears immediately after student books course or 1-to-1 session
- REQ-DF02-02: Booking card has: schedule (date + time), tutor info, type (course/session), status
- REQ-DF02-03: Booking ID is a real system-generated ID (format: DBK-YYYYMMDD-XXXXXX or BK-...)
- REQ-DF02-04: Status transitions: `Upcoming` → `Active` → `Completed` / `Cancelled`
- REQ-DF02-05: Cancelled bookings do not appear in Upcoming tab

### Selectors
| Element | Selector |
|---|---|
| Bookings heading | `h1:has-text("Booking"), h2:has-text("My Bookings")` |
| Upcoming tab | `button:has-text("Upcoming"), [data-tab="upcoming"]` |
| History tab | `button:has-text("Session History"), button:has-text("History")` |
| Booking card | `[data-testid="booking-card"], .booking-card, .session-card` |
| Booking ID | `[data-testid="booking-id"], :has-text("DBK-"), :has-text("BK-")` |
| Session type badge | `:has-text("1-to-1"), :has-text("Group"), [data-testid="session-type"]` |
| Tutor name | `[data-testid="tutor-name"], .tutor-info` |
| Schedule | `time, [data-testid="schedule"], .session-time` |
| Status | `[data-testid="status"], .status-badge` |

## Module: Session Completion & Recordings (DF-03)

**URL:** `https://dev.mehadedu.com/en/dashboard/bookings` (Session History tab)

### Requirements
- REQ-DF03-01: Completed session appears in Session History tab
- REQ-DF03-02: Recording link visible only for completed sessions (not upcoming/cancelled)
- REQ-DF03-03: Recording link resolves to a valid resource (not 404)
- REQ-DF03-04: Pending/upcoming sessions have no recording link visible

### Selectors
| Element | Selector |
|---|---|
| View Recording button | `button:has-text("View Recording"), a:has-text("View Recording")` |
| Recording link | `a[href*="recording"], [data-testid="recording-link"]` |
| Completed badge | `:has-text("Completed"), [data-testid="status"]:has-text("Completed")` |

## Module: Super Admin Sessions (DF-04)

**URL:** `https://dev.mehadedu.com/en/admin/sessions`

### Requirements
- REQ-DF04-01: All sessions (live, completed, cancelled) visible to Super Admin
- REQ-DF04-02: Each row has: student name, tutor name, session type, status, timestamps, recording link
- REQ-DF04-03: Recording link appears only for completed sessions
- REQ-DF04-04: Status filter works: Live / Completed / Cancelled
- REQ-DF04-05: Session count matches sum across all status categories

### Selectors
| Element | Selector |
|---|---|
| Sessions heading | `h1:has-text("Sessions"), h2:has-text("All Sessions")` |
| Sessions table | `table, [data-testid="sessions-table"]` |
| Student name column | `th:has-text("Student"), td[data-col="student"]` |
| Tutor name column | `th:has-text("Tutor"), td[data-col="tutor"]` |
| Status column | `th:has-text("Status"), td[data-col="status"]` |
| Recording link | `a:has-text("Recording"), [data-testid="recording-link"]` |
| Status filter | `select:has-text("Status"), [placeholder*="Status"]` |

## Module: Tutor Calendar (DF-05)

**URL:** `https://dev.mehadedu.com/en/dashboard/availability`

### Requirements
- REQ-DF05-01: All tutor-created slots visible in calendar
- REQ-DF05-02: Slot availability status: `available`, `booked`, `completed`, `cancelled`
- REQ-DF05-03: Booked slot shows student name or booking reference
- REQ-DF05-04: Past slots marked completed or show history

### Selectors
| Element | Selector |
|---|---|
| Calendar heading | `h1:has-text("Availability"), h2:has-text("Calendar")` |
| Calendar grid | `.calendar, [data-testid="calendar"], .fc-view` |
| Available slot | `.slot-available, [data-status="available"], .available` |
| Booked slot | `.slot-booked, [data-status="booked"], .booked` |
| Completed slot | `.slot-completed, [data-status="completed"]` |
| Time slot | `.time-slot, [data-testid="slot"], .fc-event` |

## Module: Tutor Booked Sessions (DF-06)

**URL:** `https://dev.mehadedu.com/en/dashboard/booked-sessions`

### Requirements
- REQ-DF06-01: Booked sessions appear immediately after student books
- REQ-DF06-02: Each row has: student details, time, session type, status
- REQ-DF06-03: Upcoming and Session History tabs both functional
- REQ-DF06-04: No mock/placeholder student names

### Selectors
| Element | Selector |
|---|---|
| All Sessions heading | `h1:has-text("Sessions"), :has-text("All Sessions")` |
| Upcoming tab | `button:has-text("Upcoming Sessions")` |
| History tab | `button:has-text("Session History")` |
| Search input | `input[placeholder="Search sessions..."]` |
| Filters button | `button:has-text("Filters")` |
| Session row | `.session-item, [data-testid="session-row"], tr` |
| Student name | `[data-testid="student-name"], .student-name` |
| Session type | `:has-text("1-to-1"), :has-text("Group")` |

## Module: Course Creation Real Data (DF-07)

**URL:** `https://dev.mehadedu.com/en/dashboard/create-course`

### Requirements
- REQ-DF07-01: Course stored with real name, description, pricing, schedule
- REQ-DF07-02: Created course appears in tutor's course list immediately
- REQ-DF07-03: Same course visible in student find-tutors/course listing
- REQ-DF07-04: Course ID consistent across tutor dashboard and student view
- REQ-DF07-05: No hardcoded course data in any UI state

## Module: Tutor Earnings & Payouts (DF-08)

**URL:** `https://dev.mehadedu.com/en/dashboard/earnings`

### Requirements
- REQ-DF08-01: Earnings page loads with Available Balance, Pending Earnings, Total Earnings
- REQ-DF08-02: Completed 1-to-1 session adds gross amount to Available Balance
- REQ-DF08-03: Completed group session: pending → available after course completes
- REQ-DF08-04: Platform fee deducted and visible (if applicable)
- REQ-DF08-05: Transaction reference in earnings matches booking ID

### Selectors
| Element | Selector |
|---|---|
| Earnings heading | `h1:has-text("Earning"), h2:has-text("Earnings")` |
| Available Balance | `:has-text("Available Balance"), [data-testid="available-balance"]` |
| Pending Earnings | `:has-text("Pending"), [data-testid="pending-earnings"]` |
| Total Earnings | `:has-text("Total"), [data-testid="total-earnings"]` |
| Payout list | `[data-testid="payout-list"], .earnings-list` |
| Transaction ref | `[data-testid="transaction-ref"], :has-text("DBK-"), :has-text("BK-")` |

## Cross-Module Consistency Rules

| ID | Rule |
|---|---|
| CC-01 | Booking ID in Student My Bookings = Booking ID in Tutor Booked Sessions = Admin Sessions |
| CC-02 | Payment amount in Student Wallet = Gross earnings in Tutor Earnings |
| CC-03 | Session status in Student Bookings = Session status in Tutor Calendar = Admin Sessions |
| CC-04 | Recording link in Student History = Recording link in Admin Sessions |
| CC-05 | Tutor name displayed in Student Bookings matches tutor's registered name |

## Mock Data Detection Rules

The following strings in any dashboard indicate mock/hardcoded data (FAIL):
- `Sample Tutor`, `Test Tutor`, `Demo Student`
- `Lorem ipsum`
- `Student Unknown`, `Instructor Unknown`, `Automation Demo`
- Static booking IDs that do not match an API/database record
- Placeholder report rows that have no pytest JSON result, screenshot, trace, or logged evidence

## Test Data

### Valid
- Tutor account: approved instructor with completed profile, subject `Math`, and real availability slot in a future date.
- Student account: active student with verified login and enough wallet/gateway access to complete a sandbox payment.
- One-to-one booking: future slot with real booking ID prefix `DBK-` or `BK-`, price, date, start time, end time, tutor ID, and student ID.
- Group course booking: real course ID, capacity greater than zero, schedule, amount, and enrolled student ID.
- Completion evidence: status `Completed`, matching booking ID across Student Bookings, Tutor Calendar, Tutor Earnings, Admin Sessions, and Reports.

### Invalid
- Cancelled booking shown as completed.
- Unpaid booking counted as tutor earnings.
- Future booked slot marked completed before the class completion action.
- Mock student or tutor names used as report evidence.
- Report pass row generated without a real test result artifact.
- `John Doe`, `Jane Doe` (unless real registered user)
- `XXX`, `TBD`, `Placeholder`
- Booking ID: `12345`, `99999`, `0000` (non-system-format IDs)
- Amount: exactly `0.00` when sessions are completed (earnings not calculated)

## Test Accounts

| Role | Phone | OTP | Country |
|---|---|---|---|
| Tutor | `98976564` | `123456` | `+880` Bangladesh |
| Student | `98765432` | `123456` | `+880` Bangladesh |

## Edge Cases

| ID | Scenario | Expected |
|---|---|---|
| EC-DF-01 | No bookings exist | Empty state shown, not mock rows |
| EC-DF-02 | Session cancelled after payment | Wallet shows refund or cancellation record |
| EC-DF-03 | Two students book same tutor slot | Second booking blocked or separate slot created |
| EC-DF-04 | Recording not yet processed | "Processing" state shown, not broken link |
| EC-DF-05 | Admin filters by student name | Sessions filtered correctly with real data |
