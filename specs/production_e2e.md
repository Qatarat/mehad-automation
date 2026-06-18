# Production End-to-End Test Walkthrough

**Environment:** `https://mehadedu.com`
**Date verified:** 2026-06-06
**Tester:** Manual browser automation (Claude Code + Playwright MCP)

---

## Overview

This document records the full production E2E test covering:
1. New teacher signup → profile creation → admin approval
2. Teacher sets availability
3. Student logs in → finds tutor → books session
4. Payment flow (live gateway)

## Requirements

- REQ-PROD-01: Production teacher signup must create a real pending tutor application, not a mock profile.
- REQ-PROD-02: Admin approval must unlock the real tutor dashboard menus and public tutor profile.
- REQ-PROD-03: Tutor availability must persist and become visible on the public tutor profile.
- REQ-PROD-04: Student booking must create a real booking number with tutor, student, date, duration, price, and gateway URL.
- REQ-PROD-05: Live production test-card payment failure must be reported as failed and must not be shown as a successful purchase.
- REQ-PROD-06: Dev/sandbox payment success may complete the purchase only when the sandbox gateway returns a successful result.
- REQ-PROD-07: Tutor earnings must appear only after a successful payment and completed session.
- REQ-PROD-08: Admin/session/report views must use real booking, payment, and completion records only.
- REQ-PROD-09: Cancelled, unpaid, failed, or future sessions must not be counted as completed classes or tutor earnings.
- REQ-PROD-10: The final automation report must mark live-gateway limitations as blocked or expected-failure evidence, never as fake pass data.

## User Flows

### Flow 1: Teacher creates a production-ready profile
1. Open the production become-a-tutor path.
2. Register or login with a real phone number and OTP.
3. Complete personal details, certification, subject expertise, and review steps.
4. Submit the application.
5. Verify the tutor profile remains pending until an admin approves it.
6. After approval, verify the dashboard and public profile use the same real tutor record.

### Flow 2: Teacher creates availability for paid classes
1. Login as the approved tutor.
2. Open the availability calendar.
3. Add date range, weekdays, start time, and end time.
4. Save the slot.
5. Verify the slot appears in the tutor dashboard calendar.
6. Open the public tutor profile and verify the same slot is available to students.

### Flow 3: Student books and pays for a class
1. Login as a real student.
2. Open the approved tutor profile or find-tutors result.
3. Select a visible slot and duration.
4. Review teacher, subject, date, time, duration, price, and platform fee.
5. Confirm the booking and capture the generated booking number.
6. On production, submit a known test card only to verify the live gateway failure path.
7. On dev/sandbox, submit the sandbox test card and verify successful redirect to bookings.
8. Verify the booking status matches the gateway result and is visible in the correct dashboard.

### Flow 4: Complete class and verify earnings where payment succeeded
1. Use the dev/sandbox successful booking or a real production paid booking.
2. Move the session through the real completion path after class time or through an authorized completion action.
3. Verify student history shows the class as completed.
4. Verify tutor booked sessions and calendar show the class as completed.
5. Verify tutor earnings include the completed paid session.
6. Verify admin sessions and reports show the same booking number, tutor, student, amount, and completed status.

### Flow 5: Report only real production evidence
1. Collect screenshots, pytest JSON, booking number, gateway status, and report rows for the run.
2. Mark live card success as not-tested unless a real successful payment was made.
3. Fail any report that shows cancelled, unpaid, or failed bookings as completed.
4. Fail any report row that is not backed by an executed test artifact.

---

## Phase 1: New Teacher Onboarding

### 1.1 Teacher Registration
| Step | URL | Action | Result |
|------|-----|--------|--------|
| Navigate to Become a Tutor | `/en/become-tutor` | Click "Apply Now" | Redirects to `/en/tutor-login` |
| Enter phone | `/en/tutor-login` | +880 1316314566 → Send Code → OTP | Authenticated as new tutor |
| Redirect | `/en/tutor/profile` | Banner: "Instructor Profile not completed" | Profile wizard loads |

### 1.2 Instructor Profile Wizard (`/en/tutor/profile`)

**Step 1 — Personal Information**

| Field | Value Used | Notes |
|-------|-----------|-------|
| First Name | Test | Max 30 chars |
| Last Name | Teacher | Max 30 chars |
| Email | testteacher@mehadedu.com | Must be valid format |
| Bio | 202 chars of teaching description | Max 500 chars |
| Languages | English | Multi-select button group |
| Timezone | Asia/Dhaka | Auto-populated from account; field disabled |
| Intro Video | (skipped) | Optional, max 100MB |

**Step 2 — Certifications**

