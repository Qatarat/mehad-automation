# Page: Reset Password
**URL:** `https://beta-stg.markopolo.ai/reset-pass`
**Type:** Authentication — Account Recovery
**Priority:** P1 — High, required for locked-out user recovery

---

## Page Purpose

Allows users who have forgotten their password to request a reset link via email. This is a two-stage flow: (1) request email, (2) set new password via link. This MD covers both stages.

---

## Stage Overview

```
Stage 1: /reset-pass          → User submits email → System sends reset email
Stage 2: /reset-pass?token=X  → User sets new password → Account updated → Redirected to /login
```

---

## UI Elements — Stage 1 (Request Reset)

| Element | Identifier Hint | Type | Required |
|---|---|---|---|
| Page heading | "Reset Password" / "Forgot Password" | Text | Yes |
| Description text | Instructional copy explaining the process | Text | Yes |
| Email input | `email`, `type="email"` | Text input | Yes |
| Submit / Send Reset Link button | Primary CTA | Submit | Yes |
| Back to Login link | Text link → `/login` | Navigation | Yes |
| Success message container | Appears after submission | Display | Conditional |
| Error message container | Appears on failure | Display | Conditional |

---

## UI Elements — Stage 2 (Set New Password)

| Element | Identifier Hint | Type | Required |
|---|---|---|---|
| Page heading | "Set New Password" / "Create New Password" | Text | Yes |
| New password input | `password`, `type="password"` | Text input | Yes |
| Confirm password input | `confirmPassword`, `type="password"` | Text input | Yes |
| Password strength indicator | Visual strength meter | Display | No |
| Show/Hide password toggle | Eye icon on each password field | Toggle | No |
| Password requirements list | Inline hints (length, special chars, etc.) | Display | No |
| Submit / Reset Password button | Primary CTA | Submit | Yes |
| Back to Login link | Text link → `/login` | Navigation | Yes |
| Expired/invalid token message | Shown when token is bad | Display | Conditional |

---

## Requirements

### Stage 1 — Request
- REQ-R-01: User must provide a valid email format to submit the form.
- REQ-R-02: Regardless of whether the email exists in the system, the success message must be identical (prevents email enumeration).
- REQ-R-03: System must send a password reset email to verified accounts within 60 seconds.
- REQ-R-04: Reset link in email must be single-use and expire after a defined TTL (typically 15–60 minutes).
- REQ-R-05: Multiple reset requests for the same email must invalidate previous tokens.
- REQ-R-06: Rate limiting must prevent spam reset requests from a single IP or email.

### Stage 2 — Set New Password
- REQ-R-07: Token in the URL must be validated server-side before rendering the set-password form.
- REQ-R-08: Expired or already-used tokens must display a clear error with a link to request a new reset.
- REQ-R-09: New password must meet the platform's password policy (minimum length, complexity).
- REQ-R-10: Confirm password must match new password before submission is allowed.
- REQ-R-11: On successful password reset, all existing sessions for that account must be invalidated.
- REQ-R-12: After successful reset, user must be redirected to `/login` with a success confirmation.
- REQ-R-13: The reset token must not be logged in server-side access logs.

---

## User Flows

### Flow 1: Successful Password Reset (Full Journey)
```
1. User navigates to /reset-pass
2. User enters registered email address
3. User clicks "Send Reset Link"
4. System validates email format
5. System looks up email (silently, result not exposed)
6. System sends reset email to registered address
7. Success message displayed: "Check your inbox — we've sent a reset link"
8. User opens email, clicks reset link (contains token)
9. Browser opens /reset-pass?token=<token>
10. System validates token (not expired, not used)
11. Stage 2 form appears: New Password + Confirm Password
12. User enters new password matching policy
13. User re-enters same password in confirm field
14. User clicks "Reset Password"
15. System updates password, invalidates token, invalidates sessions
16. Success message shown briefly
17. User redirected to /login
18. User logs in with new password successfully
```

### Flow 2: Email Not Registered
```
1. User navigates to /reset-pass
2. User enters an email not registered in the system
3. User clicks "Send Reset Link"
4. System does NOT reveal that the email is unregistered
5. Same success message shown as Flow 1: "Check your inbox..."
6. No email is sent (silently dropped)
7. Behavior is indistinguishable from Flow 1 to the user
```

### Flow 3: Invalid Email Format
```
1. User navigates to /reset-pass
2. User enters malformed email (e.g., "notanemail")
3. User clicks submit
4. Client-side validation triggers immediately
5. Error shown: "Please enter a valid email address"
6. No server request made
```

### Flow 4: Expired Reset Token
```
1. User clicks an old/expired reset link from email
2. Browser opens /reset-pass?token=<expired_token>
3. System validates token — detects expiry
4. Error message shown: "This link has expired"
5. Link to request a new reset is displayed
6. Stage 2 password form is NOT shown
```

### Flow 5: Already-Used Reset Token
```
1. User clicks a reset link that was already used
2. System validates token — detects already-consumed state
3. Error message shown: "This link has already been used"
4. Link to request a new reset is displayed
```

### Flow 6: Password Mismatch in Stage 2
```
1. User is on Stage 2 (/reset-pass?token=valid)
2. User enters new password
3. User enters a different value in confirm password
4. User clicks submit (or confirm field loses focus)
5. Validation error: "Passwords do not match"
6. Form not submitted
```

### Flow 7: Password Does Not Meet Policy
```
1. User is on Stage 2
2. User enters a weak password (e.g., "123")
3. User clicks submit
4. Validation error describing the policy requirements
5. Form not submitted
```

