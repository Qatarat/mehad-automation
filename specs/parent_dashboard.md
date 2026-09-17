# Page: Parent Dashboard — Manage Children, Bookings & Account

**URL:** `https://dev.mehadedu.com/en/dashboard/sessions`

## Description
The Parent role logs in via the homepage modal's "Parent" tab (see `login.md`) and lands on a dashboard for managing one or more child profiles, viewing/booking sessions, tracking invoices, and managing saved addresses and account credentials. This is a previously undocumented feature area — no spec existed for the Parent role despite it being the platform's default login tab. Coverage below is derived from the dashboard.html QA matrix's "Parent Portal & Manage Child" feature description and must be confirmed/adjusted against the live sidebar structure the first time this spec is run (mark any selector that does not match with an updated selector, do not silently skip).

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| Sidebar Sessions link | `a:has-text("Sessions")` | Required |
| Sidebar My Children / Manage Children link | `a:has-text("Children"), a:has-text("My Children")` | Required |
| Sidebar Bookings link | `a:has-text("Bookings"), a:has-text("My Bookings")` | Required |
| Sidebar Messages link | `a:has-text("Messages")` | Required |
| Sidebar Addresses link | `a:has-text("Address")` | Required |
| Sidebar Invoices/Payment History link | `a:has-text("Invoice"), a:has-text("Payment History")` | Required |
| Sidebar Settings/Account link | `a:has-text("Settings"), a:has-text("Account")` | Required |
| Add Child button | `button:has-text("Add Child")` | Required |
| Child profile form — name | `input[name*="child" i][name*="name" i], input[placeholder*="Child" i]` | Required |
| Child profile form — grade/curriculum | `select[name*="curriculum" i], select[name*="grade" i]` | Required |
| Child profile form — birth date | `input[type="date"], input[name*="birth" i]` | Required |
| Child profile save button | `button:has-text("Save")` | Required |
| Child credential setup (username/password for Child Login) | `input[name*="username" i]`, `input[name*="password" i]` | Required — this is what provisions `/en/child-login` access |
| Delete/Remove child action | `button:has-text("Remove"), button:has-text("Delete")` | Required |
| Add Address form | `button:has-text("Add Address")` | Required |
| Address fields (street/city/postal/country) | `input[name*="street" i], input[name*="city" i], input[name*="postal" i], select[name*="country" i]` | Required |
| Invoice/history table | `table, [data-testid="invoice-list"]` | Required |
| Invoice VAT line item | `:text("VAT"), :text("15%")` | Required — Saudi 15% VAT must be itemized |
| Account switcher (role badge) | `text="Parent"` | Required |

## User Flows

### Flow 1: Add a Child Profile
1. Log in as Parent (Parent tab, phone 500000000, OTP 6789 on prod / dev-equivalent fixed OTP)
2. Navigate to "My Children"
3. Click "Add Child"
4. Fill name, birth date, curriculum/grade
5. Click "Save"
→ Expected: New child appears in the children list; a corresponding Child Login username/password is generated or settable

### Flow 2: Provision Child Login Credentials
1. Open an existing child profile
2. Set/reset the child's username and password used at `/en/child-login`
3. Save
4. Open a new session, log in at `/en/child-login` with those exact credentials
→ Expected: Child login succeeds and lands on the restricted Sessions/Messages-only dashboard (see `child_portal.md`)

### Flow 3: Book a Session for a Child
1. Log in as Parent
2. Navigate to Bookings / Find Tutors
3. Select a child, a subject/curriculum, a tutor, and a time slot
4. Confirm booking
→ Expected: Session appears in Sessions list associated with the correct child; booking triggers an invoice with 15% VAT applied

### Flow 4: Manage Saved Addresses
1. Navigate to Addresses
2. Click "Add Address"
3. Fill Saudi address (street, city e.g. Riyadh, postal code, country Saudi Arabia)
4. Save
→ Expected: Address appears in the saved list and is selectable during checkout

### Flow 5: View Invoice History
1. Navigate to Invoices / Payment History
2. Open a past invoice
→ Expected: Line items shown including base price and 15% VAT, matching Saudi ZATCA e-invoice expectations

## Requirements
- REQ-01: Parent dashboard must show a "My Children" area distinct from the Parent's own profile
- REQ-02: Each child profile supports create, edit, and delete
- REQ-03: Child Login credentials (username/password) are settable from the Parent's child-management UI, and take effect immediately at `/en/child-login`
- REQ-04: A Parent can have more than one child profile linked to the same account
- REQ-05: Booking a session requires selecting which child the session is for
- REQ-06: Every invoice/payment record itemizes a 15% VAT line matching Saudi tax requirements
- REQ-07: Parent cannot access another parent's children, bookings, or invoices by guessing/incrementing an ID in the URL (IDOR check)
- REQ-08: Deleting a child profile must not orphan/expose that child's historical session or invoice records to unauthorized viewers
- REQ-09: Address form validates required fields (street, city, postal code, country) before allowing save
- REQ-10: Page title must not contain 500 or 404 anywhere in this dashboard

## Edge Cases
| EC-01 | Add child with empty name | Save button disabled or inline required-field error |
| EC-02 | Add child with future birth date | Rejected with validation error |
| EC-03 | Add child with birth date implying age > 100 or negative age | Rejected with validation error |
| EC-04 | Set child username that already exists for another child/account | Rejected with a clear "username taken" error, no silent overwrite |
| EC-05 | Set child password shorter than minimum length (e.g. "1") | Rejected with a minimum-length validation error |
| EC-06 | Remove a child who has upcoming booked sessions | Either blocked with a warning, or cascades safely without leaving a broken session reference |
| EC-07 | Book a session without selecting a child | Booking blocked until a child is selected |
| EC-08 | Change another parent's child ID in the dashboard URL (e.g. `/en/dashboard/children/999`) | Returns 403/redirect, not another family's data |
| EC-09 | XSS payload in child name field (`<script>alert(1)</script>`) | Stored/rendered as literal text, no script execution anywhere it's displayed (list, invoice, session card) |
| EC-10 | SQL injection payload in address city field (`' OR 1=1--`) | Rejected or safely escaped, no 500, no data leakage |
| EC-11 | Add address with only Saudi-format postal code vs a clearly invalid one ("ABCDE") | Valid postal code accepted, invalid one rejected with inline error |
| EC-12 | Concurrent booking of the same tutor time slot from two children under one parent | Second attempt is blocked with a clear conflict message, no double-booking |
| EC-13 | View invoice history with zero invoices | Clean empty state, no console errors |
| EC-14 | Session/network expiry mid-checkout after selecting a child and slot | Graceful error, no partial/duplicate booking created |

## Test Data
### Valid
| Field | Value |
|---|---|
| name | 500000000 |
| name | 6789 |
| name | Automations Parent |
| name | Riyadh |
| name | King Fahd Road |
| name | 12211 |
| name | Saudi Arabia |

### Invalid
| Field | Value |
|---|---|
| name | ' OR 1=1-- |
| name | <script>alert(1)</script> |
| name | ABCDE |
| name |  |
| name | 2099-13-32 |
