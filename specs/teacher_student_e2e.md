# Page: Teacher–Student Full E2E Workflow

**URL:** `https://dev.mehadedu.com/en`

## Description
End-to-end business cycle verification. A teacher (tutor) creates an account, sets up a group session and 1-to-1 availability. A student discovers the session, enrolls/books, completes payment. Both accounts must reflect the same real data — nothing is simulated. This spec verifies that data written by one account is immediately visible to the other account, confirming real database persistence.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Become a Tutor link | `a[href="/en/become-tutor"], a:has-text("Become a Tutor")` | Teacher signup entry |
| Apply Now button | `a:has-text("Apply Now"), button:has-text("Apply Now")` | Required |
| Teacher Login heading | `h1:has-text("Teacher Login"), h2:has-text("Teacher Login")` | Required |
| Login button (header) | `button:has-text("Log In"):not([aria-label])` | Student login entry |
| Login dialog | `[role="dialog"]` | Required |
| Country code button | `button[aria-label="Country code"], button:has-text("Country code")` | Required |
| Country search | `[role="listbox"] input[placeholder*="Search"]` | Required |
| Bangladesh option | `[role="option"]:has-text("Bangladesh")` | Required |
| Phone input | `input[type="tel"]` | Required |
| Send Code button | `button:has-text("Send Code")` | Required |
| OTP input | `input[placeholder="000000"]` | Required |
| Continue button | `button:has-text("Continue")` | Required |
| First name input | `input[name="firstName"], input[placeholder*="First"]` | Tutor signup |
| Last name input | `input[name="lastName"], input[placeholder*="Last"]` | Tutor signup |
| Email input | `input[type="email"]` | Tutor signup |
| Bio textarea | `textarea[name="bio"], textarea[placeholder*="bio"]` | Tutor signup |
| Next button | `button:has-text("Next")` | Multi-step form |
| Submit Application button | `button:has-text("Submit Application")` | Tutor signup |
| Create Group Session button | `button:has-text("Create Group Session"), button:has-text("New Group Session")` | Teacher dashboard |
| Session title input | `input[name="title"], input[placeholder*="title"]` | Group session form |
| Session date picker | `input[type="date"], [aria-label*="date"]` | Group session form |
| Session time picker | `input[type="time"], [aria-label*="time"]` | Group session form |
| Course/Subject select | `select[name="subject"], [placeholder*="subject"], [placeholder*="course"]` | Group session form |
| Max students input | `input[name="maxStudents"], input[placeholder*="max"]` | Group session form |
| Session price input | `input[name="price"], input[placeholder*="price"]` | Group session form |
| Publish Session button | `button:has-text("Publish"), button:has-text("Create Session"), button:has-text("Save")` | Group session |
| Availability calendar | `.calendar, [data-testid="availability-calendar"]` | 1-to-1 setup |
| Add slot button | `button:has-text("Add Slot"), button:has-text("Add Availability")` | 1-to-1 setup |
| Find Tutors button | `button:has-text("Find Tutors"), nav button:has-text("Find Tutors")` | Student nav |
| Group Session option | `[role="menuitem"]:has-text("Group Session"), a:has-text("Group Session")` | Student nav |
| Enroll Now button | `button:has-text("Enroll Now")` | Student — group session |
| Book Trial Lesson button | `button:has-text("Book Trial Lesson")` | Student — 1-to-1 |
| Payment card input | `input[name="cardNumber"], input[placeholder*="card number"]` | Payment |
| Card expiry input | `input[name="expiry"], input[placeholder*="MM/YY"]` | Payment |
| CVV input | `input[name="cvv"], input[placeholder*="CVV"]` | Payment |
| Confirm and Pay button | `button:has-text("Confirm & Pay"), button:has-text("Pay Now")` | Payment |
| My Bookings link | `a[href*="bookings"], a:has-text("My Bookings")` | Student dashboard |
| Enrolled Students list | `[data-testid="enrolled-students"], .enrolled-students` | Teacher dashboard |
| Earnings Pending Balance | `:has-text("Pending Balance"), [data-testid="pending-balance"]` | Teacher earnings |
| Join Classroom button | `button:has-text("Join"), a:has-text("Join Classroom")` | Both accounts |
| Recording link | `a:has-text("Recording"), button:has-text("View Recording")` | Post-session |

## User Flows

