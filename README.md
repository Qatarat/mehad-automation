# Markopolo Autonomous AI Testing

> Intent-based autonomous testing — describe the system, let AI handle the rest.

**No API keys. No Playwright scripts. No test maintenance. 100% free and open source.**

---

## How It Works

```
specs/*.md  →  AI reads & understands  →  Generates Playwright tests
            →  Executes against staging  →  Analyzes failures  →  Fixes & retries
            →  Detects coverage gaps     →  Publishes HTML report
```

Push a code change → GitHub Actions triggers → AI does everything automatically.

---

## AI Stack (all free, all local)

| Tool | Role | Cost |
|------|------|------|
| **Ollama** | Local AI inference engine | Free |
| **qwen2.5-coder:1.5b** | AI model — reads specs, generates test code | Free |
| **Playwright** | Browser automation | Free / Open source |
| **pytest** | Test execution framework | Free / Open source |
| **GitHub Actions** | CI/CD runner | Free tier (2000 min/month) |

No OpenAI. No Anthropic. No Gemini. No API keys. Everything runs locally.

---

## Local Setup

```bash
# 1. Install Ollama
brew install ollama          # macOS
# or: curl -fsSL https://ollama.ai/install.sh | sh   (Linux)

# 2. Pull the AI model
ollama pull qwen2.5-coder:1.5b    # 1GB  — fast, fits in CI
# or for better quality locally:
ollama pull qwen2.5-coder:7b      # 4GB  — recommended for local use
ollama pull llama3.2               # 2GB  — general reasoning

# 3. Install Python dependencies
pip install -r requirements.txt
playwright install chromium

# 4. Run the AI agent
BASE_URL=https://beta-stg.markopolo.ai python ai_engine/agent.py
```

---

## Project Structure

```
Markopolo-Automation-Testing/
├── specs/                    ← Test specifications (your input to the AI)
│   ├── login.md
│   ├── reset-password.md
│   └── signup.md
├── ai_engine/
│   ├── agent.py              ← Main AI orchestrator (ReAct loop)
│   └── reporter.py           ← HTML report generator
├── tests/                    ← AI-generated test files (runtime, gitignored)
├── reports/                  ← Results, gaps, HTML report (runtime, gitignored)
├── conftest.py               ← Playwright pytest config
├── requirements.txt
├── pytest.ini
└── .github/workflows/
    └── ai-tests.yml          ← Full CI/CD pipeline
```

---

## What the AI Agent Does

1. **THINK** — reads each `.md` spec, understands requirements, flows, and edge cases
2. **GENERATE** — writes complete Playwright Python test code (no templates, no hardcoded selectors)
3. **EXECUTE** — runs tests against the live staging environment
4. **REFLECT** — if tests fail, AI analyzes the failure output and rewrites the tests
5. **ITERATE** — retries until tests pass or max retries reached
6. **DETECT GAPS** — AI compares spec against tests and lists what was missed
7. **REPORT** — generates a full HTML report with per-page results and gap analysis

---

## CI/CD Triggers

| Event | What Happens |
|-------|-------------|
| Push to `specs/**` | Full AI test run triggered automatically |
| Push to `ai_engine/**` | Full AI test run triggered automatically |
| Pull Request to `main` | AI validates the changes |
| Every night at 2 AM UTC | Scheduled regression run |
| Manual (`workflow_dispatch`) | Run from GitHub Actions UI anytime |

---

## Model Recommendations

| Model | Size | Use Case |
|-------|------|----------|
| `qwen2.5-coder:1.5b` | 1GB | GitHub Actions CI (fits in 7GB runner RAM) |
| `qwen2.5-coder:7b` | 4GB | Local development — better code quality |
| `llama3.2` | 2GB | Better reasoning for complex edge cases |
| `deepseek-r1:8b` | 5GB | Best reasoning — use locally for deep analysis |

Change the model by setting `AI_MODEL` environment variable:
```bash
AI_MODEL=qwen2.5-coder:7b python ai_engine/agent.py
```

---

## Adding a New Page to Test

1. Create `specs/new-page.md` following the same structure as existing specs
2. Push to GitHub
3. AI automatically picks it up, generates tests, and runs them

That's it. No code changes needed.

---

## Viewing Reports

- **GitHub Actions** → click a workflow run → **Artifacts** → download `ai-test-reports-N`
- **Locally** → open `reports/report.html` in your browser after running the agent
