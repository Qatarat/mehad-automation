# Student Payment & Wallet Spec

**URL:** `https://dev.mehadedu.com/en/dashboard/wallet`

## Overview
The Payment & Wallet page (`/en/dashboard/wallet`) shows the student's transaction history under a "Payments" heading. It lists "Recent Transactions" with a "No transactions found" state when empty. Accessible only to authenticated students.

## URL
`/en/dashboard/wallet`

## Roles
- Student (authenticated)

## Prerequisites
- Student must be logged in: Bangladesh +880, phone 98976564, OTP 123456

## Test Scenarios

### SW-01: Wallet page loads with Payments heading
**Given** a student is logged in and navigates to `/en/dashboard/wallet`
**When** the page finishes loading
**Then** the "Payments" heading is visible
**Selectors:**
- heading: `h1:has-text("Payments")`

### SW-02: Recent Transactions section shows empty state when no transactions
**Given** the student has no transaction history
**When** the student views the wallet page
**Then** "Recent Transactions" heading and "No transactions found" message are displayed
**Selectors:**
- transactions heading: `text="Recent Transactions"`
- empty state: `text="No transactions found"`

### SW-03: Transactions list shows entries when purchases exist
**Given** the student has made at least one booking payment
**When** the student views the wallet page
**Then** transaction entries are shown with amount, date, and status
**Selectors:**
- transaction entry: `[data-testid="transaction"], .transaction-row, tr`

### SW-04: Sidebar navigation is present
**Given** the student is on the wallet page
**When** the user inspects the sidebar
**Then** the Payment & Wallet link in the sidebar is active/highlighted
**Selectors:**
- wallet link active: `a[href="/en/dashboard/wallet"][aria-current="page"], a[href="/en/dashboard/wallet"].active`

### SW-05: Negative — Unauthenticated access redirects
**Given** a user is not logged in
**When** the user navigates to `/en/dashboard/wallet`
**Then** the user is redirected to the homepage or login
**Selectors:**
- redirect: `/en` url or login modal
