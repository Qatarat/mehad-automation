# Page: Sign Up
**URL:** `https://beta-stg.markopolo.ai/signup`
**Type:** Authentication — New User Registration
**Priority:** P0 — Critical path, primary user acquisition entry point

---

## Page Purpose

Allows new users to create a Markopolo account. This is the primary registration funnel. Any friction or failure here directly impacts user acquisition and activation metrics.

---

## UI Elements

| Element | Identifier Hint | Type | Required |
|---|---|---|---|
| Full Name input | `name`, `fullName` | Text input | Yes |
| Email input | `email`, `type="email"` | Text input | Yes |
| Password input | `password`, `type="password"` | Text input | Yes |
| Confirm Password input | `confirmPassword`, `type="password"` | Text input | Yes (if present) |
| Company / Organization input | `company`, `organization` | Text input | Conditional |
| Phone number input | `phone`, `tel` | Text/Tel input | Conditional |
| Password strength indicator | Visual strength meter | Display | No |
| Show/Hide password toggle | Eye icon on password field | Toggle | No |
| Password requirements list | Inline hints | Display | Recommended |
| Terms & Conditions checkbox | `terms`, links to T&C | Checkbox | Yes |
| Privacy Policy link | Opens T&C / Privacy page | Link | Yes |
| Sign Up / Create Account button | Primary CTA | Submit | Yes |
| Already have account? Log In link | Text link → `/login` | Navigation | Yes |
| Social Sign-Up button (Google) | OAuth button | Button | Conditional |
| Email verification notice | Post-submit message | Display | Conditional |
| Error message container | Inline or toast | Display | Conditional |

---

## Requirements

- REQ-S-01: All required fields must be filled before form submission is allowed.
- REQ-S-02: Email must be in valid format and must be unique (not already registered).
- REQ-S-03: Password must meet the platform's password policy.
- REQ-S-04: Confirm Password must match Password field.
- REQ-S-05: User must accept Terms & Conditions to complete registration.
- REQ-S-06: Duplicate email addresses must be rejected with a clear, actionable error.
- REQ-S-07: Upon successful registration, a verification email must be sent.
- REQ-S-08: Unverified users must see instructions to check their inbox.
- REQ-S-09: Successful signup must create a new user record in the system.
- REQ-S-10: No auto-login on signup — user must verify email first (or document if auto-login occurs).
- REQ-S-11: All form submissions must occur over HTTPS.
- REQ-S-12: Rate limiting must prevent automated mass registration attempts.
- REQ-S-13: The page must be accessible on mobile viewports (375px+).

---

## User Flows

### Flow 1: Successful Registration
```
1. User navigates to https://beta-stg.markopolo.ai/signup
2. Page loads with registration form
3. User enters full name
4. User enters a unique, valid email address
5. User enters a password meeting the policy requirements
6. User re-enters the same password in Confirm Password
7. User enters company name (if required)
8. User checks the Terms & Conditions checkbox
9. User clicks "Sign Up" / "Create Account"
10. Client-side validation passes
11. Form is submitted to the server
12. Server creates new user account
13. Server sends verification email to the provided address
14. User sees success screen: "Account created! Check your inbox to verify your email."
15. (Optional) User is auto-redirected to /login or an onboarding page
```

### Flow 2: Duplicate Email Registration
```
1. User navigates to /signup
2. User fills in all fields with a valid email that is already registered
3. User submits the form
4. Server detects duplicate email
5. Error displayed: "An account with this email already exists"
6. Link to /login or /reset-pass is shown in the error message
7. User remains on /signup page
```

### Flow 3: Client-side Validation Failure
```
1. User navigates to /signup
2. User clicks Sign Up without filling required fields
3. Client-side validation triggers immediately
4. Each empty required field is highlighted with an error indicator
5. Inline messages appear: "This field is required"
6. No server request is made
7. Focus moves to the first invalid field
```

### Flow 4: Password Mismatch
```
1. User fills all fields
2. Password and Confirm Password fields contain different values
3. On blur of Confirm field (or on submit attempt)
4. Validation error: "Passwords do not match"
5. Confirm field is highlighted
6. Form not submitted
```