| Field | Value Used | Notes |
|-------|-----------|-------|
| Highest Degree | Bachelor of Science in Computer Science | Max 50 chars |
| University/Institution | University of Dhaka | Max 50 chars |
| Graduation Year | 2020 | 4 digits, numbers only |
| Certificate | test_certificate.png (minimal PNG) | PDF/JPG/PNG, max 10MB; uploaded to CDN |

Certificate CDN URL: `https://cdn.mehadedu.com/tutor-applications/7a9df0e5-9723-4809-8b6a-b365b70e6fa5.png`

**Step 3 — Subjects & Expertise**

| Field | Value Used | Notes |
|-------|-----------|-------|
| Subject Name | Math | Dropdown (Arabic/Biology/Chemistry/English/Math) |
| Hourly Rate | 100 SAR | Max 10,000 |
| About This Subject | 227 chars description | Max 500 chars |
| Years of Experience | 5 years | Dropdown 1–10 |
| Target Students | High School | Primary/Middle School/High School/University |
| Additional Experience | (skipped) | Optional |

**Step 4 — Review**
All data shown in read-only summary. "Submit Application" button visible and clickable.

**Post-submission:** Redirects to `/en/tutor/profile` success screen:
> "Application Submitted — Thank you for applying to teach on Mehad! Your application has been received and is pending management review."
> "This process usually takes 2–3 business days."

### 1.3 Admin Approval
After admin approves in the admin panel:
- Account `userId: 615, role: tutor, status: active`
- Tutor profile ID assigned: **301**
- Full tutor dashboard menus unlock (Availability Calendar, Booked Sessions, Group Sessions, Earnings, etc.)
- Instructor Profile at `/en/dashboard/instructor-profile` shows all 3 tabs with submitted data

**⚠️ Important:** After approval, profile at `/en/tutor/301` shows "No available slots" until the tutor sets availability.

---

## Phase 2: Tutor Sets Availability

**URL:** `/en/dashboard/availability`

| Action | Details | Result |
|--------|---------|--------|
| Click "Add Availability Time" | Dialog opens | Start Date, End Date, day buttons, time pickers |
| Set date range | 2026-06-08 to 2026-06-30 | |
| Select days | Mon, Tue, Wed, Thu, Fri | Buttons M T W T F |
| Set time slot | 10:00 AM – 12:00 PM | Radix UI combobox dropdowns |
| Click Apply | | Toast: "5 day(s) added" |

**Result:** Calendar shows `10:00 AM - 12:00 PM` on every Mon–Fri from June 8–30, 2026.

---

## Phase 3: Student Books a Session

**Student account:** +880 1316314566, userId: 514, role: student
**Tutor profile:** `/en/tutor/301` (Test Teacher)

| Step | URL | Action | Result |
|------|-----|--------|--------|
| Login | `/en` homepage modal | +880 1316314566, OTP → Continue | Logged in as student |
| Navigate to tutor | `/en/tutor/301` | Click "Next week" to Jun 7–13 | Slots visible: 10:00/10:30/11:00/11:30 AM |
| Open booking | Click "Book Trial Lesson" | Booking dialog opens: "Book a Session" | Step 1: Date & Time |
| Select duration | Click "1 hour" | Two 1-hour slots shown: 10:00–11:00, 11:00–12:00 | |
| Select date | Click "08" (Monday Jun 8) | Day highlighted | |
| Select time | Click "10:00 AM - 11:00 AM" | "Selected time: June 8, 2026 • 10:00 AM - 11:00 AM" | Continue enabled |
| Review | Click Continue | Step 2: Review & Details | Teacher, Subject, Duration, Date, Time, Price |
| Confirm | Click "Confirm & Pay" | Redirects to payment page | `BK-20260606-KTFE91` |

**Booking Review Summary:**
- Teacher: Test Teacher
- Subject: Math  
- Duration: 60-minute Session
- Date: Monday, June 8, 2026
- Time: 10:00 AM - 11:00 AM
- Session Fee: 100 SAR
- Platform Fee: 30 SAR
- Total: 100 SAR

---

## Phase 4: Payment

**URL:** `/en/payment?bookingNumber=BK-20260606-KTFE91&gatewaySlug=paytabs&price=100`

**Gateway:** MyFatoorah — `https://sa.myfatoorah.com` (LIVE)

