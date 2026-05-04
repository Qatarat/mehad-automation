# Markopolo Autonomous AI Testing

> **Intent-based autonomous QA system** — describe the system in Markdown, let AI handle everything else.

**Zero API keys. Zero hardcoded scripts. Zero manual maintenance. 100% free and open source.**

---

## What Is This?

A self-writing, self-healing QA automation system that:

1. **Reads** your Markdown spec files (written by a human QA)
2. **Compiles** them into deterministic JSON (no AI guessing structure)
3. **Generates** Playwright tests across all 15 testing types
4. **Validates** the generated code before execution (AST gate)
5. **Runs** tests against your staging environment
6. **Heals** failures automatically (3 rounds of AI self-fix)
7. **Reports** a professional HTML bug report with POC screenshots
8. **Learns** from failures via persistent memory between runs

```
specs/*.md → Spec Compiler → JSON → AI → 15 Test Types → Validate → Execute
           → Self-Heal → Bug Tickets (with POC) → Gap Analysis → HTML Report
```

Push a change → GitHub Actions runs the full pipeline automatically.

---

## v2 Architecture (Production-Grade)

```
login.md
   ↓
spec_compiler.py  ← converts MD to structured JSON (no AI interpretation)
   ↓
login.spec.json   ← deterministic selector map + flows + edge cases
   ↓
test_generator.py ← generates all 15 test types (AI + template fallback)
   ↓
test_validator.py ← AST gate (blocks syntax errors, missing assertions, dangerous code)
   ↓
pytest execution  ← with conftest.py evidence capture (network + console + performance)
   ↓
memory.py         ← records failures, persists selector fixes between runs
   ↓
self-healing loop ← AI rewrites failing tests (max 3 rounds)
   ↓
bug_builder.py    ← per-failure AI bug tickets with POC screenshots
   ↓
gap_checker.py    ← coverage gap analysis against spec requirements
   ↓
reporter.py       ← full HTML report (dark theme, screenshots, network logs)
```

### Why This Architecture?

| Old Approach (v1)               | This Approach (v2)                          |
|---------------------------------|---------------------------------------------|
| AI interprets raw Markdown      | Compiler extracts structure first           |
| AI guesses selectors            | Selector map built from UI element table    |
| Same spec → different tests     | Same spec → same JSON → deterministic tests |
| One giant AI prompt             | 15 focused prompts (no token overflow)      |
| No validation before execution  | AST validator blocks broken code            |
| Starts fresh every run          | Memory persists fixes between runs          |

---

## AI Stack (all free, all local)

| Tool | Role | Cost |
|------|------|------|
| **Ollama** | Local AI inference (no cloud, no API key) | Free |
| **qwen2.5-coder:1.5b** | Primary model — generates test code | Free |
| **llama3.2:1b** | Fallback model 1 | Free |
| **phi3.5** | Fallback model 2 | Free |
| **qwen2.5:0.5b** | Fallback model 3 (tiny last resort) | Free |
| **Playwright** | Browser automation | Free / Open source |
| **pytest** | Test execution framework | Free / Open source |
| **GitHub Actions** | CI/CD runner (2000 min/month free) | Free |

5-model fallback chain. If the primary model fails or runs out of tokens, the next model takes over automatically. If ALL models fail, a template engine generates valid (but simpler) tests.

---

## 15 Test Types Covered

| # | Type | What it tests |
|---|------|---------------|
| 1 | **Functional** | Every user flow in the spec |
| 2 | **Validation** | Form field rules (valid/invalid inputs) |
| 3 | **Negative** | Wrong credentials, empty fields, rejected inputs |
| 4 | **Boundary** | Min/max length, 255 chars, overflow, empty strings |
| 5 | **Security** | XSS payloads, SQL injection (OWASP standard vectors) |
| 6 | **API/Network** | Request method, response status, response body |
| 7 | **Accessibility** | axe-core violations, ARIA labels, keyboard nav |
| 8 | **Responsive** | 375px mobile, 768px tablet, 1280px desktop |
| 9 | **Navigation** | Internal links (forgot password, sign up, back) |
| 10 | **Session/Auth** | Token persistence, redirect when authenticated |
| 11 | **Performance** | Page load < 3s, DOMContentLoaded, large resources |
| 12 | **Console Errors** | No JS errors on page load or form interaction |
| 13 | **Error States** | No stack traces exposed, network error handling |
| 14 | **Visual/Layout** | Elements within viewport, title set, favicon loads |
| 15 | **Cross-browser** | Smoke tests tagged for Chromium/Firefox/WebKit |