### Flow 5: Password Does Not Meet Policy
```
1. User fills all fields
2. Password entered is too weak (e.g., "pass")
3. Password strength indicator shows "Weak" or "Very Weak"
4. On submit, validation blocks with message describing the policy
5. Form not submitted until password meets requirements
```

### Flow 6: Terms Not Accepted
```
1. User fills all fields correctly
2. Terms & Conditions checkbox remains unchecked
3. User clicks Sign Up
4. Validation error near checkbox: "You must accept the Terms & Conditions"
5. Form not submitted
```

### Flow 7: Navigate to Login
```
1. User is on /signup
2. User clicks "Already have an account? Log In" link
3. Browser navigates to /login
```

### Flow 8: Google / SSO Sign-Up (if present)
```
1. User clicks "Continue with Google"
2. Google OAuth popup/redirect opens
3. User selects Google account
4. Google returns auth token to Markopolo
5. System creates account with Google profile data (if new)
6. User is redirected to dashboard or onboarding
```

### Flow 9: Already Authenticated User
```
1. User has an active session
2. User navigates directly to /signup
3. System detects existing valid session
4. User is redirected to /dashboard
5. /signup page is not rendered
```

---

## Validation Rules

### Full Name Field
- Must not be empty
- Minimum 2 characters
- Maximum ~100 characters
- Should accept international characters (Unicode)
- Should not accept only spaces or special characters

### Email Field
- Must not be empty
- Must match format: `user@domain.tld`
- Whitespace trimmed before validation
- Must be unique in the system (server-side check)
- Case-insensitive comparison on server

### Password Field
- Must not be empty
- Minimum 8 characters
- Must contain at least one uppercase letter
- Must contain at least one lowercase letter
- Must contain at least one digit
- Must contain at least one special character: `!@#$%^&*()-_=+[]{}|;:',.<>?/`
- Strength indicator updates in real-time as user types

### Confirm Password Field
- Must match Password field exactly
- Validated on blur and on submit

### Company Field (if required)
- Must not be empty if marked required
- Minimum 2 characters

### Terms Checkbox
- Must be checked before form submission
- Cannot be pre-checked by default

---

## Edge Cases

| ID | Scenario | Expected Behavior |
|---|---|---|
| EC-S-01 | Name with numbers: "User123" | Accepted or rejected based on policy (document actual) |
| EC-S-02 | Name with only spaces | Rejected; trimmed value fails minimum length |
| EC-S-03 | International name: "Méjbaur Ämäl" | Accepted; Unicode characters supported |
| EC-S-04 | Email with + alias: `user+test@gmail.com` | Accepted as valid email format |
| EC-S-05 | Email with subdomain: `user@mail.company.com` | Accepted |
| EC-S-06 | Already registered email | Error with link to login/reset |
| EC-S-07 | Password = email address | Rejected if policy disallows it |
| EC-S-08 | Password = name | Rejected if policy disallows it |
| EC-S-09 | Password with only spaces | Rejected |
| EC-S-10 | Paste into password field | Should work; show/hide toggle functional |
| EC-S-11 | XSS in name: `<script>alert(1)</script>` | Sanitized; no execution |
| EC-S-12 | SQL injection in email: `' OR 1=1--@test.com` | Sanitized; rejected or fails validation |
| EC-S-13 | Rapid form submissions (double-click Submit) | Deduplicated; only one account created |
| EC-S-14 | Very long name (500+ chars) | Graceful error |
| EC-S-15 | Very long email (255+ chars) | Graceful error |
| EC-S-16 | Very long password (500+ chars) | Graceful error or accepted per policy |
| EC-S-17 | Signup on mobile (375px viewport) | Full form visible and usable |
| EC-S-18 | Registration with disposable email service | Accepted or blocked depending on policy |
| EC-S-19 | Network failure during submission | User-facing error; form data preserved |
| EC-S-20 | Browser back button after successful signup | Does not re-submit form |

---

## Expected Behaviors

### Success State
- Success message is clear and tells the user what to do next (check inbox)
- No sensitive data (password) persists in the form post-submit
- User is not automatically logged in if email verification is required
- Verification email arrives within 60 seconds

