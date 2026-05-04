# Page: Login
**URL:** `https://beta-stg.markopolo.ai/login`
**Type:** Authentication
**Priority:** P0 — Critical path, blocks all authenticated workflows

---

## Page Purpose

Entry point for existing users to authenticate and access the Markopolo platform. Failure here blocks 100% of authenticated feature usage.

---

## UI Elements

| Element | Identifier Hint | Type | Required |
|---|---|---|---|
| Email input | `email`, `type="email"` | Text input | Yes |
| Password input | `password`, `type="password"` | Text input | Yes |
| Login / Sign In button | Primary CTA button | Submit | Yes |
| Forgot Password link | Text link → `/reset-pass` | Navigation | No |
| Sign Up link | Text link → `/signup` | Navigation | No |
| Show/Hide password toggle | Eye icon on password field | Toggle | No |
| Remember Me checkbox | Optional persistent session | Checkbox | No |
| Social login (Google/SSO) | If present on page | OAuth button | No |
| Error message container | Inline or toast notification | Display | Conditional |

---

## Requirements

- REQ-L-01: Users must authenticate using a registered email and password.
- REQ-L-02: Invalid credentials must display a user-facing error message without revealing which field is incorrect.
- REQ-L-03: Successful login must redirect authenticated users to the dashboard or the originally requested URL.
- REQ-L-04: The form must prevent submission when required fields are empty.
- REQ-L-05: Email field must enforce valid email format before submission.
- REQ-L-06: Password field must mask characters by default.
- REQ-L-07: Session must persist appropriately based on "Remember Me" selection.
- REQ-L-08: Already authenticated users visiting `/login` must be redirected away (no double-login).
- REQ-L-09: Brute-force protection must be in place (rate limiting or lockout after N failed attempts).
- REQ-L-10: All form submissions must occur over HTTPS.

---

## User Flows

### Flow 1: Successful Login
```
1. User navigates to https://beta-stg.markopolo.ai/login
2. Page loads with email and password fields visible
3. User enters valid registered email address
4. User enters correct password
5. User clicks Login button
6. System validates credentials
7. System creates authenticated session
8. User is redirected to /dashboard (or originally intended URL)
9. User sees authenticated state (avatar, nav menu, etc.)
```

### Flow 2: Login with Invalid Credentials
```
1. User navigates to /login
2. User enters email address (valid format, may or may not be registered)
3. User enters incorrect password
4. User clicks Login button
5. System rejects credentials
6. Error message appears: generic "Invalid email or password" (no field-specific hint)
7. Password field is cleared; email field retains value
8. User remains on /login page
```

### Flow 3: Login with Empty Fields
```
1. User navigates to /login
2. User clicks Login button without filling any fields
3. Client-side validation triggers immediately (no server round-trip)
4. Both required fields highlight with error indicators
5. Appropriate inline validation messages appear
6. Form is not submitted
```

### Flow 4: Navigate to Forgot Password
```
1. User is on /login
2. User clicks "Forgot Password?" link
3. Browser navigates to /reset-pass
4. No authentication state is required
```

### Flow 5: Navigate to Sign Up
```
1. User is on /login
2. User clicks "Sign Up" / "Create account" link
3. Browser navigates to /signup
```

### Flow 6: Already Authenticated User
```
1. User has an active session
2. User navigates directly to /login
3. System detects existing valid session
4. User is automatically redirected to /dashboard
5. /login page is never rendered to the authenticated user
```

### Flow 7: Session Expiry
```
1. User had a session that has expired
2. User attempts to access a protected route
3. System redirects to /login with a return URL parameter
4. After successful login, user is redirected back to original destination
```

---

## Validation Rules

### Email Field
- Must not be empty (required)
- Must match email format: `user@domain.tld`
- Must not accept: `user@domain`, `@domain.com`, `userdomain.com`, plain text
- Whitespace trimmed before validation
- Case-insensitive comparison on server

### Password Field
- Must not be empty (required)
- Minimum length check is a server-side concern (no frontend hint about requirements on login)
- Characters must be masked by default
- Show/hide toggle switches between `type="password"` and `type="text"`