### Flow 1: Teacher Signup with Real Phone Number
1. Navigate to https://dev.mehadedu.com/en/become-tutor
2. Click "Apply Now"
3. Redirects to /en/tutor-login — shows "Teacher Login" heading
4. Click country code button
5. Search for "Bangladesh" and select "+880"
6. Enter teacher phone number (TEACHER_PHONE env var: 98976564)
7. Click "Send Code"
8. Enter OTP (TEACHER_OTP env var: 123456)
9. Click "Continue"
10. Tutor signup form appears
11. Fill First Name: TestTeacher
12. Fill Last Name: Fagun
13. Fill Email: testteacher@mehadedu.com
14. Fill Bio: Experienced math teacher with 5 years of online teaching
15. Select Language: English
16. Click "Next" (step 2: education)
17. Fill Highest Degree: B.Sc.
18. Fill University: Test University
19. Fill Graduation Year: 2020
20. Click "Next" (step 3: subjects)
21. Select Subject: Math
22. Set Hourly Rate: 50
23. Fill Subject Description: Expert in algebra and calculus
24. Select Experience: 3 years
25. Select Teaching Level: High School
26. Click "Next" (review step)
27. Click "Submit Application"
→ Expected: Application submitted. Teacher logs in with same phone 98976564 on next visit.

### Flow 2: Teacher Creates Group Session
1. Log in as teacher (phone: 98976564, OTP: 123456)
2. Navigate to teacher dashboard
3. Click "Create Group Session" or "New Group Session"
4. Step 1 — Session details:
   - Title: Math Group Session — Algebra Basics
   - Subject: Math
   - Level: High School
   - Max Students: 10
   - Price: 25
5. Step 2 — Date and time:
   - Date: next available date
   - Start Time: 10:00 AM
   - Duration: 60 minutes
6. Step 3 — Review and publish:
   - Verify all details shown
   - Click "Publish" or "Create Session"
→ Expected: Session appears in teacher's session list AND on /en/find-tutors for students

### Flow 3: Teacher Sets 1-to-1 Availability
1. Log in as teacher (phone: 98976564, OTP: 123456)
2. Navigate to /en/dashboard/availability
3. Click on available time slots in the calendar
4. Select Monday 09:00–10:00 AM
5. Select Monday 11:00 AM–12:00 PM
6. Click "Save" or confirm availability
→ Expected: Slots saved and visible to students on teacher's booking page

### Flow 4: Student Signup with Real Phone Number
1. Navigate to https://dev.mehadedu.com/en
2. Click "Log In" button in header
3. Dialog opens
4. Click country code button
5. Search "Bangladesh" and select "+880"
6. Enter student phone number (STUDENT_PHONE env var: 98765432)
7. Click "Send Code"
8. Enter OTP: 123456
9. Click "Continue"
10. Student dashboard opens
→ Expected: New student account created. Login with same phone 98765432 on next visit.

### Flow 5: Student Finds and Enrolls in Group Session
1. Log in as student (phone: 98765432, OTP: 123456)
2. Click "Find Tutors" in header
3. Click "Group Session" from dropdown
4. Group session listing page opens at /en/find-tutors (group mode)
5. Teacher's "Math Group Session" is visible in the list
6. Click "Enroll Now" on the session
7. Group booking modal opens showing session details
8. Verify: session title, date, time, price displayed
9. Click "Continue"
10. Payment form opens
11. Enter card: 4111 1111 1111 1111
12. Enter expiry: 05/28
13. Enter CVV: 100
14. Click "Confirm & Pay"
→ Expected: Payment success. Session appears in student's My Bookings. Teacher's dashboard shows +1 enrolled student.

### Flow 6: Student Books 1-to-1 Trial Lesson
1. Log in as student (phone: 98765432, OTP: 123456)
2. Click "Find Tutors" → "1 to 1 session"
3. Find teacher "TestTeacher Fagun" in the list
4. Click "Book Trial Lesson"
5. Teacher's profile opens with availability calendar
6. Click available slot (Monday 09:00–10:00 AM)
7. Click "Continue"
8. Payment form opens (trial may be free or paid)
9. Click "Confirm & Pay"
→ Expected: Booking confirmed. Appears in student's My Bookings. Teacher sees new booking.

