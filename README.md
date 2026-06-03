# Fagun Autonomous QA Platform

<div align="center">

[![CI](https://github.com/Qatarat/mehad-automation/actions/workflows/ai-tests.yml/badge.svg)](https://github.com/Qatarat/mehad-automation/actions/workflows/ai-tests.yml)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Playwright](https://img.shields.io/badge/Playwright-1.44%2B-green?logo=playwright)
![Claude](https://img.shields.io/badge/Claude-Sonnet%204.6-blueviolet?logo=anthropic)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

**Write a simple text file describing your app. Get hundreds of automated tests — instantly.**

*1246+ tests · 68 pages covered · Works on staging and production · No coding required*

</div>

---

## What Is This?

This tool **automatically tests the Mehad website** — clicking buttons, filling forms, checking pages, logging in — exactly like a real user would, but hundreds of times faster and around the clock.

You do not need to be a programmer to use it. If you can:
- Copy and paste commands
- Follow numbered steps
- Read plain English

…you can run this tool.

---

## What Does It Test?

Every page in the Mehad app is described in a simple text file (called a "spec"). The tool reads those files and automatically:

- Opens the website in a browser
- Clicks buttons and fills forms
- Logs in as a teacher, then as a student
- Checks that the right things appear on screen
- Reports any problems it finds

**68 pages are covered.** Each page gets hundreds of checks including:
- Does the page load correctly?
- Are all buttons and links working?
- Does the login work with OTP?
- Do error messages appear when wrong input is entered?
- Is the page secure against attacks?
- Does data saved by the teacher appear correctly for the student?

---

## Before You Start — What You Need

Install these three things on your computer (free, one-time setup):

### 1. Python 3.10 or newer

Python runs the test code.

**Check if you already have it:**
```
python3 --version
```
If you see `Python 3.10.x` or higher — you're good. Skip this step.

**If not installed:**
- Go to **https://www.python.org/downloads/**
- Click the big yellow "Download Python" button
- Open the downloaded file and follow the installer
- On the last screen, make sure **"Add Python to PATH"** is checked

---

### 2. Node.js 18 or newer

Node.js runs the WhatsApp message reader (needed for production OTP).

**Check if you already have it:**
```
node --version
```
If you see `v18.x.x` or higher — skip this step.

**If not installed:**
- Go to **https://nodejs.org/**
- Click the **"LTS" (Long Term Support)** download button
- Open the file and follow the installer (keep all default settings)

---

### 3. Git

Git downloads the project code.

**Check if you already have it:**
```
git --version
```

**If not installed:**
- **Mac:** Open Terminal and type `git --version` — Mac will offer to install it automatically
- **Windows:** Download from **https://git-scm.com/download/win** and run the installer

---

## Installation — Step by Step

Open your **Terminal** (Mac) or **Command Prompt** (Windows) and run these commands one by one:

### Step 1 — Download the project

```bash
git clone https://github.com/Qatarat/mehad-automation
cd mehad-automation
```

> This downloads all the project files into a folder called `mehad-automation` and moves you into it.

---

### Step 2 — Install Python packages

```bash
pip install -r requirements.txt
```

> This installs all the Python tools the project needs (Playwright, pytest, etc.). Takes 1–2 minutes.

---

### Step 3 — Install the browser engine

```bash
playwright install chromium
```

> This downloads a special automated browser. Takes 1–2 minutes.

---

### Step 4 — Install WhatsApp bridge packages (for production OTP)

```bash
cd scripts
npm install
cd ..
```

> This installs the WhatsApp message reader. Takes 1–2 minutes.

---

### Step 5 — Create your settings file

```bash
cp .env.example .env
```

> This creates a file called `.env` where you put your phone numbers and passwords.
> Open `.env` in any text editor (Notepad, TextEdit, VS Code) to edit it.

---

## Settings File (.env) — What to Fill In

Open the `.env` file in a text editor. You will see sections like this:

### For staging/testing (dev.mehadedu.com) — easiest setup

These settings work immediately with no extra setup:

```
BASE_URL=https://dev.mehadedu.com/en

TEST_PHONE=98976564
TEST_COUNTRY=+880
TEST_OTP=123456

TEACHER_PHONE=98976564
TEACHER_OTP=123456

STUDENT_PHONE=98976564
STUDENT_OTP=123456
```

> The staging server always accepts OTP `123456` for registered test accounts.
> **No real phone or WhatsApp needed for staging.**

---

## Run Your First Test (Staging)

Once `.env` is set up for staging, run:

```bash
pytest tests/test_specs_all.py -v
```

You will see output like:

```
PASSED tests/test_specs_all.py::TestLogin::test_smoke_page_loads
PASSED tests/test_specs_all.py::TestLogin::test_nav_login_button_visible
PASSED tests/test_specs_all.py::TestLogin::test_func_otp_send_code_flow
...
1246 passed in 8m 42s
```

That's it — you are running 1246 automated tests.

---

## Watch the Tests Run (Optional)

Want to see the browser open and click things automatically? Add `HEADED=1`:

```bash
HEADED=1 pytest tests/test_specs_all.py -k "Login" -v
```

> `HEADED=1` makes the browser window visible instead of running hidden.
> `-k "Login"` runs only the Login page tests (faster for demos).

---

## Production Testing — Getting Real WhatsApp OTPs

When testing **https://mehadedu.com** (the live site), the app sends a real WhatsApp message with a 6-digit code. The tool needs to read that code automatically.

You have two free options:

---

### Option A — WAHA (Easiest for production · Requires Docker)

**What is WAHA?**
WAHA is a free program that connects to WhatsApp and lets our tool read incoming messages automatically. It runs inside Docker — a tool that runs programs in a self-contained box.

#### A1 — Install Docker Desktop

1. Go to **https://www.docker.com/products/docker-desktop**
2. Click **"Download for Mac"** (or Windows)

   > **Mac users:** If you have an Apple Silicon Mac (M1/M2/M3 chip), download "Apple Silicon". If you have an older Intel Mac, download "Intel Chip". Not sure? Go to Apple menu → About This Mac.

3. Open the downloaded file:
   - **Mac:** Drag the Docker icon into your Applications folder
   - **Windows:** Run the installer and follow the prompts

4. Launch Docker from your Applications (or Start menu)

5. Wait for the **whale icon** in the menu bar (Mac) or taskbar (Windows) to stop animating. When it's still, Docker is ready.

6. Verify it works — open Terminal/Command Prompt and type:
   ```bash
   docker --version
   ```
   You should see something like: `Docker version 27.x.x`

---

#### A2 — Start WAHA

Copy and paste this exact command into Terminal:

```bash
docker run -d --name waha --restart unless-stopped -p 3000:3000 devlikeapro/waha
```

**What each part means:**

| Part | What it does |
|---|---|
| `docker run` | Start a new program |
| `-d` | Run it in the background (you can close Terminal) |
| `--name waha` | Call it "waha" so you can find it later |
| `--restart unless-stopped` | Auto-restart if your computer reboots |
| `-p 3000:3000` | Make it available at http://localhost:3000 |
| `devlikeapro/waha` | The WAHA program to download and run |

The first time, it downloads WAHA (about 500MB). Subsequent starts are instant.

---

#### A3 — Connect your WhatsApp (scan QR — one time only)

1. Open your web browser and go to: **http://localhost:3000/dashboard**
2. You will see the WAHA dashboard
3. Click **"Start session"** → then click **"default"**
4. A **QR code** appears on screen
5. Open **WhatsApp** on your phone → tap **Settings** → **Linked Devices** → **Link a Device**
6. Point your phone camera at the QR code on your screen
7. The dashboard shows **"WORKING"** — your WhatsApp is now connected

> You only scan the QR code **once**. WAHA remembers the connection.
> Use a **test phone** (not your personal number) for this.

---

#### A4 — Update your .env for production

Open `.env` and change/add these lines:

```
BASE_URL=https://mehadedu.com/en
PROD_OTP_BACKEND=waha
WAHA_URL=http://localhost:3000
WAHA_SESSION=default
WAHA_CHAT_ID=+8801755572498@c.us

PROD_COUNTRY_CODE=+880
PROD_TEST_PHONE=1755572498
PROD_TEACHER_PHONE=1755572498
PROD_STUDENT_PHONE=1755572498
```

> Replace `+8801755572498` with your actual test phone number in this format: `+[country code][number]@c.us`
> Example: USA number +12025551234 becomes `+12025551234@c.us`

---

#### A5 — Run production tests

Make sure WAHA is running (step A2), then:

```bash
pytest tests/test_specs_all.py -v
```

When the test reaches the login step, it will:
1. Enter your phone number and click "Send Code"
2. Wait for the WhatsApp OTP to arrive (WAHA reads it automatically)
3. Enter the OTP and log in
4. Continue testing

---

#### Managing WAHA

```bash
# Check if WAHA is running
docker ps

# Stop WAHA
docker stop waha

# Start WAHA again (no QR needed — stays connected)
docker start waha

# View WAHA logs if something goes wrong
docker logs waha -f

# Completely remove WAHA (you would need to scan QR again)
docker rm -f waha
```

---

### Option B — whatsapp-web.js Bridge (No Docker needed)

This is already installed (you ran `npm install` in Step 4). Use this if you cannot install Docker.

#### B1 — Start the bridge

Open a Terminal window and run:

```bash
cd scripts
node whatsapp_otp_server.js
```

A QR code will print in the terminal like this:

```
[WA] Scan this QR code with your test WhatsApp account:

█████████████████████████████
█ ▄▄▄▄▄ █▀█ █▄█▀ ▀▄▀▄▀ ▄▄▄▄▄ █
█ █   █ █▀▀▄▀ ▄  ▄▀▄▄▀ █   █ █
...

[WA] Authenticated — session saved.
[WA] WhatsApp client ready. OTP server listening on :3001
```

Scan the QR code with your WhatsApp test phone (same as WAHA step A3).

> **Important:** Keep this Terminal window open while tests run. Opening a second Terminal window for the next step.

#### B2 — Update .env

```
BASE_URL=https://mehadedu.com/en
PROD_OTP_BACKEND=whatsapp_local
WA_OTP_PORT=3001
PROD_COUNTRY_CODE=+880
PROD_TEST_PHONE=1755572498
```

#### B3 — Run tests in the second Terminal window

```bash
pytest tests/test_specs_all.py -v
```

---

### Option C — Free Online SMS Receiver (No install, no account)

Use this if the site also sends OTP via **SMS** (not just WhatsApp).

> **Note:** Mehad currently uses WhatsApp for OTPs. Options A and B work with WhatsApp.
> Option C works if there is an SMS fallback. Try it — if no OTP arrives within 90 seconds, switch to Option A or B.

**Step 1 — Go to a free SMS receiver website:**
- **https://receivesmsfast.com** — has Bangladesh numbers
- **https://quackr.io** — has USA, EU numbers
- **https://sms-online.co** — has many countries

**Step 2 — Pick a number from the list on the website**

For example, on receivesmsfast.com you might pick: `+8801755572498`

**Step 3 — Update .env:**

```
BASE_URL=https://mehadedu.com/en
PROD_OTP_BACKEND=receivesmsfast
RECEIVESMSFAST_NUMBER=8801755572498
PROD_COUNTRY_CODE=+880
PROD_TEST_PHONE=1755572498
```

**Step 4 — Run tests:**

```bash
pytest tests/test_specs_all.py -v
```

The tool will poll the website every 5 seconds, waiting for the OTP to appear.

> These numbers are public — anyone can see messages sent to them. Only use for test accounts.

---

### Option D — Manual OTP (Simplest · No setup at all)

**The easiest way to test production.** You enter your own real phone number and type the OTP yourself when it arrives on WhatsApp. No Docker, no Node.js, no extra tools.

> **This is how the production login was verified live** — phone `+8801316314566` received a real WhatsApp OTP and login completed successfully on `https://mehadedu.com/en`.

#### How it works

1. The test opens the Mehad login page in a browser
2. It asks you: **"Enter your WhatsApp phone number"**
3. You type your number (e.g. `+8801316314566`)
4. Mehad sends a 6-digit OTP to your WhatsApp
5. The test asks: **"Enter the OTP from your WhatsApp"**
6. You type the 6 digits
7. Login completes — test continues automatically from there

#### D1 — Update your .env

```
BASE_URL=https://mehadedu.com/en
PROD_OTP_BACKEND=manual
```

That is all you need in `.env`. No phone numbers, no tokens — you enter everything interactively at run time.

#### D2 — Run the tests

Open a Terminal in the project folder and run:

```bash
pytest tests/test_specs_all.py -v -s
```

> The `-s` flag is important — it lets you type your answers when the test asks for your phone number and OTP.

#### D3 — What you will see

When the test reaches the login step, it pauses and shows:

```
[PROD OTP] Enter your WhatsApp phone number (with country code, e.g. +8801316314566):
```

Type your number and press **Enter**.

A few seconds later:

```
[PROD OTP] OTP sent to +8801316314566 — check your WhatsApp and enter the 6-digit code:
```

Open WhatsApp on your phone, find the message from Mehad, and type the 6 digits.

Login completes and the rest of the tests run automatically.

#### D4 — Running just the login test first

If you want to verify login works before running all 1200+ tests:

```bash
pytest tests/test_specs_all.py::TestSpec_Login -v -s
```

Or run the full QA login test:

```bash
pytest tests/test_qa_comprehensive.py::TestQA01Functional::test_qa01_full_login_flow_success -v -s
```

#### Tips for manual OTP mode

- **Have WhatsApp open** on your phone before running — the OTP arrives within a few seconds of "Send Code"
- **You have ~60 seconds** to enter the OTP before it expires
- If the OTP expires, just run the test again — a new code will be sent
- This mode is perfect for a **one-off production check** or when you don't have Docker available
- For **automated CI/CD** without manual input, use Option A (WAHA) instead

---

## Which Option Should I Use?

| My situation | Best option |
|---|---|
| Testing staging only (dev.mehadedu.com) | Just set `TEST_OTP=123456` in `.env` — no WhatsApp needed |
| **Quick production check, any phone** | **Option D — Manual OTP** (zero setup, you type the OTP) |
| Testing production, comfortable with Docker | **Option A — WAHA** (fully automatic, best for repeated runs) |
| Testing production, no Docker | **Option B — whatsapp-web.js** (already installed) |
| App sends SMS instead of WhatsApp | **Option C — free SMS receiver** (no install) |
| Running tests in CI/CD automatically | **Option A — WAHA** with a self-hosted instance |

---

## Running Specific Tests

```bash
# Run all tests (all 68 pages)
pytest tests/test_specs_all.py -v

# Run only the Login page tests
pytest tests/test_specs_all.py -k "Login" -v

# Run only the Find Tutors page
pytest tests/test_specs_all.py -k "FindTutors" -v

# Run the full comprehensive QA suite
pytest tests/test_qa_comprehensive.py -v

# Watch the browser (great for demos or debugging)
HEADED=1 SLOW_MO=1000 pytest tests/test_specs_all.py -k "Login" -v

# Run tests faster in parallel (4 at a time)
pytest tests/test_specs_all.py -n 4 -v
```

---

## Understanding the Test Results

When tests run, you will see:

```
PASSED  ← This check worked correctly
FAILED  ← Something went wrong — details shown below
ERROR   ← The test itself had a problem (not the app)
```

After all tests finish, a summary appears:

```
==================== 1198 passed, 48 failed in 9m 12s ====================
```

A detailed HTML report is saved in the `reports/` folder. Open `reports/index.html` in your browser to see:
- Which tests passed and failed
- Screenshots of failures
- Timing for each test

---

## Common Problems and Fixes

### "Auth setup failed" / Login not working

- Make sure `TEACHER_PHONE` is a registered account in the system
- For staging: confirm `TEST_OTP=123456` is in your `.env`
- Add `HEADED=1` to watch what happens: `HEADED=1 pytest tests/test_specs_all.py -k "Login" -v`

### WhatsApp OTP never arrives (production)

- **WAHA (Option A):** Open http://localhost:3000/dashboard — check the session status shows "WORKING". If not, click the session and restart it.
- **whatsapp-web.js (Option B):** Check the Terminal window where you ran `node whatsapp_otp_server.js` — it should say "WhatsApp client ready". If the window is closed, reopen it and run the command again.
- Make sure the phone number in `.env` matches the WhatsApp account you connected

### "playwright: Executable doesn't exist"

Run this:
```bash
playwright install chromium
```

### "Docker not found" or "Cannot connect to Docker"

- Make sure Docker Desktop is running (look for the whale icon in your menu bar / taskbar)
- If Docker Desktop is not installed, see the Docker installation steps in Option A above

### Tests run very slowly

```bash
LOAD_TIME_LIMIT=30 pytest tests/test_specs_all.py -v
```

### A new page spec is not creating tests

```bash
python3 scripts/validate_all_specs.py
pytest tests/test_specs_all.py -v
```

---

## Adding a New Page to Test

1. Create a new file in the `specs/` folder, e.g. `specs/checkout.md`
2. Write a description of the page in plain English with numbered steps:

```markdown
# Checkout Page

**URL:** `https://dev.mehadedu.com/en/checkout`

## Steps
1. Navigate to the checkout page
2. Select a payment method
3. Click "Pay Now"
4. Verify confirmation message appears
```

3. Run:
```bash
pytest tests/test_specs_all.py -k "Checkout" -v
```

Tests are automatically generated from your description. No coding needed.

---

## GitHub Actions (Automatic Testing in the Cloud)

The tests can run automatically on GitHub every time code changes, without you doing anything manually.

### Setup (one time)

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** for each of these:

| Secret name | What to put in it |
|---|---|
| `BASE_URL` | `https://dev.mehadedu.com/en` |
| `TEACHER_PHONE` | `98976564` |
| `STUDENT_PHONE` | `98976564` |
| `TEST_OTP` | `123456` |
| `TEST_COUNTRY` | `+880` |

### Running manually

1. Go to **Actions** tab in your GitHub repository
2. Click **Fagun Autonomous QA Platform** in the left sidebar
3. Click **Run workflow** → **Run workflow**

Tests run in the cloud and results appear in the Actions tab.

---

## Project Files Explained

```
mehad-automation/
│
├── specs/                    ← Text files describing each page (68 files)
│   └── login.md              ← Example: describes the login page
│
├── tests/
│   ├── test_specs_all.py     ← Auto-generated tests (do not edit manually)
│   └── test_qa_comprehensive.py  ← Extra detailed tests for homepage/login
│
├── scripts/
│   ├── get_otp.py            ← Reads OTP from WhatsApp/SMS automatically
│   └── whatsapp_otp_server.js ← WhatsApp bridge (Option B)
│
├── ai_engine/                ← The engine that reads specs and creates tests
│
├── reports/                  ← Test results saved here (open index.html)
│
├── .env.example              ← Template for your settings file
├── .env                      ← Your actual settings (never share this file)
└── requirements.txt          ← List of Python packages needed
```

---

## Getting Help

If something is not working:

1. Check the **Common Problems** section above
2. Add `HEADED=1` to your command to watch the browser and see what's happening
3. Check `docker logs waha -f` if using WAHA

---

<div align="center">

**Fagun Autonomous QA Platform**

Built by **[Mejbaur Bahar Fagun](mailto:mejbaur@markopolo.ai)** · Senior Software Engineer QA (IV) · Markopolo.ai

Powered by Claude + Playwright + Ollama

</div>
