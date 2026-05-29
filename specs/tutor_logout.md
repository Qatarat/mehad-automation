# Page: Tutor Logout

**URL:** `https://dev.mehadedu.com/en/dashboard`

## Description
Tutor logout flow from dashboard. Clicking the avatar at the bottom of the sidebar shows "My Profile" and "Logout" options. Clicking Logout clears session and redirects to landing page.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Tutor avatar/name in sidebar | `.sidebar-avatar, [data-testid="user-avatar"]` | Required |
| Profile popup | `.profile-popup, [role="menu"]` | Conditional |
| My Profile option | `[role="menuitem"]:has-text("My Profile"), button:has-text("My Profile")` | Optional |
| Logout option | `[role="menuitem"]:has-text("Logout"), button:has-text("Logout")` | Required |
| Log In button (post-logout) | `button:has-text("Log In")` | Required after logout |
| Landing page heading | `h1:has-text("Learn with the Best")` | Optional |

## User Flows

### Flow 1: Tutor Logout
1. Log in as tutor (phone 98976564, OTP 123456)
2. Navigate to tutor dashboard
3. Click avatar/name at bottom of sidebar
4. Popup shows "My Profile" and "Logout"
5. Click "Logout"
→ Expected: Session cleared, redirected to /en, "Log In" button visible

### Flow 2: Verify Post-Logout State
1. After logout, verify homepage loads
2. Header shows "Log In" button (not logged-in user)
3. Dashboard routes redirect to login
→ Expected: Fully unauthenticated state

## Requirements
- REQ-01: Sidebar shows tutor avatar and name while authenticated
- REQ-02: Clicking avatar shows My Profile and Logout popup
- REQ-03: Logout clears session cookie and localStorage
- REQ-04: After logout, user is redirected to landing page
- REQ-05: Dashboard URLs redirect to login after logout

## Edge Cases
| EC-01 | Logout and navigate back | Auth protected pages redirect to login |
| EC-02 | Logout in multiple tabs | All tabs cleared |
| EC-03 | Session already expired | Logout still works gracefully |
| EC-04 | Network error during logout | Session cleared locally |

## Test Data
### Valid
| Field | Value |
|---|---|
| name | 98976564 |
| name | 123456 |

### Invalid
| Field | Value |
|---|---|
| name | 000000 |