---

## Local Setup (Step by Step)

### Prerequisites

- macOS or Linux
- Python 3.10+
- Git

### 1. Clone the repo

```bash
git clone https://github.com/mejbaur-markopolo/Markopolo-Automation-Testing.git
cd Markopolo-Automation-Testing
```

### 2. Install Ollama

```bash
# macOS
brew install ollama
brew services start ollama   # run as background service

# Linux
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve &
```

### 3. Pull AI models

```bash
# Minimum (CI-grade, 1GB):
ollama pull qwen2.5-coder:1.5b

# Recommended for local (better quality, 4GB):
ollama pull qwen2.5-coder:7b

# Backup models (pulled automatically in CI):
ollama pull llama3.2:1b
```

### 4. Install Python dependencies

```bash
# macOS with Homebrew Python
pip3 install -r requirements.txt
playwright install chromium

# Or with pip
pip install -r requirements.txt
playwright install chromium
```

### 5. Run the agent

```bash
# Basic run (uses default staging URL)
python ai_engine/agent.py

# Custom URL
BASE_URL=https://your-staging-url.com python ai_engine/agent.py

# Better AI quality locally
AI_MODEL=qwen2.5-coder:7b python ai_engine/agent.py

# With test password for login tests
TEST_PASSWORD=YourPass python ai_engine/agent.py
```

### 6. View the report

```bash
open reports/bug-report.html
```

---

## Adapt to ANY Project (Just Change the MD Files)

This system is designed to work with any web application. To test a different project:

### Step 1: Delete the existing specs

```bash
rm specs/*.md
```

### Step 2: Create your own spec file

Use this structure for each page:

```markdown
# Page: Login

**URL:** `https://your-app.com/login`
**Priority:** P0

## UI Elements

| Element | Type / Hint | Description |
|---------|-------------|-------------|
| Email input | email, type="email" | Primary email field |
| Password input | password, type="password" | Password field |
| Login button | submit, CTA button | Primary submit button |

## Requirements

| ID | Requirement |
|----|-------------|
| REQ-L-01 | User can log in with valid credentials |
| REQ-L-02 | Invalid credentials show error message |

## User Flows

### Flow 1 — Happy Path Login
1. Navigate to /login
2. Enter valid email
3. Enter valid password
4. Click login button
5. Redirects to dashboard

### Flow 2 — Invalid Login
1. Navigate to /login
2. Enter invalid email
3. Enter wrong password
4. Click login button
5. Error message displayed

## Validation Rules

- Email must be valid format
- Password minimum 8 characters
- Both fields required

## Edge Cases

| ID | Scenario | Expected |
|----|----------|----------|
| EC-L-01 | SQL injection in email | Login fails safely |
| EC-L-02 | XSS in password field | Sanitized, no alert |

## API Contract

POST /api/auth/login
- 200 on success
- 401 on invalid credentials

## Test Data

### Valid
| Field | Value |
|-------|-------|
| email | testuser@example.com |
| password | Test@1234! |

### Invalid
| Field | Value |
|-------|-------|
| email | notanemail |
| password | 123 |
```

### Step 3: Change the BASE_URL

```bash
# In the run command:
BASE_URL=https://your-staging.com python ai_engine/agent.py

