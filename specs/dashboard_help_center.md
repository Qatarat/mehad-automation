# Dashboard Help Center Spec

## Overview
The Help Center page is accessible from the sidebar of both the student and teacher dashboards. It provides FAQ / support content for authenticated users. The URL is `/en/dashboard/help-center` for both roles.

## URL
`/en/dashboard/help-center`

## Roles
- Student (authenticated)
- Teacher (authenticated)

## Prerequisites
- Student credentials: Bangladesh +880, phone 98976564, OTP 123456
- Teacher credentials: same phone, via `/en/tutor-login`

## Test Scenarios

### HC-01: Student can navigate to Help Center from sidebar
**Given** a student is logged in on the dashboard
**When** the student clicks "Help Center" in the sidebar
**Then** the browser navigates to `/en/dashboard/help-center` and help content is displayed
**Selectors:**
- help center link: `a[href="/en/dashboard/help-center"]`
- heading: `h1:has-text("Help"), h2:has-text("Help")`

### HC-02: Teacher can navigate to Help Center from sidebar
**Given** a teacher is logged in on the dashboard
**When** the teacher clicks "Help Center" in the sidebar
**Then** the browser navigates to `/en/dashboard/help-center` and help content is displayed
**Selectors:**
- help center link: `a[href="/en/dashboard/help-center"]`

### HC-03: Page loads without errors
**Given** an authenticated user navigates to `/en/dashboard/help-center`
**When** the page finishes loading
**Then** no 404 or 500 error is displayed
**Selectors:**
- no error: `title:not(:has-text("404"))`

### HC-04: Negative — Unauthenticated access redirects to login
**Given** a user is not logged in
**When** the user navigates directly to `/en/dashboard/help-center`
**Then** the user is redirected to the homepage or login prompt
**Selectors:**
- redirect: `/en` url or `[role="dialog"]:has-text("Welcome back")`