### Flow 7: Verify Cross-Account Data (Teacher sees Student)
1. Log in as teacher (phone: 98976564, OTP: 123456)
2. Navigate to group session that student enrolled in
3. View "Enrolled Students" section
4. Student account (phone: 98765432) is listed
5. Student name and enrollment date visible
6. Navigate to teacher calendar/bookings
7. 1-to-1 booking from student is visible with student's name
→ Expected: All student data visible in teacher account — real database confirmation

### Flow 8: Verify Cross-Account Data (Student sees Teacher)
1. Log in as student (phone: 98765432, OTP: 123456)
2. Navigate to My Bookings
3. Group session booking shows teacher name "TestTeacher Fagun"
4. 1-to-1 booking shows teacher name and confirmed slot
5. Navigate to booked group session detail
6. Teacher's profile information (name, bio, subjects) is visible
→ Expected: Teacher data visible in student account — real database confirmation

### Flow 9: Join Classroom and Session
1. Log in as teacher at session time
2. Navigate to upcoming session
3. Click "Join" or "Start Classroom"
4. Classroom/video tool opens
5. In parallel: student logs in and clicks "Join" on same session
6. Both teacher and student are in classroom
→ Expected: Both parties can join the classroom link

### Flow 10: Teacher Earnings After Paid Session
1. Log in as teacher (phone: 98976564, OTP: 123456)
2. Navigate to /en/dashboard/earnings
3. Paid session amount visible under "Pending Balance"
4. Transaction history shows the student's payment
→ Expected: Earnings reflect the real payment — same amount student paid

### Flow 11: Student Views Recording After Session
1. Log in as student (phone: 98765432, OTP: 123456)
2. Navigate to My Bookings → completed sessions
3. Completed session shows "View Recording" link
4. Recording opens and is playable
→ Expected: Recording available post-session

## Requirements
- REQ-01: Teacher phone used for signup must be the same phone used for subsequent logins
- REQ-02: Student phone used for signup must be the same phone used for subsequent logins
- REQ-03: Group session created by teacher appears on student-facing /en/find-tutors page
- REQ-04: Student enrollment is visible in teacher's enrolled students list
- REQ-05: Booking created by student appears in teacher's calendar/bookings
- REQ-06: Teacher profile info (name, bio, subjects, rate) displays correctly on student-facing tutor card
- REQ-07: Payment of 25 SAR for group session reflects in teacher's pending balance
- REQ-08: 1-to-1 availability slots set by teacher are shown on teacher's booking calendar
- REQ-09: Both teacher and student can join the classroom using the same session link
- REQ-10: Completed session creates a recording accessible to the student
- REQ-11: Student's My Bookings list matches teacher's bookings list (same session IDs)
- REQ-12: Cancellation by teacher returns hours/credits to student
- REQ-13: Student cancellation within 12 hours receives full refund

## Edge Cases
| EC-01 | Teacher uses same phone to sign up twice | System shows existing account, does not duplicate |
| EC-02 | Student tries to enroll in fully booked session | Enroll button disabled, capacity message shown |
| EC-03 | Student enrolls same group session twice | System prevents duplicate enrollment |
| EC-04 | Payment fails (invalid card) | Error shown, booking not created |
| EC-05 | Teacher cancels session after student enrolled | Student gets refund / hours back |
| EC-06 | Student cancels within 12 hours | Full refund or hours credited back |
| EC-07 | Student cancels after 12-hour window | No refund per cancellation policy |
| EC-08 | Teacher has no availability set | Book Trial Lesson button disabled or shows no slots |
| EC-09 | Both teacher and student log in with same phone | System should detect same account type conflict |
| EC-10 | Session data mismatch between teacher and student view | Both show identical session details |

## Test Data
### Valid
| Field | Value |
|---|---|
| teacher_phone | 98976564 |
| teacher_otp | 123456 |
| teacher_country | +880 |
| student_phone | 98765432 |
| student_otp | 123456 |
| student_country | +880 |
| teacher_first_name | TestTeacher |
| teacher_last_name | Fagun |
| teacher_email | testteacher@mehadedu.com |
| teacher_bio | Experienced math teacher with 5 years of online teaching |
| session_title | Math Group Session — Algebra Basics |
| session_price | 25 |
| session_max_students | 10 |
| card_number | 4111 1111 1111 1111 |
| card_expiry | 05/28 |
| card_cvv | 100 |

### Invalid
| Field | Value |
|---|---|
| card_number | 0000 0000 0000 0000 |
| card_expiry | 01/20 |
| teacher_bio | (over 500 characters) |
| session_price | -1 |
