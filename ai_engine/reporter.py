"""
Generates a single consolidated HTML report from all test results.
Called by agent.py after all specs are processed.
"""

import json
from pathlib import Path
from datetime import datetime

REPORTS_DIR = Path("reports")


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Markopolo AI Test Report</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
          background: #0f0f0f; color: #e0e0e0; padding: 24px; }}
  h1 {{ font-size: 24px; font-weight: 700; margin-bottom: 4px; color: #fff; }}
  .meta {{ color: #888; font-size: 13px; margin-bottom: 32px; }}
  .summary-cards {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 32px; }}
  .card {{ background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 12px; padding: 20px; }}
  .card .label {{ font-size: 12px; color: #888; text-transform: uppercase; letter-spacing: 0.5px; }}
  .card .value {{ font-size: 36px; font-weight: 700; margin-top: 8px; }}
  .card.pass .value {{ color: #22c55e; }}
  .card.fail .value {{ color: #ef4444; }}
  .card.total .value {{ color: #60a5fa; }}
  .card.model .value {{ font-size: 14px; color: #a78bfa; margin-top: 12px; word-break: break-all; }}
  table {{ width: 100%; border-collapse: collapse; background: #1a1a1a;
           border: 1px solid #2a2a2a; border-radius: 12px; overflow: hidden; margin-bottom: 32px; }}
  th {{ background: #111; color: #888; font-size: 12px; text-transform: uppercase;
        letter-spacing: 0.5px; padding: 12px 16px; text-align: left; }}
  td {{ padding: 12px 16px; border-top: 1px solid #2a2a2a; font-size: 14px; }}
  .badge {{ display: inline-block; padding: 2px 10px; border-radius: 999px; font-size: 12px; font-weight: 600; }}
  .badge.pass {{ background: #14532d; color: #22c55e; }}
  .badge.fail {{ background: #450a0a; color: #ef4444; }}
  .badge.gen-fail {{ background: #3b1a08; color: #fb923c; }}
  .section-title {{ font-size: 16px; font-weight: 600; color: #fff; margin-bottom: 12px; }}
  .gaps-block {{ background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 12px;
                 padding: 20px; margin-bottom: 24px; white-space: pre-wrap; font-size: 13px;
                 color: #ccc; line-height: 1.7; }}
  .gaps-block h3 {{ color: #a78bfa; margin-bottom: 12px; }}
  footer {{ color: #444; font-size: 12px; text-align: center; margin-top: 48px; }}
</style>
</head>
<body>
<h1>🤖 Markopolo AI Test Report</h1>
<div class="meta">Generated: {timestamp} &nbsp;|&nbsp; Model: {model} &nbsp;|&nbsp; Target: {base_url}</div>

<div class="summary-cards">
  <div class="card pass"><div class="label">Passed</div><div class="value">{total_passed}</div></div>
  <div class="card fail"><div class="label">Failed</div><div class="value">{total_failed}</div></div>
  <div class="card total"><div class="label">Total Tests</div><div class="value">{total_tests}</div></div>
  <div class="card model"><div class="label">AI Model (Local)</div><div class="value">{model}</div></div>
</div>

<div class="section-title">Results by Page</div>
<table>
  <thead>
    <tr>
      <th>Page</th>
      <th>Status</th>
      <th>Passed</th>
      <th>Failed</th>
      <th>Total</th>
    </tr>
  </thead>
  <tbody>
    {rows}
  </tbody>
</table>

<div class="section-title">Coverage Gaps (AI Analysis)</div>
{gaps_blocks}

<footer>Markopolo Autonomous Testing · Zero API keys · Powered by Ollama + Playwright + pytest</footer>
</body>
</html>
"""

ROW_TEMPLATE = """
    <tr>
      <td><strong>{name}</strong></td>
      <td><span class="badge {badge_class}">{status_label}</span></td>
      <td>{passed}</td>
      <td>{failed}</td>
      <td>{total}</td>
    </tr>
"""

GAP_BLOCK_TEMPLATE = """
<div class="gaps-block">
  <h3>{name}</h3>
{gaps}
</div>
"""


def generate_report(all_results: dict, base_url: str, model: str) -> Path:
    total_p = sum(r.get("passed", 0) for r in all_results.values())
    total_f = sum(r.get("failed", 0) for r in all_results.values())
    total_t = sum(r.get("total",  0) for r in all_results.values())

    rows = ""
    for name, r in all_results.items():
        status = r.get("status", "unknown")
        if status == "generation_failed":
            badge, label = "gen-fail", "Gen Failed"
        elif r.get("failed", 1) == 0:
            badge, label = "pass", "PASSED"
        else:
            badge, label = "fail", "FAILED"

        rows += ROW_TEMPLATE.format(
            name=name,
            badge_class=badge,
            status_label=label,
            passed=r.get("passed", 0),
            failed=r.get("failed", 0),
            total=r.get("total", 0),
        )

    gaps_blocks = ""
    for name, r in all_results.items():
        gaps_text = r.get("gaps", "No gap analysis available.")
        gaps_blocks += GAP_BLOCK_TEMPLATE.format(
            name=name.replace("-", " ").title(),
            gaps=gaps_text,
        )

    html = HTML_TEMPLATE.format(
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        model=model,
        base_url=base_url,
        total_passed=total_p,
        total_failed=total_f,
        total_tests=total_t,
        rows=rows,
        gaps_blocks=gaps_blocks,
    )

    REPORTS_DIR.mkdir(exist_ok=True)
    out = REPORTS_DIR / "report.html"
    out.write_text(html)
    return out
