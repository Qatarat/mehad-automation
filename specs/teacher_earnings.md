# Teacher Earnings & Payouts Spec

**URL:** `https://dev.mehadedu.com/en/dashboard/earnings`

## Overview
The Earnings & Payouts page (`/en/dashboard/earnings`) shows four financial metric cards (Total Earnings, Available Balance, Pending Earnings, Completed Payouts), an Earnings/Payout tab switcher, and a Recent Earnings history list. Shows "No earnings yet." when empty.

## URL
`/en/dashboard/earnings`

## Roles
- Teacher (authenticated)

## Prerequisites
- Teacher must be logged in: Bangladesh +880, phone 98976564, OTP 123456

## Test Scenarios

### TE-01: Page loads with Earnings & Payouts heading
**Given** a teacher is logged in and navigates to `/en/dashboard/earnings`
**When** the page finishes loading
**Then** the "Earnings & Payouts" heading is visible
**Selectors:**
- heading: `h1:has-text("Earnings & Payouts")`

### TE-02: Four metric cards are displayed
**Given** the earnings page is loaded
**When** the user views the summary section
**Then** four cards show: Total Earnings, Available Balance, Pending Earnings, Completed Payouts — each with a numeric value
**Selectors:**
- total earnings: `p:has-text("Total Earnings")`
- available balance: `p:has-text("Available Balance")`
- pending earnings: `p:has-text("Pending Earnings")`
- completed payouts: `p:has-text("Completed Payouts")`

### TE-03: Earnings and Payout tab buttons are present
**Given** the earnings page is loaded
**When** the user views the tab switcher
**Then** "Earnings" and "Payout" tab buttons are visible
**Selectors:**
- earnings tab: `button:has-text("Earnings")`
- payout tab: `button:has-text("Payout")`

### TE-04: Recent Earnings section shows empty state when no earnings
**Given** the teacher has no earnings
**When** the teacher views the earnings page
**Then** "Recent Earnings" heading and "No earnings yet." message are shown
**Selectors:**
- recent heading: `h3:has-text("Recent Earnings")`
- empty state: `text="No earnings yet."`

### TE-05: Payout tab shows payout request form or history
**Given** the earnings page is loaded
**When** the user clicks the "Payout" tab
**Then** the view switches to show payout request options or payout history
**Selectors:**
- payout tab: `button:has-text("Payout")`

### TE-06: Metric values are numeric (SAR formatted)
**Given** the earnings page is loaded
**When** the user reads the metric card values
**Then** all values display a numeric format (e.g. "0.00")
**Selectors:**
- value: `h3:has-text("0.00"), [class*="amount"], [class*="balance"]`

### TE-07: Negative — Unauthenticated access redirects
**Given** a user is not logged in
**When** the user navigates to `/en/dashboard/earnings`
**Then** the user is redirected to the homepage or login
**Selectors:**
- redirect: `/en` url