# Or set it permanently in .env:
echo "BASE_URL=https://your-staging.com" >> .env
```

### Step 4: Push and watch it run

```bash
git add specs/
git commit -m "Add specs for my project"
git push
```

GitHub Actions picks it up automatically.

---

## Project Structure

```
Markopolo-Automation-Testing/
│
├── specs/                        ← YOUR INPUT (edit these)
│   ├── login.md                  ← Login page spec
│   ├── reset-password.md         ← Password reset spec
│   ├── signup.md                 ← Registration spec
│   └── *.spec.json               ← Auto-compiled (do not edit)
│
├── ai_engine/                    ← Core system (no need to edit)
│   ├── agent.py                  ← Main orchestrator (ReAct loop)
│   ├── spec_parser.py            ← Parses MD into ParsedSpec dataclass
│   ├── spec_compiler.py          ← MD → structured JSON (v2 deterministic layer)
│   ├── test_generator.py         ← Generates all 15 test types
│   ├── test_validator.py         ← AST validation gate
│   ├── evidence.py               ← Loads network/console/performance evidence
│   ├── bug_builder.py            ← AI bug ticket writer
│   ├── gap_checker.py            ← Coverage gap analysis
│   ├── memory.py                 ← Persistent memory (learns between runs)
│   └── reporter.py               ← HTML report generator
│
├── payloads/                     ← Security test payloads (OWASP standard)
│   ├── xss.txt                   ← XSS vectors
│   ├── sqli.txt                  ← SQL injection vectors
│   ├── boundary.txt              ← Boundary test strings
│   └── __init__.py               ← Payload loader
│
├── tests/                        ← AI-generated (runtime, gitignored)
├── reports/                      ← Results (runtime, gitignored)
│   ├── bug-report.html           ← Main HTML report
│   ├── screenshots/              ← Failure screenshots (POC)
│   ├── evidence/                 ← Per-test network/console/perf data
│   ├── gaps_*.md                 ← Coverage gap reports
│   └── summary.json              ← Machine-readable summary
│
├── conftest.py                   ← pytest config + evidence capture
├── pytest.ini                    ← pytest settings
├── requirements.txt              ← Python dependencies
├── memory_store.json             ← Persistent memory (learns from failures)
│
└── .github/workflows/
    └── ai-tests.yml              ← Full CI/CD pipeline
```

---

## CI/CD

Every push to `main` triggers the full pipeline:

```
checkout → install deps → install Ollama → cache models → pull models
→ verify all modules → compile specs → run AI agent → upload artifacts
```

### Artifacts produced per run

| Artifact | Contents |
|----------|----------|
| `bug-report-N` | Self-contained HTML report with screenshots |
| `screenshots-N` | PNG failure screenshots (POC evidence) |
| `full-reports-N` | All reports + evidence + JSON data |
| `ai-generated-tests-N` | The generated Playwright test files |
| `compiled-specs-N` | Compiled JSON spec files |

### Manual trigger

Go to: **Actions → Markopolo Autonomous AI Testing → Run workflow**

---

## Model Recommendations

| Model | RAM | Use Case | Command |
|-------|-----|----------|---------|
| `qwen2.5-coder:1.5b` | 1GB | GitHub Actions CI | Default |
| `qwen2.5-coder:7b` | 4GB | Local development | `AI_MODEL=qwen2.5-coder:7b` |
| `llama3.2:1b` | 1.3GB | Fast fallback | Auto |
| `phi3.5` | 2.2GB | General reasoning fallback | Auto |
| `deepseek-coder-v2:16b` | 10GB | Best quality locally | `AI_MODEL=deepseek-coder-v2:16b` |

---

## Troubleshooting

### "Ollama not running"

```bash
# macOS
brew services start ollama

# Linux
ollama serve &
```

### "0 tests collected"

The generated file might be in `tests/`. Check:

```bash
python ai_engine/test_validator.py tests/
cat tests/test_login.py
```

### "pip not found" on macOS

```bash
pip3 install -r requirements.txt
```

### Tests pass but report is empty

Check that `reports/` directory exists:

```bash
mkdir -p reports reports/screenshots reports/evidence
```

### AI keeps producing syntax errors

The template engine handles this. If you see "using template fallback", it means all AI models failed. Try a larger model:

```bash
AI_MODEL=qwen2.5-coder:7b python ai_engine/agent.py
```

---

## Spec File Format Reference

Your Markdown spec must use these exact section headings:

```markdown
## UI Elements       ← table of form fields and elements
## Requirements      ← REQ-X-NN: requirement text
## User Flows        ← ### Flow N — Name, then numbered steps
## Validation        ← bullet list of validation rules
## Edge Cases        ← table with EC-X-NN | scenario | expected
## API Contract      ← METHOD /api/endpoint
## Test Data         ← ### Valid / ### Invalid tables
```

The Spec Compiler reads these headings to build the JSON. Any heading not listed above is ignored.

---

## Security Payloads

This system uses **OWASP standard security vectors** for authorized testing:

- `payloads/xss.txt` — XSS injection attempts
- `payloads/sqli.txt` — SQL injection attempts
- `payloads/boundary.txt` — Boundary value strings

These test that your application handles malicious input safely — they verify that your app **does not** execute the payloads, showing logs them, shows an error, or ignores them gracefully.

**Use only on applications you own or have permission to test.**

---

*Built with Ollama + Playwright + pytest + GitHub Actions. Zero cloud cost.*