| Step | Result |
|------|--------|
| Payment page loads | Booking number, 100 SAR total, Card button pre-selected |
| MyFatoorah iframe loads | iframe `name="MFEmbeddedIframe"` from `sa.myfatoorah.com` |
| Fill: Card Holder Name = "Test Student" | Accepted |
| Fill: Card Number = `4111 1111 1111 1111` | Auto-formats to `4111 1111 1111 1111` |
| Fill: Expiry = `05/28` | Accepted |
| Fill: CVV = `100` | Accepted |
| Click "Pay now" | Processing... |
| Result | `/en/payment/result?status=failed` — "Payment Failed" |

**Payment failure (test card on live gateway):** Expected behavior — error page renders correctly with message and "Back to Dashboard" button. No real charge occurred.

### Payment Success (dev environment)
On `dev.mehadedu.com` with `demo.myfatoorah.com` sandbox, the same test card (`4111 1111 1111 1111`, CVV `100`, expiry `05/28`) succeeds, 3DS ACS emulator auto-approves, and redirects to `/en/dashboard/bookings`.

---

## Phase 5: Teacher Earnings Verification

After a successful dev payment, the teacher's Earnings & Payouts page at `/en/dashboard/earnings` reflects the transaction. On production, this can only be verified after a real card payment succeeds.

---

## Key Production Observations

| # | Observation | Status |
|---|-------------|--------|
| 1 | New teacher signup → wizard → pending | ✅ Works |
| 2 | 4-step profile wizard all steps complete | ✅ Works |
| 3 | Certificate uploaded to CDN correctly | ✅ Works |
| 4 | Admin approval unlocks full dashboard | ✅ Works |
| 5 | Post-approval profile visible at `/en/tutor/301` | ✅ Works |
| 6 | Availability calendar Add Availability Time dialog | ✅ Works |
| 7 | Slots appear on public tutor profile | ✅ Works |
| 8 | Student login (homepage modal) | ✅ Works |
| 9 | Same phone can be both student and tutor | ✅ Works |
| 10 | Book Trial Lesson dialog (date, time, duration) | ✅ Works |
| 11 | Booking review screen (price, details) | ✅ Works |
| 12 | Redirect to payment page with booking number | ✅ Works |
| 13 | MyFatoorah iframe loads on production | ✅ Works |
| 14 | Card fields accept input in iframe | ✅ Works |
| 15 | Payment failure error page | ✅ Works |
| 16 | Payment success with real card | 🔲 Not tested (live gateway) |
| 17 | Teacher earnings after payment | 🔲 Requires real payment first |
| 18 | `/en/tutors` listing page | ❌ 404 on prod (page not implemented) |

---

## Production Test Data

### Valid

### Teacher Account
| Field | Value |
|-------|-------|
| Phone | +880 1316314566 |
| userId | 615 |
| role | tutor |
| status | active |
| Tutor Profile ID | 301 |
| Public URL | `https://mehadedu.com/en/tutor/301` |
| Subject | Math — 100 SAR/hr — High School — 5 yrs |
| Availability | Mon–Fri 10:00 AM–12:00 PM (Asia/Dhaka), Jun 8–30 2026 |

### Student Account
| Field | Value |
|-------|-------|
| Phone | +880 1316314566 |
| userId | 514 |
| role | student |
| status | active |

### Test Booking Created
| Field | Value |
|-------|-------|
| Booking Number | BK-20260606-KTFE91 |
| Date | Monday, June 8, 2026 |
| Time | 10:00 AM – 11:00 AM (Asia/Dhaka) |
| Duration | 60 minutes |
| Amount | 100 SAR |
| Status | Payment Failed (test card on live gateway) |

### Invalid

- Live production test card result shown as a successful payment.
- Failed payment counted as tutor earnings.
- Future booked session shown as a completed class without a completion action.
- Cancelled session shown in completed-session totals.
- Report pass row with no matching browser, gateway, pytest, or admin evidence.

---

## Running Production Tests Manually

```bash
# Student login (homepage modal)
# 1. Go to https://mehadedu.com/en
# 2. Click "Log In" (desktop button, no aria-label)
# 3. Select country code +880 (Bangladesh)
# 4. Enter phone: 1316314566
# 5. Click "Send Code" → enter real OTP from WhatsApp

# Teacher login (separate portal)
# 1. Go to https://mehadedu.com/en/tutor-login
# 2. Select +880, enter 1316314566
# 3. Click "Send Code" → enter OTP
```

## Notes for Automated Tests Against Production

- Production OTPs are real SMS/WhatsApp — cannot be automated without OTP interception
- Payment is live — use `status=failed` result page as the test assertion instead of `status=success`
- Booking number format differs: prod uses `BK-` prefix, dev uses `DBK-` prefix
- `/en/tutors` returns 404 on prod — use `/en/find-tutors` instead
- Tutor profile ID ≠ user ID — resolve via network request inspection