### Submission
- Login button disabled or form blocked while submission is in-flight (prevent double submit)
- Network errors must show a user-friendly message (not a raw HTTP status)

---

## Edge Cases

| ID | Scenario | Expected Behavior |
|---|---|---|
| EC-L-01 | Email with leading/trailing whitespace | Trim and process normally |
| EC-L-02 | Email in uppercase | Treat as case-insensitive match |
| EC-L-03 | Password with special characters `!@#$%^&*()` | Accept and process correctly |
| EC-L-04 | Password with spaces | Accept as valid input |
| EC-L-05 | Very long email (255+ chars) | Graceful error, no crash |
| EC-L-06 | Very long password (500+ chars) | Graceful error, no crash |
| EC-L-07 | SQL injection attempt in email: `' OR '1'='1` | Sanitized; login fails safely |
| EC-L-08 | XSS in email: `<script>alert(1)</script>@x.com` | Sanitized; no script execution |
| EC-L-09 | Rapid repeated failed logins (5+ times) | Rate limit triggers; lockout or CAPTCHA |
| EC-L-10 | Login on slow/offline network | Loading state shown; timeout error displayed |
| EC-L-11 | Back button after successful login | Does not re-submit login form |
| EC-L-12 | Copy-pasted email with invisible Unicode characters | Normalized or rejected gracefully |
| EC-L-13 | Unverified account attempting login | Clear message: "Please verify your email" |
| EC-L-14 | Deactivated/suspended account | Clear message without exposing system details |
| EC-L-15 | Login on mobile viewport (375px wide) | Layout intact, inputs usable, keyboard doesn't overlap CTA |

---

## Expected Behaviors

### Success States
- Redirect to `/dashboard` or return URL within 2 seconds of credential acceptance
- No login page flash after redirect
- User avatar / greeting visible in post-login view

### Error States
- Error message is visible without scrolling
- Error is descriptive enough to guide user but not expose security details
- Error does not persist after the user starts correcting input

### Loading State
- Login button shows loading indicator during API call
- Inputs are disabled during submission to prevent duplicate requests
- Loading state resolves in ≤ 5 seconds under normal conditions

### Accessibility
- All inputs have associated `<label>` elements
- Error messages are linked via `aria-describedby`
- Tab order: Email → Password → Login button → Forgot Password → Sign Up
- Page is navigable with keyboard only
- Screen reader announces errors when they appear

---

## Test Data

### Valid Credentials
```
email: mejbaur@markopolo.ai
password: [use environment variable TEST_USER_PASSWORD]
```

### Invalid Credentials
```
email: notregistered@example.com
password: WrongPassword123!

email: mejbaur@markopolo.ai
password: IncorrectPass999
```

### Malformed Inputs
```
email: notanemail
email: @nodomain.com
email: spaces here@test.com
email: <script>alert(1)</script>@test.com
password: (empty string)
password: ' OR '1'='1'--
```

---

## API Contract

| Method | Endpoint | Trigger |
|---|---|---|
| POST | `/api/auth/login` or `/api/v1/session` | Form submission |
| GET | `/api/auth/session` | Page load (check existing session) |

### Expected Request Body
```json
{
  "email": "user@example.com",
  "password": "userPassword"
}
```

### Expected Response — Success (200)
```json
{
  "token": "<jwt_or_session_token>",
  "user": {
    "id": "...",
    "email": "...",
    "name": "..."
  },
  "redirect": "/dashboard"
}
```

### Expected Response — Failure (401)
```json
{
  "error": "Invalid email or password"
}
```

### Expected Response — Rate Limited (429)
```json
{
  "error": "Too many attempts. Please try again later."
}
```

---

## Related Pages
- `/reset-pass` — Triggered via Forgot Password link
- `/signup` — Triggered via Sign Up link
- `/dashboard` — Post-login destination

---

## Coverage Gaps to Investigate
- [ ] Behavior when cookies are disabled in browser
- [ ] Login via magic link (if feature exists)
- [ ] Multi-factor authentication (MFA) flow (if enabled)
- [ ] SSO / Google OAuth redirect and callback handling
- [ ] Concurrent login from multiple devices/tabs
- [ ] Session token rotation on login