### Flow 8: Navigate Back to Login
```
1. User is on /reset-pass (any stage)
2. User clicks "Back to Login" link
3. Browser navigates to /login
```

---

## Validation Rules

### Stage 1 — Email Field
- Must not be empty
- Must be valid email format: `user@domain.tld`
- Whitespace trimmed before validation
- Submission blocked if format invalid (client-side)

### Stage 2 — New Password Field
- Must not be empty
- Minimum 8 characters (verify actual policy)
- Should require at least one: uppercase letter, lowercase letter, number, special character
- Must not be the same as previous password (if policy enforces it)

### Stage 2 — Confirm Password Field
- Must match New Password field exactly
- Validated on blur and on submit
- Real-time match indicator preferred

---

## Edge Cases

| ID | Scenario | Expected Behavior |
|---|---|---|
| EC-R-01 | Email with leading/trailing spaces | Trimmed and processed |
| EC-R-02 | Uppercase email | Treated as case-insensitive |
| EC-R-03 | Submitting the reset form multiple times quickly | Only one active token at a time; previous token invalidated |
| EC-R-04 | Requesting reset while already logged in | Should still work, or redirect to account settings |
| EC-R-05 | Token in URL has been tampered with | Treated as invalid token; error shown |
| EC-R-06 | Token is missing from URL on Stage 2 | Redirect to Stage 1 or clear error message |
| EC-R-07 | New password = current password | Error if policy disallows; accepted otherwise |
| EC-R-08 | New password with all spaces | Rejected by policy validation |
| EC-R-09 | XSS in email field: `<script>alert(1)</script>@x.com` | Sanitized, no execution |
| EC-R-10 | Reset link opened in different browser/device | Token is URL-based, must work cross-device |
| EC-R-11 | Very long password (500+ chars) | Graceful error or acceptance per policy |
| EC-R-12 | Page refresh on Stage 2 | Token re-validated; form re-shown or error if token consumed |
| EC-R-13 | Multiple browser tabs with same token | Only first successful submission accepted |
| EC-R-14 | Reset link opened after account deletion | Token validation fails gracefully |
| EC-R-15 | Rate limit hit on Stage 1 | User-facing message: "Too many requests, try again later" |

---

## Expected Behaviors

### Stage 1 Success State
- Success message is visible without page scroll
- Message is neutral and does not confirm whether email exists
- Submit button returns to default state (not stuck in loading)
- Email field may be cleared or retained (document actual behavior)

### Stage 2 Success State
- Brief success confirmation displayed
- Automatic redirect to `/login` within 2–3 seconds
- No way to re-use the same token after this point

### Error States
- All error messages are visible without scrolling
- Expired/invalid token message includes a clear action (request new link)
- Mismatch errors appear inline near the relevant field

### Accessibility
- All inputs have associated `<label>` elements
- Error messages linked via `aria-describedby`
- Tab order: Email → Submit → Back to Login
- Password strength requirements are readable by screen readers
- Stage 2 tab order: New Password → Confirm Password → Submit → Back to Login

---

## Test Data

### Stage 1 Inputs
```
Valid registered email:    mejbaur@markopolo.ai
Valid unregistered email:  ghost_user_99@nonexistent.com
Invalid format:            notanemail
Invalid format:            @domain.com
Injection:                 ' OR '1'='1'--@test.com
XSS:                       <script>alert(1)</script>@test.com
```

### Stage 2 Passwords
```
Valid strong password:     Test@1234!
Weak password (too short): 123
No special char:           TestPassword1
No number:                 TestPass!
All spaces:                "        "
Mismatched confirm:        NewPass@123 vs NewPass@456
Password = old password:   [same as current stored password]
```

---

## API Contract

### Stage 1 — Request Reset Email

| Method | Endpoint | Trigger |
|---|---|---|
| POST | `/api/auth/forgot-password` | Stage 1 form submit |

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response — Always 200 (to prevent enumeration):**
```json
{
  "message": "If an account exists with this email, a reset link has been sent."
}
```

---

### Stage 2 — Validate Token (on page load)

| Method | Endpoint | Trigger |
|---|---|---|
| GET | `/api/auth/reset-password/validate?token=<token>` | Page load with token param |

**Response — Valid (200):**
```json
{ "valid": true }
```

**Response — Invalid/Expired (400/410):**
```json
{ "error": "Token is invalid or has expired." }
```

---

### Stage 2 — Submit New Password

| Method | Endpoint | Trigger |
|---|---|---|
| POST | `/api/auth/reset-password` | Stage 2 form submit |

**Request Body:**
```json
{
  "token": "<reset_token>",
  "password": "NewSecurePassword@1",
  "confirmPassword": "NewSecurePassword@1"
}
```

**Response — Success (200):**
```json
{
  "message": "Password reset successfully.",
  "redirect": "/login"
}
```

**Response — Failure (400):**
```json
{
  "error": "Token has expired. Please request a new reset link."
}
```

---

## Related Pages
- `/login` — Entry point and post-reset destination
- `/signup` — For users without an account

---

## Coverage Gaps to Investigate
- [ ] Reset email delivery time SLA (should be under 60 seconds)
- [ ] Reset email content and link format
- [ ] Token TTL exact value (15 min? 60 min? 24 hours?)
- [ ] Whether previous active sessions are invalidated after reset
- [ ] Behavior when account email has changed since token was issued
- [ ] Whether reset works for OAuth-only accounts (accounts with no password)
- [ ] CSRF protection on the reset form submission