### Error States
- All errors visible without scrolling
- Each field error appears inline beside or below the relevant field
- Generic server errors are user-friendly (no stack traces exposed)
- Duplicate email error includes a clear path to recovery (login or reset)

### Loading State
- Submit button shows loading state during API call
- All inputs disabled during submission to prevent duplicates
- Resolves in ≤ 5 seconds under normal conditions

### Accessibility
- All inputs have associated `<label>` elements
- Error messages linked via `aria-describedby`
- Tab order: Name → Email → Password → Confirm Password → Company → Terms Checkbox → Sign Up → Log In link
- Password strength indicator readable by screen readers
- Form is fully keyboard-navigable
- Color is not the sole indicator of error state

---

## Test Data

### Valid Registration
```
name:             Test User QA
email:            qa_test_[timestamp]@mailinator.com   (use unique email per run)
password:         Test@1234!
confirmPassword:  Test@1234!
company:          QA Test Company
terms:            checked
```

### Duplicate Email
```
email: mejbaur@markopolo.ai   (already registered)
```

### Invalid Inputs
```
name:             (empty)
name:             " "   (spaces only)
name:             a     (single char — too short)
email:            notanemail
email:            @nodomain.com
email:            user @test.com   (space in email)
password:         123   (too short/weak)
password:         password   (no uppercase, number, special)
password:         PASSWORD1!   (no lowercase)
confirmPassword:  DifferentPass@1   (mismatch)
terms:            unchecked
```

### Injection & Security
```
name:             <script>alert('xss')</script>
email:            '; DROP TABLE users;--@test.com
password:         ' OR '1'='1
```

---

## API Contract

### Registration Submission

| Method | Endpoint | Trigger |
|---|---|---|
| POST | `/api/auth/register` or `/api/v1/users` | Form submit |

**Request Body:**
```json
{
  "name": "Test User",
  "email": "user@example.com",
  "password": "SecurePass@123",
  "confirmPassword": "SecurePass@123",
  "company": "Test Company",
  "acceptedTerms": true
}
```

**Response — Success (201):**
```json
{
  "message": "Account created. Please verify your email.",
  "userId": "abc123",
  "email": "user@example.com"
}
```

**Response — Duplicate Email (409):**
```json
{
  "error": "An account with this email already exists.",
  "action": "login"
}
```

**Response — Validation Error (422):**
```json
{
  "errors": {
    "email": "Must be a valid email address.",
    "password": "Must be at least 8 characters and include uppercase, number, and special character."
  }
}
```

**Response — Rate Limited (429):**
```json
{
  "error": "Too many registration attempts. Please try again later."
}
```

---

## Post-Registration Email

### Expected Email Content
- Subject: "Verify your email address" (or similar)
- Contains: User's name, verification link, expiry notice
- Verification link format: `https://beta-stg.markopolo.ai/verify-email?token=<token>`
- Token expiry: 24 hours (verify actual TTL)
- Contains: Link to /login, link to support

### Email Verification Flow
```
1. User receives verification email
2. User clicks verification link
3. Token is validated server-side
4. Account marked as verified
5. User redirected to /login with success message: "Email verified! You can now log in."
```

---

## Related Pages
- `/login` — For existing users; linked from signup page
- `/reset-pass` — For recovery; shown in duplicate-email error
- `/verify-email` — Post-registration token verification
- `/dashboard` / `/onboarding` — Post-login destination after verification

---

## Coverage Gaps to Investigate
- [ ] Whether email verification is required before login is allowed
- [ ] Whether auto-login occurs after signup (bypassing verification)
- [ ] Verification email re-send flow (if user doesn't receive it)
- [ ] Verification token TTL and expiry behavior
- [ ] Behavior when verification link is opened on a different device
- [ ] Whether signup is possible with Google (OAuth) and what fields are skipped
- [ ] CAPTCHA or bot protection mechanism on signup form
- [ ] Whether invite-based signup has a different flow
- [ ] Onboarding steps after first login (if any)
- [ ] Account deletion and re-registration with the same email
