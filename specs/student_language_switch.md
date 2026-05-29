# Page: Language Switcher

**URL:** `https://dev.mehadedu.com/en`

## Description
Bilingual language switcher between English (/en) and Arabic (/ar). Toggle buttons in the header switch the full interface between LTR English and RTL Arabic.

## UI Elements

| Element | Selector | Notes |
|---|---|---|
| English language button | `button[aria-label="English"], button:has-text("EN")` | Required |
| Arabic language button | `button[aria-label="العربية"], button:has-text("AR")` | Required |
| Active language indicator | `button[aria-current="true"], .lang-btn.active` | Optional |
| Page heading (EN) | `h1:has-text("Learn with the Best")` | Required in EN |
| HTML dir attribute | `html[dir="rtl"]` | Required in AR |

## User Flows

### Flow 1: Switch to Arabic
1. Navigate to https://dev.mehadedu.com/en
2. Click "AR" language button in header
3. Page reloads/navigates to /ar
4. All content displays in Arabic RTL
→ Expected: URL changes to /ar, content in Arabic, dir="rtl"

### Flow 2: Switch Back to English
1. Navigate to https://dev.mehadedu.com/ar
2. Click "EN" language button
3. Page navigates to /en
4. Content in English LTR
→ Expected: URL changes to /en, content in English

### Flow 3: Language Persists Across Navigation
1. Switch to Arabic
2. Navigate to another page (e.g., /ar/find-tutors)
3. Language remains Arabic
→ Expected: Arabic locale maintained

## Requirements
- REQ-01: EN and AR language toggle buttons visible in header
- REQ-02: Clicking AR navigates to /ar locale
- REQ-03: Arabic locale sets dir="rtl" on HTML element
- REQ-04: Clicking EN navigates to /en locale
- REQ-05: Active language button is visually indicated
- REQ-06: All page content translates to selected language

## Edge Cases
| EC-01 | Click active language button | No change or page reloads same locale |
| EC-02 | Direct navigation to /ar | Full Arabic interface shown |
| EC-03 | Arabic with login modal | Modal renders in Arabic |
| EC-04 | Language switch while logged in | Session maintained |

## Test Data
### Valid
| Field | Value |
|---|---|
| name | English |
| name | Arabic |

### Invalid
| Field | Value |
|---|---|
| name | unsupported_language |
