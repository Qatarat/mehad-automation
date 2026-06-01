"""
Generates a fully self-contained HTML QA report (Commit Report design).
All screenshots are embedded as base64 — one file, ready to share.
"""

import ast, json, os, re
from pathlib import Path
from datetime import datetime

REPORTS_DIR = Path("reports")

# ─────────────────────────────────────────────────────────────────────────────
# HTML escape helper (defined first so _PAGE builder functions can use it)
# ─────────────────────────────────────────────────────────────────────────────

def _esc(s) -> str:
    if not s:
        return ""
    s = str(s)
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;"))


# ─────────────────────────────────────────────────────────────────────────────
# HTML skeleton  — ALL CSS braces must be {{ }} except Python placeholders
# ─────────────────────────────────────────────────────────────────────────────

_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Mehad QA — Run #{run_num} · {run_date}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&family=Instrument+Serif:ital@0;1&display=swap" rel="stylesheet"/>
<style>
/* ── Design tokens ── */
:root{{
  --bg-0:#07080b;
  --bg-1:#0c0e13;
  --bg-2:#11141b;
  --bg-3:#181c26;
  --ink-0:#f6f7fa;
  --ink-1:#cdd1de;
  --ink-2:#9aa0b4;
  --ink-3:#626880;
  --ink-4:#3a4154;
  --accent:oklch(0.85 0.18 95);
  --ok:oklch(0.78 0.16 155);
  --bad:oklch(0.72 0.20 25);
  --warn:oklch(0.82 0.14 70);
  --accent-dim:oklch(0.85 0.18 95 / 0.15);
  --ok-dim:oklch(0.78 0.16 155 / 0.15);
  --bad-dim:oklch(0.72 0.20 25 / 0.15);
  --warn-dim:oklch(0.82 0.14 70 / 0.15);
  --radius:10px;
  --font:'Inter',system-ui,sans-serif;
  --mono:'JetBrains Mono',monospace;
  --serif:'Instrument Serif',Georgia,serif;
}}

/* ── Reset ── */
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
html{{scroll-behavior:smooth}}
body{{background:var(--bg-0);color:var(--ink-1);font-family:var(--font);font-size:14px;line-height:1.6}}
a{{color:var(--accent);text-decoration:none}}
a:hover{{text-decoration:underline}}
code,pre{{font-family:var(--mono);font-size:12px}}
pre{{background:var(--bg-1);border:1px solid var(--ink-4);border-radius:6px;
     padding:12px;overflow-x:auto;white-space:pre-wrap;word-break:break-word;color:var(--ink-1)}}

/* ── Nav ── */
.nav{{
  position:sticky;top:0;z-index:100;
  background:rgba(7,8,11,0.85);
  backdrop-filter:blur(12px);
  border-bottom:1px solid var(--ink-4);
  padding:0 24px;
  display:flex;align-items:center;gap:16px;height:52px;
}}
.mark{{
  width:28px;height:28px;border-radius:7px;flex-shrink:0;
  background:conic-gradient(from 135deg,oklch(0.85 0.18 95),oklch(0.78 0.16 155),oklch(0.72 0.20 25),oklch(0.85 0.18 95));
  display:flex;align-items:center;justify-content:center;
  font-weight:700;font-size:13px;color:#07080b;font-family:var(--mono);
}}
.crumbs{{font-size:13px;color:var(--ink-3);display:flex;align-items:center;gap:6px;flex:1}}
.crumbs a{{color:var(--ink-2);}}
.crumbs a:hover{{color:var(--ink-0)}}
.crumbs .sep{{color:var(--ink-4)}}
.crumbs .current{{color:var(--ink-0);font-weight:600}}
.btn{{
  border:1px solid var(--ink-4);background:var(--bg-2);color:var(--ink-1);
  padding:6px 14px;border-radius:7px;cursor:pointer;font-size:12px;font-weight:500;
  font-family:var(--font);transition:background .15s,border-color .15s;
}}
.btn:hover{{background:var(--bg-3);border-color:var(--ink-2)}}
.btn.primary{{background:var(--accent);color:#07080b;border-color:var(--accent);font-weight:700}}
.btn.primary:hover{{opacity:.9}}

/* ── Page wrap ── */
.wrap{{max-width:1200px;margin:0 auto;padding:28px 24px}}

/* ── Commit / run header section ── */
.commit{{
  background:linear-gradient(160deg,var(--bg-2) 0%,var(--bg-1) 100%);
  border:1px solid var(--ink-4);border-radius:14px;
  padding:28px 32px;margin-bottom:24px;
}}
.badge-row{{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:16px}}
.pill{{
  display:inline-flex;align-items:center;gap:6px;
  border-radius:99px;padding:4px 12px;font-size:12px;font-weight:600;
  border:1px solid var(--ink-4);background:var(--bg-3);color:var(--ink-2);
}}
.pill.run{{background:var(--accent-dim);border-color:var(--accent);color:var(--accent)}}
.pill.ok{{background:var(--ok-dim);border-color:var(--ok);color:var(--ok)}}
.pill.fail{{background:var(--bad-dim);border-color:var(--bad);color:var(--bad)}}
.commit h1{{
  font-size:clamp(20px,3vw,28px);font-weight:700;color:var(--ink-0);
  letter-spacing:-0.5px;margin-bottom:10px;
}}
.commit h1 em{{font-family:var(--serif);font-style:italic;color:var(--accent)}}
.commit-meta{{font-size:13px;color:var(--ink-2);display:flex;gap:20px;flex-wrap:wrap;margin-bottom:12px}}
.commit-meta b{{color:var(--ink-1)}}
.stamp{{
  display:inline-flex;align-items:center;gap:8px;
  font-size:12px;font-weight:700;letter-spacing:.5px;text-transform:uppercase;
  padding:5px 14px;border-radius:99px;
  border:1px solid var(--bad);color:var(--bad);background:var(--bad-dim);
}}
.stamp.pass-stamp{{border-color:var(--ok);color:var(--ok);background:var(--ok-dim)}}

/* ── Card ── */
.card{{
  background:var(--bg-1);border:1px solid var(--ink-4);
  border-radius:12px;margin-bottom:20px;overflow:hidden;
}}
.card-head{{
  padding:14px 20px;border-bottom:1px solid var(--ink-4);
  display:flex;align-items:center;justify-content:space-between;
}}
.card-head h4{{font-size:13px;font-weight:700;color:var(--ink-0);letter-spacing:.3px;text-transform:uppercase}}
.card-body{{padding:20px}}

/* ── Quality diff strip ── */
.diff-rows{{display:flex;flex-direction:column;gap:2px}}
.diff-row{{
  display:grid;grid-template-columns:20px 1fr auto;
  gap:10px;align-items:center;padding:10px 16px;
  border-radius:6px;font-size:13px;
}}
.diff-row .sym{{font-weight:700;font-family:var(--mono);font-size:13px}}
.diff-row .lbl{{color:var(--ink-1)}}
.diff-row .val{{font-weight:700;font-family:var(--mono);font-size:14px}}
.diff-row.add{{background:var(--bad-dim)}}
.diff-row.add .sym{{color:var(--bad)}}
.diff-row.add .val{{color:var(--bad)}}
.diff-row.up{{background:var(--ok-dim)}}
.diff-row.up .sym{{color:var(--ok)}}
.diff-row.up .val{{color:var(--ok)}}
.diff-row.neutral{{background:var(--bg-2)}}
.diff-row.neutral .sym{{color:var(--ink-3)}}
.diff-row.neutral .val{{color:var(--ink-2)}}

/* ── Two-column layout ── */
.layout{{display:grid;grid-template-columns:1fr 340px;gap:20px;align-items:start}}

/* ── Trace (spec waterfall) ── */
.trace-axis{{padding:14px 20px 6px;display:flex;justify-content:space-between;
            font-size:10px;color:var(--ink-4);text-transform:uppercase;letter-spacing:.5px}}
.trace-row{{
  display:grid;grid-template-columns:180px 1fr;
  gap:12px;align-items:center;padding:6px 16px;
}}
.trace-row:hover{{background:var(--bg-2)}}
.trace-row .nm{{font-size:12px;color:var(--ink-2);font-family:var(--mono);
               white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.trace-row .lane{{height:22px;background:var(--bg-3);border-radius:4px;overflow:hidden;position:relative}}
.trace-bar{{
  height:100%;border-radius:4px;display:flex;align-items:center;
  padding:0 8px;font-size:10px;font-weight:700;color:#07080b;
  white-space:nowrap;overflow:hidden;min-width:4%;
  transition:width .4s ease;
}}
.trace-bar.pass{{background:var(--ok)}}
.trace-bar.fail{{background:var(--bad)}}

/* ── Tests section ── */
.section h5{{
  font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.7px;
  color:var(--ink-3);padding:14px 20px 10px;border-bottom:1px solid var(--ink-4);
}}
.tests-tools{{
  padding:12px 16px;display:flex;gap:8px;align-items:center;flex-wrap:wrap;
  border-bottom:1px solid var(--ink-4);background:var(--bg-2);
}}
.chip{{
  padding:5px 12px;border-radius:99px;font-size:12px;font-weight:600;cursor:pointer;
  border:1px solid var(--ink-4);color:var(--ink-2);background:var(--bg-3);
  transition:all .15s;user-select:none;
}}
.chip:hover{{border-color:var(--ink-2);color:var(--ink-1)}}
.chip.active{{background:var(--bg-3);border-color:var(--ink-1);color:var(--ink-0)}}
.chip.fail.active{{background:var(--bad-dim);border-color:var(--bad);color:var(--bad)}}
.chip.pass.active{{background:var(--ok-dim);border-color:var(--ok);color:var(--ok)}}
#testSearch{{
  flex:1;min-width:160px;background:var(--bg-1);border:1px solid var(--ink-4);
  border-radius:99px;padding:5px 14px;font-size:12px;color:var(--ink-1);
  font-family:var(--font);outline:none;transition:border-color .15s;
}}
#testSearch:focus{{border-color:var(--accent)}}
#testSearch::placeholder{{color:var(--ink-4)}}

/* ── Group (spec accordion) ── */
.group{{border-bottom:1px solid var(--ink-4)}}
.group:last-child{{border-bottom:none}}
.group-head{{
  display:flex;align-items:center;gap:10px;padding:12px 16px;cursor:pointer;
  user-select:none;transition:background .12s;
}}
.group-head:hover{{background:var(--bg-2)}}
.group-head .chev{{font-size:10px;color:var(--ink-3);transition:transform .2s;width:12px;flex-shrink:0}}
.group.open .group-head .chev{{transform:rotate(90deg)}}
.group-head .gtag{{font-size:13px;font-weight:600;color:var(--ink-0);font-family:var(--mono);flex:1}}
.group-head .count{{font-size:11px;color:var(--ink-3);white-space:nowrap}}
.group-body{{display:none;background:var(--bg-0)}}
.group.open .group-body{{display:block}}

/* ── Individual test row ── */
.test{{border-bottom:1px solid var(--ink-4)}}
.test:last-child{{border-bottom:none}}
.test-row{{
  display:flex;align-items:center;gap:10px;padding:9px 28px;cursor:pointer;
  transition:background .12s;font-size:13px;
}}
.test:not(.open) .test-row:hover{{background:var(--bg-2)}}
.test.open .test-row{{background:var(--bg-2)}}
.test-row .chev{{font-size:9px;color:var(--ink-4);transition:transform .2s;width:10px;flex-shrink:0}}
.test.open .test-row .chev{{transform:rotate(90deg)}}
.statdot{{
  width:18px;height:18px;border-radius:50%;flex-shrink:0;
  display:flex;align-items:center;justify-content:center;
  font-size:9px;font-weight:800;
}}
.statdot.pass{{background:var(--ok-dim);color:var(--ok);border:1px solid var(--ok)}}
.statdot.fail{{background:var(--bad-dim);color:var(--bad);border:1px solid var(--bad)}}
.name-cell{{flex:1;min-width:0;overflow:hidden}}
.tname{{font-family:var(--mono);font-size:12px;color:var(--ink-1);
        white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.tag{{font-size:10px;font-weight:700;padding:2px 7px;border-radius:4px;flex-shrink:0}}
.tag.p0{{background:var(--bad-dim);color:var(--bad);border:1px solid var(--bad)}}
.tag.p1{{background:var(--warn-dim);color:var(--warn);border:1px solid var(--warn)}}
.tag.p2{{background:var(--ok-dim);color:var(--ok);border:1px solid var(--ok)}}
.tag.p3{{background:var(--accent-dim);color:var(--accent);border:1px solid var(--accent)}}

/* ── Test expanded body ── */
.test-body{{display:none;padding:14px 28px 18px 56px;background:var(--bg-0);border-top:1px solid var(--ink-4)}}
.test.open .test-body{{display:block}}
.pass-body{{display:none;padding:14px 28px 18px 56px;background:var(--bg-0);border-top:1px solid var(--ink-4)}}
.test.open .pass-body{{display:block}}
.pass-fields{{display:flex;flex-direction:column;gap:6px}}
.pass-fields dt{{font-size:11px;text-transform:uppercase;letter-spacing:.5px;color:var(--ink-3);font-weight:600;margin-top:6px}}
.pass-fields dd{{font-size:13px;color:var(--ink-1);font-family:var(--mono);padding-left:12px}}

/* ── Meta grid (inside test body) ── */
.meta-grid{{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:12px}}
.meta-cell{{background:var(--bg-2);border-radius:7px;padding:10px 12px}}
.meta-cell .k{{font-size:10px;text-transform:uppercase;letter-spacing:.5px;color:var(--ink-3);font-weight:600;margin-bottom:3px}}
.meta-cell .v{{font-size:13px;color:var(--ink-1);font-family:var(--mono)}}

/* ── Er grid (expected/actual) ── */
.er-grid{{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:12px 0}}
.er-card{{border-radius:8px;padding:12px 14px;border:1px solid}}
.er-card.ok{{background:var(--ok-dim);border-color:var(--ok)}}
.er-card.ok .k{{color:var(--ok)}}
.er-card.bad{{background:var(--bad-dim);border-color:var(--bad)}}
.er-card.bad .k{{color:var(--bad)}}
.er-card .k{{font-size:10px;text-transform:uppercase;letter-spacing:.5px;font-weight:700;margin-bottom:4px}}
.er-card .v{{font-size:12px;color:var(--ink-1)}}

/* ── Code box ── */
.codebox{{
  background:var(--bg-2);border:1px solid var(--ink-4);border-radius:7px;
  padding:12px;font-family:var(--mono);font-size:11px;color:var(--ink-2);
  overflow-x:auto;white-space:pre-wrap;word-break:break-word;margin-top:8px;
}}

/* ── Traceback toggle ── */
.trace-toggle{{
  width:100%;background:var(--bg-1);border:1px solid var(--ink-4);
  border-radius:6px;padding:8px 14px;color:var(--bad);font-family:var(--mono);
  font-size:11px;cursor:pointer;text-align:left;display:flex;
  justify-content:space-between;align-items:center;margin-top:12px;
  font-family:var(--font);
}}
.trace-toggle:hover{{background:var(--bg-2)}}
.trace-toggle .arr{{color:var(--ink-3);font-size:10px}}

/* ── Sidebar ── */
.side{{position:sticky;top:70px}}
.side-head{{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.7px;color:var(--ink-3);margin-bottom:10px}}
.ringwrap{{display:flex;align-items:center;justify-content:center;padding:20px 16px}}
.ring{{width:120px;height:120px}}

/* ── Mini-stats row ── */
.mini-stats{{display:grid;grid-template-columns:1fr 1fr;gap:8px;padding:0 16px 16px}}
.ms{{background:var(--bg-2);border-radius:8px;padding:10px 12px;border:1px solid var(--ink-4)}}
.ms .ms-v{{font-size:22px;font-weight:700;font-family:var(--mono);line-height:1}}
.ms .ms-l{{font-size:10px;color:var(--ink-3);text-transform:uppercase;letter-spacing:.5px;margin-top:3px}}
.ms.bad .ms-v{{color:var(--bad)}}
.ms.warn .ms-v{{color:var(--warn)}}
.ms.ok .ms-v{{color:var(--ok)}}

/* ── Run metadata DL ── */
.run-dl{{padding:14px 18px;display:flex;flex-direction:column;gap:0}}
.run-dl dt{{font-size:10px;text-transform:uppercase;letter-spacing:.5px;color:var(--ink-3);
           font-weight:600;margin-top:10px}}
.run-dl dt:first-child{{margin-top:0}}
.run-dl dd{{font-size:13px;color:var(--ink-1);font-family:var(--mono)}}

/* ── Bug cards ── */
.bug-card{{
  background:var(--bg-1);border:1px solid var(--ink-4);
  border-radius:12px;margin-bottom:20px;overflow:hidden;
}}
.bug-card-hdr{{
  padding:16px 20px;display:flex;align-items:flex-start;
  justify-content:space-between;flex-wrap:wrap;gap:8px;
  border-bottom:1px solid var(--ink-4);background:var(--bg-2);
}}
.bug-card-hdr .left{{display:flex;align-items:center;gap:10px;flex-wrap:wrap}}
.bug-id{{
  font-size:11px;font-weight:700;color:var(--ink-3);
  font-family:var(--mono);background:var(--bg-0);
  border:1px solid var(--ink-4);padding:2px 8px;border-radius:4px;
}}
.bug-title{{font-size:15px;font-weight:600;color:var(--ink-0);margin-top:4px}}
.bug-meta{{font-size:12px;color:var(--ink-3);display:flex;gap:16px;flex-wrap:wrap;margin-top:6px}}
.bug-meta span{{display:flex;align-items:center;gap:4px}}
.bug-body{{padding:20px}}

/* ── Badge / severity ── */
.badge{{
  display:inline-block;padding:3px 10px;border-radius:99px;font-size:11px;
  font-weight:700;letter-spacing:.4px;text-transform:uppercase;
}}
.badge.CRITICAL{{background:var(--bad-dim);color:var(--bad);border:1px solid var(--bad)}}
.badge.HIGH{{background:var(--warn-dim);color:var(--warn);border:1px solid var(--warn)}}
.badge.MEDIUM{{background:var(--accent-dim);color:var(--accent);border:1px solid var(--accent)}}
.badge.LOW{{background:var(--ok-dim);color:var(--ok);border:1px solid var(--ok)}}
.badge.PASS{{background:var(--ok-dim);color:var(--ok);border:1px solid var(--ok)}}
.badge.FAIL{{background:var(--bad-dim);color:var(--bad);border:1px solid var(--bad)}}
.badge.gen-fail{{background:var(--warn-dim);color:var(--warn);border:1px solid var(--warn)}}
.badge.P0{{background:var(--bad-dim);color:var(--bad);border:1px solid var(--bad)}}
.badge.P1{{background:var(--warn-dim);color:var(--warn);border:1px solid var(--warn)}}
.badge.P2{{background:var(--ok-dim);color:var(--ok);border:1px solid var(--ok)}}
.badge.P3{{background:var(--accent-dim);color:var(--accent);border:1px solid var(--accent)}}

/* ── Info blocks ── */
.info-block{{border-radius:8px;padding:14px 16px;margin-bottom:12px}}
.info-block .ib-label{{font-size:11px;font-weight:700;text-transform:uppercase;
                       letter-spacing:.6px;margin-bottom:8px}}
.info-block.expected{{background:var(--ok-dim);border-left:3px solid var(--ok)}}
.info-block.expected .ib-label{{color:var(--ok)}}
.info-block.actual{{background:var(--bad-dim);border-left:3px solid var(--bad)}}
.info-block.actual .ib-label{{color:var(--bad)}}
.info-block.analysis{{background:var(--bg-3);border-left:3px solid var(--accent)}}
.info-block.analysis .ib-label{{color:var(--accent)}}
.info-block.fix{{background:var(--ok-dim);border-left:3px solid var(--ok)}}
.info-block.fix .ib-label{{color:var(--ok)}}
.info-block.rootcause{{background:var(--warn-dim);border-left:3px solid var(--warn)}}
.info-block.rootcause .ib-label{{color:var(--warn)}}
.info-block.priority{{background:var(--bg-3);border-left:3px solid var(--accent)}}
.info-block.priority .ib-label{{color:var(--accent)}}

/* ── Two-col for info blocks ── */
.two-col{{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px}}
@media(max-width:640px){{.two-col{{grid-template-columns:1fr}}}}

/* ── Steps ── */
ol.steps{{padding-left:20px;color:var(--ink-1)}}
ol.steps li{{margin-bottom:5px}}

/* ── Screenshot ── */
.shot-wrap{{margin-top:16px}}
.shot-label{{font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.6px;
            color:var(--ink-3);margin-bottom:8px;display:flex;align-items:center;gap:6px}}
.screenshot{{width:100%;border:1px solid var(--ink-4);border-radius:8px;cursor:zoom-in;transition:opacity .2s}}
.screenshot:hover{{opacity:.9}}
.no-shot{{background:var(--bg-2);border:1px dashed var(--ink-4);border-radius:8px;
         padding:20px;text-align:center;color:var(--ink-3);font-size:12px}}

/* ── Video ── */
.video-wrap{{margin-top:16px}}
.video-label{{font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.6px;
             color:var(--ink-3);margin-bottom:8px;display:flex;align-items:center;gap:6px}}
.poc-video{{width:100%;max-height:540px;border:1px solid var(--ink-4);border-radius:8px;background:#000}}

/* ── Error toggle ── */
.err-toggle{{
  width:100%;background:var(--bg-2);border:1px solid var(--ink-4);
  border-radius:6px;padding:10px 14px;color:var(--bad);font-size:12px;
  cursor:pointer;text-align:left;display:flex;justify-content:space-between;
  align-items:center;margin-top:14px;font-family:var(--font);
}}
.err-toggle:hover{{background:var(--bg-3)}}
.err-body{{display:none;margin-top:1px}}
.err-body.open{{display:block}}

/* ── Evidence panels ── */
.ev-toggle{{
  width:100%;background:var(--bg-2);border:1px solid var(--ink-4);border-radius:6px;
  padding:9px 14px;color:var(--accent);font-size:12px;cursor:pointer;
  text-align:left;display:flex;justify-content:space-between;align-items:center;
  margin-top:10px;font-family:var(--font);
}}
.ev-toggle:hover{{background:var(--bg-3)}}
.ev-body{{display:none;margin-top:1px}}
.ev-body.open{{display:block}}
.ev-table{{width:100%;border-collapse:collapse;font-size:11px;margin-top:4px}}
.ev-table th{{background:var(--bg-0);color:var(--ink-3);padding:5px 10px;text-align:left;font-weight:600;border:1px solid var(--ink-4)}}
.ev-table td{{padding:4px 10px;border:1px solid var(--ink-4);color:var(--ink-1);word-break:break-all;max-width:400px}}
.perf-grid{{display:flex;gap:16px;flex-wrap:wrap;margin-top:4px}}
.perf-stat{{background:var(--bg-2);border:1px solid var(--ink-4);border-radius:6px;padding:10px 16px;min-width:120px;text-align:center}}
.perf-stat .pval{{font-size:22px;font-weight:700;color:var(--accent)}}
.perf-stat .plbl{{font-size:10px;color:var(--ink-3);text-transform:uppercase;letter-spacing:.5px;margin-top:4px}}
.pval.warn{{color:var(--warn)}}
.pval.bad{{color:var(--bad)}}

/* ── Console ── */
.console-err{{background:var(--bad-dim);border-left:3px solid var(--bad);padding:6px 10px;border-radius:4px;margin-bottom:4px;font-size:11px;font-family:var(--mono);color:var(--bad)}}
.console-warn{{background:var(--warn-dim);border-left:3px solid var(--warn);padding:6px 10px;border-radius:4px;margin-bottom:4px;font-size:11px;font-family:var(--mono);color:var(--warn)}}

/* ── Env strip ── */
.env-strip{{font-size:11px;color:var(--ink-3);display:flex;gap:16px;flex-wrap:wrap;
           margin-top:14px;padding-top:14px;border-top:1px solid var(--ink-4)}}
.env-strip b{{color:var(--ink-1)}}

/* ── Board/SLA chips ── */
.board-chip{{font-size:10px;font-weight:700;letter-spacing:.4px;padding:2px 8px;
           border-radius:4px;text-transform:uppercase;display:inline-block}}
.board-chip.expedite{{background:var(--bad-dim);color:var(--bad);border:1px solid var(--bad)}}
.board-chip.else{{background:var(--accent-dim);color:var(--accent);border:1px solid var(--accent)}}
.biz-badge{{font-size:10px;font-weight:700;letter-spacing:.4px;padding:2px 8px;
          border-radius:4px;background:var(--warn-dim);color:var(--warn);
          border:1px solid var(--warn);display:inline-block;animation:biz-pulse 2s ease-in-out infinite}}
@keyframes biz-pulse{{0%,100%{{opacity:1}} 50%{{opacity:.7}}}}
.sla-chip{{font-size:10px;color:var(--ink-3);background:var(--bg-2);
         border:1px solid var(--ink-4);border-radius:4px;padding:2px 8px;display:inline-block}}

/* ── Cluster summary ── */
.cluster-summary{{margin:0 0 20px}}
.cluster-headline{{font-size:14px;color:var(--ink-2);margin-bottom:14px}}
.cluster-headline strong{{color:var(--accent)}}
.cluster-list{{display:flex;flex-direction:column;gap:8px}}
.cluster-row{{background:var(--bg-2);border:1px solid var(--ink-4);border-radius:8px;
             padding:14px 18px;display:grid;grid-template-columns:auto 1fr auto;
             gap:14px;align-items:center}}
.cluster-row:hover{{border-color:var(--accent)}}
.cluster-meta{{display:flex;gap:6px;align-items:center;flex-wrap:wrap}}
.cluster-count{{font-size:11px;color:var(--ink-3);background:var(--bg-0);
               border:1px solid var(--ink-4);border-radius:4px;padding:3px 8px;font-weight:600}}
.cluster-title{{font-size:13px;color:var(--ink-0);font-weight:600}}
.cluster-tickets{{display:flex;gap:6px;flex-wrap:wrap;justify-content:flex-end;max-width:300px}}
.cluster-bug-link{{font-size:10px;font-family:var(--mono);color:var(--accent);
                  text-decoration:none;background:var(--bg-0);border:1px solid var(--ink-4);
                  padding:2px 6px;border-radius:4px}}
.cluster-bug-link:hover{{border-color:var(--accent);background:var(--accent-dim)}}
.recurrence-badge{{background:var(--bad-dim);color:var(--bad);border:1px solid var(--bad);
                  border-radius:4px;padding:2px 8px;font-size:10px;
                  font-weight:700;text-transform:uppercase;letter-spacing:.4px}}
.cluster-help{{font-size:11px;color:var(--ink-3);margin-top:12px;
              padding:8px 12px;background:var(--bg-2);border-radius:6px;
              border-left:3px solid var(--accent)}}

/* ── Gap block ── */
.gap-block{{background:var(--bg-2);border:1px solid var(--ink-4);
           border-radius:var(--radius);padding:20px;margin-bottom:16px}}
.gap-block h3{{color:var(--accent);font-size:14px;margin-bottom:12px}}
.gap-block p,.gap-block li{{color:var(--ink-2);font-size:13px;margin-bottom:4px}}

/* ── Priority strip ── */
.priority-strip{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:20px}}
.pstrip-item{{background:var(--bg-2);border:1px solid var(--ink-4);border-radius:var(--radius);
             padding:14px 16px;text-align:center;transition:transform .12s,border-color .12s}}
.pstrip-item:hover{{transform:translateY(-2px)}}
.pstrip-label{{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.6px;margin-bottom:6px}}
.pstrip-val{{font-size:28px;font-weight:700;line-height:1;margin-bottom:4px}}
.pstrip-sla{{font-size:10px;color:var(--ink-3);margin-top:4px}}
.pstrip-item.p0{{border-top:3px solid var(--bad)}}
.pstrip-item.p0 .pstrip-label,.pstrip-item.p0 .pstrip-val{{color:var(--bad)}}
.pstrip-item.p1{{border-top:3px solid var(--warn)}}
.pstrip-item.p1 .pstrip-label,.pstrip-item.p1 .pstrip-val{{color:var(--warn)}}
.pstrip-item.p2{{border-top:3px solid var(--ok)}}
.pstrip-item.p2 .pstrip-label,.pstrip-item.p2 .pstrip-val{{color:var(--ok)}}
.pstrip-item.p3{{border-top:3px solid var(--accent)}}
.pstrip-item.p3 .pstrip-label,.pstrip-item.p3 .pstrip-val{{color:var(--accent)}}

/* ── Brand footer ── */
.brand-foot{{
  margin-top:48px;padding:36px 24px;border-top:1px solid var(--ink-4);
  display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:32px;
}}
.brand-foot .who{{display:flex;flex-direction:column;gap:6px}}
.brand-foot .who .logo-row{{display:flex;align-items:center;gap:10px;margin-bottom:4px}}
.brand-foot .who .bname{{font-weight:700;font-size:15px;color:var(--ink-0)}}
.brand-foot .who .btitle{{font-size:12px;color:var(--ink-3)}}
.brand-foot .links{{display:flex;flex-direction:column;gap:8px}}
.brand-foot .links a{{font-size:13px;color:var(--ink-2)}}
.brand-foot .links a:hover{{color:var(--ink-0)}}
.brand-foot .col-head{{font-size:11px;font-weight:700;text-transform:uppercase;
                       letter-spacing:.6px;color:var(--ink-3);margin-bottom:12px}}

/* ── Lightbox ── */
#lb{{display:none;position:fixed;inset:0;background:rgba(0,0,0,.92);
    z-index:1000;cursor:zoom-out;justify-content:center;align-items:center}}
#lb.show{{display:flex}}
#lb img{{max-width:95vw;max-height:92vh;border-radius:10px;border:1px solid var(--ink-4)}}

/* ── Section heading h5 in cards ── */
.sec-title{{font-size:15px;font-weight:700;color:var(--ink-0);
           border-bottom:1px solid var(--ink-4);padding-bottom:12px;margin:0 0 18px}}
.sec-title .count{{background:var(--bg-3);color:var(--ink-3);font-size:11px;
                  padding:2px 8px;border-radius:99px;margin-left:8px;font-weight:400}}

/* ── Responsive breakpoints ── */
@media(max-width:1100px){{
  .layout{{grid-template-columns:1fr}}
  .side{{position:static}}
  .brand-foot{{grid-template-columns:1fr 1fr}}
}}
@media(max-width:880px){{
  .commit{{padding:20px}}
  .trace-row{{grid-template-columns:120px 1fr}}
  .priority-strip{{grid-template-columns:repeat(2,1fr)}}
}}
@media(max-width:680px){{
  .wrap{{padding:16px 12px}}
  .brand-foot{{grid-template-columns:1fr}}
  .commit h1{{font-size:20px}}
  .commit-meta{{gap:10px}}
  .meta-grid{{grid-template-columns:1fr}}
  .er-grid{{grid-template-columns:1fr}}
  .two-col{{grid-template-columns:1fr}}
  .mini-stats{{grid-template-columns:1fr 1fr}}
  .cluster-row{{grid-template-columns:1fr;gap:8px}}
  .cluster-tickets{{justify-content:flex-start;max-width:100%}}
  .priority-strip{{grid-template-columns:1fr 1fr}}
  .perf-grid{{flex-wrap:wrap}}
}}
@media print{{
  .nav{{display:none}}
  body{{background:#fff;color:#000}}
  .bug-card,.card{{border:1px solid #ccc;break-inside:avoid}}
}}
</style>
</head>
<body>

<!-- Nav -->
<nav class="nav">
  <div class="mark">M</div>
  <div class="crumbs">
    <a href="index.html">Mehad QA</a>
    <span class="sep">/</span>
    <span class="current">Run #{run_num}</span>
  </div>
  <button class="btn primary" onclick="window.print()">Export PDF</button>
</nav>

<!-- Lightbox -->
<div id="lb" onclick="this.classList.remove('show')">
  <img id="lb-img" src="" alt="Screenshot"/>
</div>

<div class="wrap">

<!-- ── Run header ── -->
<section class="commit">
  <div class="badge-row">
    <span class="pill run">Run #{run_num}</span>
    <span class="pill">{base_url_short}</span>
    <span class="pill {verdict_pill_cls}">{verdict_pill}</span>
  </div>
  <h1>{run_summary_title}</h1>
  <div class="commit-meta">
    <span><b>Date:</b> {run_date}</span>
    <span><b>Model:</b> {model}</span>
    <span><b>Specs:</b> {total_specs}</span>
    <span><b>Tests:</b> {total_tests}</span>
  </div>
  <p style="font-size:13px;color:var(--ink-2);margin-bottom:16px">{run_description}</p>
  <span class="stamp {stamp_cls}">{verdict_label}</span>
</section>

<!-- ── Quality overview ── -->
<section class="card">
  <div class="card-head">
    <h4>Quality Overview</h4>
    <span style="font-size:12px;color:var(--ink-3)">{total_passed}/{total_tests} passing</span>
  </div>
  <div class="card-body">
    <div class="diff-rows">
      <div class="diff-row {pass_rate_cls}">
        <span class="sym">{pass_rate_sym}</span>
        <span class="lbl">Pass rate</span>
        <span class="val">{pass_rate}%</span>
      </div>
      <div class="diff-row {fail_cls}">
        <span class="sym">{fail_sym}</span>
        <span class="lbl">Failing tests</span>
        <span class="val">{total_failed}</span>
      </div>
      <div class="diff-row {p0_cls}">
        <span class="sym">{p0_sym}</span>
        <span class="lbl">P0 critical bugs</span>
        <span class="val">{p0_label}</span>
      </div>
      <div class="diff-row {p1_cls}">
        <span class="sym">{p1_sym}</span>
        <span class="lbl">P1 high bugs</span>
        <span class="val">{p1_label}</span>
      </div>
    </div>
  </div>
</section>

<!-- ── Priority strip ── -->
<div class="priority-strip">
  <div class="pstrip-item p0">
    <div class="pstrip-label">P0 Highest</div>
    <div class="pstrip-val">{cnt_p0}</div>
    <div class="pstrip-sla">24h SLA · Expedite</div>
  </div>
  <div class="pstrip-item p1">
    <div class="pstrip-label">P1 High</div>
    <div class="pstrip-val">{cnt_p1}</div>
    <div class="pstrip-sla">2–3 days · Expedite</div>
  </div>
  <div class="pstrip-item p2">
    <div class="pstrip-label">P2 Medium</div>
    <div class="pstrip-val">{cnt_p2}</div>
    <div class="pstrip-sla">Current sprint</div>
  </div>
  <div class="pstrip-item p3">
    <div class="pstrip-label">P3 Low</div>
    <div class="pstrip-val">{cnt_p3}</div>
    <div class="pstrip-sla">Backlog</div>
  </div>
</div>

<!-- ── Two-column layout ── -->
<div class="layout">

<main>

<!-- ── Spec trace waterfall ── -->
<section class="card">
  <div class="card-head"><h4>Spec Trace</h4><span style="font-size:12px;color:var(--ink-3)">{passed_specs}/{total_specs} specs clean</span></div>
  <div class="trace-axis"><span>Spec</span><span>Tests run</span></div>
  {spec_trace_rows}
</section>

<!-- ── All tests ── -->
<section class="card">
  <div class="card-head"><h4>All Tests</h4><span style="font-size:12px;color:var(--ink-3)">{total_tests} total</span></div>
  <div class="tests-tools">
    <span class="chip active" data-tf="all">All ({total_tests})</span>
    <span class="chip fail" data-tf="failed">Failed ({total_failed})</span>
    <span class="chip pass" data-tf="passed">Passed ({total_passed})</span>
    <span class="chip" data-tf="p0">P0</span>
    <span class="chip" data-tf="p1">P1</span>
    <input id="testSearch" type="text" placeholder="Search tests…"/>
  </div>
  <div id="tests-body">
    {tests_body_html}
  </div>
</section>

<!-- ── Bug tickets ── -->
{bug_section_html}

<!-- ── Coverage gaps ── -->
{gaps_section_html}

<!-- ── Extra section (cross-spec etc.) ── -->
{extra_section_html}

</main>

<!-- ── Sidebar ── -->
<aside class="side">
  <!-- Ring gauge -->
  <div class="card" style="margin-bottom:16px">
    <div style="padding:14px 18px 0;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.7px;color:var(--ink-3)">Pass Rate</div>
    <div class="ringwrap">
      <svg class="ring" viewBox="0 0 44 44">
        <circle cx="22" cy="22" r="18" fill="none" stroke="var(--bg-3)" stroke-width="5"/>
        <circle cx="22" cy="22" r="18" fill="none" stroke="{ring_color}" stroke-width="5"
          stroke-dasharray="113.1" stroke-dashoffset="{ring_offset}"
          stroke-linecap="round" transform="rotate(-90 22 22)"/>
        <text x="22" y="25" text-anchor="middle" font-size="8" font-weight="700"
          fill="{ring_color}" font-family="'JetBrains Mono',monospace">{pass_rate}%</text>
      </svg>
    </div>
    <div class="mini-stats">
      <div class="ms {p0_ms_cls}">
        <div class="ms-v">{cnt_p0}</div>
        <div class="ms-l">P0 bugs</div>
      </div>
      <div class="ms {p1_ms_cls}">
        <div class="ms-v">{cnt_p1}</div>
        <div class="ms-l">P1 bugs</div>
      </div>
      <div class="ms {p2_ms_cls}">
        <div class="ms-v">{cnt_p2}</div>
        <div class="ms-l">P2 bugs</div>
      </div>
      <div class="ms">
        <div class="ms-v">{cnt_p3}</div>
        <div class="ms-l">P3 bugs</div>
      </div>
    </div>
  </div>
  <!-- Run metadata -->
  <div class="card" style="margin-bottom:16px">
    <div class="card-head"><h4>Run Info</h4></div>
    <dl class="run-dl">
      <dt>Run #</dt><dd>{run_num}</dd>
      <dt>Date</dt><dd>{run_date}</dd>
      <dt>Target URL</dt><dd style="word-break:break-all">{base_url}</dd>
      <dt>AI Model</dt><dd>{model}</dd>
      <dt>Browser</dt><dd>Chromium (headless)</dd>
    </dl>
  </div>
  <!-- Priority breakdown -->
  <div class="card">
    <div class="card-head"><h4>Priority Breakdown</h4></div>
    <dl class="run-dl">
      <dt>Critical (P0)</dt><dd style="color:var(--bad)">{cnt_p0} · 24h SLA</dd>
      <dt>High (P1)</dt><dd style="color:var(--warn)">{cnt_p1} · 2–3 days</dd>
      <dt>Medium (P2)</dt><dd style="color:var(--ok)">{cnt_p2} · current sprint</dd>
      <dt>Low (P3)</dt><dd style="color:var(--accent)">{cnt_p3} · backlog</dd>
      <dt>Severity: Critical</dt><dd style="color:var(--bad)">{cnt_critical}</dd>
      <dt>Severity: High</dt><dd style="color:var(--warn)">{cnt_high}</dd>
      <dt>Severity: Medium</dt><dd style="color:var(--accent)">{cnt_medium}</dd>
      <dt>Severity: Low</dt><dd style="color:var(--ok)">{cnt_low}</dd>
    </dl>
  </div>
</aside>

</div><!-- /layout -->

<!-- ── Footer ── -->
<footer class="brand-foot">
  <div class="who">
    <div class="logo-row">
      <div class="mark">M</div>
      <span class="bname">Mehad QA</span>
    </div>
    <span class="btitle">AI-driven spec validation · autonomous · intent-based</span>
    <span style="font-size:12px;color:var(--ink-3);margin-top:8px">Built by Mejbaur Bahar Fagun</span>
    <span style="font-size:12px;color:var(--ink-3)">Senior Software Engineer QA (IV) · Markopolo.ai</span>
  </div>
  <div>
    <div class="col-head">Links</div>
    <div class="links">
      <a href="https://www.linkedin.com/in/mejbaur/" target="_blank" rel="noopener">LinkedIn</a>
      <a href="{base_url}" target="_blank" rel="noopener">Target App</a>
    </div>
  </div>
  <div>
    <div class="col-head">Report</div>
    <div class="links">
      <a href="#" onclick="window.print();return false">Export PDF</a>
    </div>
  </div>
  <div>
    <div class="col-head">Run #{run_num}</div>
    <div style="font-size:12px;color:var(--ink-3);line-height:1.8">
      {run_date}<br/>
      {total_tests} tests<br/>
      {total_specs} specs<br/>
      {pass_rate}% pass rate
    </div>
  </div>
</footer>

</div><!-- /wrap -->

<script>
(function(){{
  // Group toggle
  document.querySelectorAll('.group-head').forEach(function(gh){{
    gh.addEventListener('click', function(){{
      gh.closest('.group').classList.toggle('open');
    }});
  }});
  // Test row toggle
  document.querySelectorAll('.test-row').forEach(function(tr){{
    tr.addEventListener('click', function(){{
      tr.closest('.test').classList.toggle('open');
    }});
  }});
  // Chip filter
  var chips = document.querySelectorAll('[data-tf]');
  var searchEl = document.getElementById('testSearch');
  var currentMode = 'all';
  chips.forEach(function(chip){{
    chip.addEventListener('click', function(){{
      chips.forEach(function(c){{c.classList.remove('active')}});
      chip.classList.add('active');
      currentMode = chip.dataset.tf;
      doFilter();
    }});
  }});
  if(searchEl) searchEl.addEventListener('input', doFilter);
  function doFilter(){{
    var q = searchEl ? searchEl.value.toLowerCase().trim() : '';
    document.querySelectorAll('.test').forEach(function(t){{
      var out = t.dataset.outcome || '';
      var pri = (t.dataset.pri || '').toLowerCase();
      var nm = (t.querySelector('.tname')||{{}}).textContent||'';
      var mOk = currentMode==='all'||
        (currentMode==='failed'&&out==='fail')||
        (currentMode==='passed'&&out==='pass')||
        (currentMode==='p0'&&pri==='p0')||
        (currentMode==='p1'&&pri==='p1');
      var qOk = !q||nm.toLowerCase().includes(q);
      t.style.display=(mOk&&qOk)?'':'none';
    }});
    document.querySelectorAll('.group').forEach(function(g){{
      var vis=Array.from(g.querySelectorAll('.test')).some(function(t){{return t.style.display!=='none'}});
      g.style.display=vis?'':'none';
    }});
  }}
  // Traceback toggles
  document.querySelectorAll('.trace-toggle').forEach(function(btn){{
    btn.addEventListener('click',function(){{
      var wrap=btn.nextElementSibling;
      if(wrap){{wrap.style.display=wrap.style.display==='block'?'none':'block'}}
      btn.querySelector('.arr').textContent=btn.nextElementSibling&&btn.nextElementSibling.style.display==='block'?'▼':'▶';
    }});
  }});
  // Error toggle
  function toggleErr(id){{
    var el=document.getElementById(id);
    var btn=el.previousElementSibling;
    if(el.classList.contains('open')){{el.classList.remove('open');btn.querySelector('span').textContent='▶ Show error details';}}
    else{{el.classList.add('open');btn.querySelector('span').textContent='▼ Hide error details';}}
  }}
  window.toggleErr = toggleErr;
  // Evidence toggle
  function toggleEv(id){{
    var el=document.getElementById(id);
    var btn=el.previousElementSibling;
    var arrow=btn.querySelectorAll('span')[1];
    if(el.classList.contains('open')){{el.classList.remove('open');if(arrow)arrow.textContent='▶ Show';}}
    else{{el.classList.add('open');if(arrow)arrow.textContent='▼ Hide';}}
  }}
  window.toggleEv = toggleEv;
  // Bug filter
  function applyBugFilter(sev){{
    document.querySelectorAll('.bug-card').forEach(function(c){{
      if(sev==='all'){{c.style.display='';return;}}
      var match;
      if(/^P[0-3]$/.test(sev)){{match=c.dataset.priority===sev;}}
      else{{match=c.querySelector('.badge.'+sev)!==null;}}
      c.style.display=match?'':'none';
    }});
  }}
  window.applyBugFilter = applyBugFilter;
  // Lightbox
  document.addEventListener('click',function(e){{
    if(e.target.matches('.poc img,.screenshot')){{
      document.getElementById('lb-img').src=e.target.src;
      document.getElementById('lb').classList.add('show');
    }}
  }});
  document.addEventListener('keydown',function(e){{
    if(e.key==='Escape') document.getElementById('lb').classList.remove('show');
  }});
}})();
</script>
</body>
</html>"""


# ─────────────────────────────────────────────────────────────────────────────
# Helper: parse test source for docstrings
# ─────────────────────────────────────────────────────────────────────────────

def _parse_test_file(path: Path) -> dict:
    """Return {fn_name: {title, docstring, test_data}} by AST-parsing the generated test file."""
    info = {}
    if not path.exists():
        return info
    try:
        source = path.read_text(encoding="utf-8")
        tree   = ast.parse(source)
        lines  = source.splitlines()
        for node in ast.walk(tree):
            if not (isinstance(node, ast.FunctionDef) and node.name.startswith("test_")):
                continue
            doc  = ast.get_docstring(node) or ""
            data = ""
            for ln in range(node.lineno, min(node.lineno + 8, len(lines))):
                if "# TEST_DATA:" in lines[ln]:
                    data = lines[ln].split("# TEST_DATA:", 1)[-1].strip()
                    break
            raw_title = node.name[5:]
            title = raw_title.replace("_", " ").title()
            info[node.name] = {"title": title, "docstring": doc, "test_data": data}
    except Exception:
        pass
    return info


def _load_pytest_outcomes(json_report_path) -> dict:
    """Return {fn_name: outcome} from a pytest JSON report file."""
    outcomes = {}
    if not json_report_path:
        return outcomes
    p = Path(json_report_path)
    if not p.exists():
        return outcomes
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        for t in data.get("tests", []):
            nodeid  = t.get("nodeid", "")
            fn_name = nodeid.split("::")[-1].split("[")[0]
            outcomes[fn_name] = t.get("outcome", "unknown")
    except Exception:
        pass
    return outcomes


# ─────────────────────────────────────────────────────────────────────────────
# Spec trace waterfall
# ─────────────────────────────────────────────────────────────────────────────

def _build_spec_trace(all_results: dict) -> str:
    if not all_results:
        return ""
    max_total = max((r.get("total", 0) for r in all_results.values()), default=1) or 1
    rows = []
    for name, r in all_results.items():
        total  = r.get("total", 0)
        failed = r.get("failed", 0)
        bar_pct = max(4, round(total / max_total * 100))
        bar_cls = "trace-bar pass" if failed == 0 else "trace-bar fail"
        count_text = str(total) if bar_pct >= 20 else ""
        rows.append(
            f'<div class="trace-row">'
            f'<span class="nm" title="{_esc(name)}">{_esc(name)}</span>'
            f'<div class="lane">'
            f'<div class="{bar_cls}" style="width:{bar_pct}%">{_esc(count_text)}</div>'
            f'</div>'
            f'</div>'
        )
    return "\n".join(rows)


# ─────────────────────────────────────────────────────────────────────────────
# Tests body (grouped by spec)
# ─────────────────────────────────────────────────────────────────────────────

def _build_tests_body(all_results: dict) -> str:
    if not all_results:
        return '<p style="color:var(--ink-3);padding:20px">No test data available.</p>'

    groups = []
    for spec_name, r in all_results.items():
        bug_recs: list = r.get("bugs", []) or []
        passed_recs: list = r.get("passed_tests", []) or []

        # Legacy fallback: if no passed_tests, derive from pytest outcomes
        if not passed_recs:
            json_report = r.get("json_report")
            outcomes    = _load_pytest_outcomes(json_report) if json_report else {}
            tests_dir   = Path("tests")
            test_file   = tests_dir / f"test_{spec_name.replace('-', '_')}.py"
            test_info   = _parse_test_file(test_file) if test_file.exists() else {}
            bug_names   = {b.get("test_name", "") for b in bug_recs}
            for fn, info in test_info.items():
                if outcomes.get(fn, "unknown") == "passed" and fn not in bug_names:
                    passed_recs.append({
                        "name":      fn,
                        "docstring": info.get("docstring", ""),
                        "params":    info.get("test_data", ""),
                        "duration":  0.0,
                    })

        n_pass = len(passed_recs)
        n_fail = len(bug_recs)
        count_str = f"{n_pass} pass · {n_fail} fail"

        test_rows = []

        # Failed tests
        for bug in bug_recs:
            pri   = bug.get("priority", "P2").lower()
            tname = _esc(bug.get("test_name", "unknown"))
            desc  = _esc(bug.get("description", ""))
            exp   = _esc(bug.get("expected", ""))
            act   = _esc(bug.get("actual", ""))
            tb    = _esc(bug.get("traceback", ""))
            err   = _esc(bug.get("error_message", ""))
            bug_id = _esc(bug.get("id", ""))
            url   = _esc(bug.get("page_url", ""))
            ts    = _esc(bug.get("timestamp", "")[:19].replace("T", " "))

            meta_grid = (
                f'<div class="meta-grid">'
                f'<div class="meta-cell"><div class="k">URL</div><div class="v" style="word-break:break-all">{url or "—"}</div></div>'
                f'<div class="meta-cell"><div class="k">Timestamp</div><div class="v">{ts or "—"}</div></div>'
                f'<div class="meta-cell"><div class="k">Bug ID</div><div class="v"><a href="#{bug_id}">{bug_id}</a></div></div>'
                f'<div class="meta-cell"><div class="k">Priority</div><div class="v">{_esc(bug.get("priority","P2"))}</div></div>'
                f'</div>'
            )
            er_grid = (
                f'<div class="er-grid">'
                f'<div class="er-card ok"><div class="k">Expected</div><div class="v">{exp or "—"}</div></div>'
                f'<div class="er-card bad"><div class="k">Actual</div><div class="v">{act or "—"}</div></div>'
                f'</div>'
            ) if (exp or act) else ""

            tb_id = f"tb-{bug_id}"
            tb_html = ""
            if tb or err:
                tb_html = (
                    f'<button class="trace-toggle" onclick="'
                    f'var w=this.nextElementSibling;w.style.display=w.style.display===\'block\'?\'none\':\'block\';'
                    f'this.querySelector(\'.arr\').textContent=w.style.display===\'block\'?\'▼\':\'▶\';">'
                    f'<span>Traceback / Error</span><span class="arr">▶</span></button>'
                    f'<div style="display:none"><div class="codebox">{err}\n\n{tb}</div></div>'
                )

            desc_html = f'<p style="font-size:13px;color:var(--ink-1);margin-bottom:12px">{desc}</p>' if desc else ""

            test_rows.append(
                f'<div class="test" data-outcome="fail" data-pri="{_esc(pri)}">'
                f'<div class="test-row">'
                f'<span class="chev">▶</span>'
                f'<div class="statdot fail">✗</div>'
                f'<div class="name-cell"><div class="tname">{tname}</div></div>'
                f'<span class="tag {_esc(pri)}">{_esc(bug.get("priority","P2"))}</span>'
                f'</div>'
                f'<div class="test-body">'
                f'{meta_grid}'
                f'{desc_html}'
                f'{er_grid}'
                f'{tb_html}'
                f'</div>'
                f'</div>'
            )

        # Passed tests
        for rec in passed_recs:
            tname = _esc(rec.get("name", "unknown"))
            doc   = _esc((rec.get("docstring") or "").strip())
            params = _esc(rec.get("params", "") or "")
            dur   = rec.get("duration", 0.0)
            dur_s = f"{dur:.2f}s" if dur else "—"
            test_rows.append(
                f'<div class="test" data-outcome="pass">'
                f'<div class="test-row">'
                f'<span class="chev">▶</span>'
                f'<div class="statdot pass">✓</div>'
                f'<div class="name-cell"><div class="tname">{tname}</div></div>'
                f'</div>'
                f'<div class="pass-body">'
                f'<dl class="pass-fields">'
                f'<dt>Test function</dt><dd>{tname}</dd>'
                + (f'<dt>What it checks</dt><dd>{doc}</dd>' if doc else '')
                + (f'<dt>Test data</dt><dd>{params}</dd>' if params else '')
                + f'<dt>Duration</dt><dd>{dur_s}</dd>'
                f'</dl>'
                f'</div>'
                f'</div>'
            )

        if not test_rows:
            continue

        groups.append(
            f'<div class="group" data-spec="{_esc(spec_name)}">'
            f'<div class="group-head">'
            f'<span class="chev">▶</span>'
            f'<span class="gtag">{_esc(spec_name)}</span>'
            f'<span class="count">{count_str}</span>'
            f'</div>'
            f'<div class="group-body">{"".join(test_rows)}</div>'
            f'</div>'
        )

    return "".join(groups) if groups else '<p style="color:var(--ink-3);padding:20px">No test results.</p>'


# ─────────────────────────────────────────────────────────────────────────────
# Bug ticket card
# ─────────────────────────────────────────────────────────────────────────────

def _bug_ticket(bug: dict, idx: int) -> str:
    sev   = bug.get("severity", "MEDIUM")
    pri   = bug.get("priority", "P2")
    title = bug.get("title", "Untitled Bug")
    test  = bug.get("test_name", "")
    url   = bug.get("page_url", "")
    ts    = bug.get("timestamp", "")[:19].replace("T", " ")
    dur   = bug.get("duration", "")
    desc  = bug.get("description", "")
    steps = bug.get("steps", [])
    exp   = bug.get("expected", "")
    act   = bug.get("actual", "")
    root  = bug.get("root_cause", "")
    fix   = bug.get("suggested_fix", "")
    err   = _esc(bug.get("error_message", ""))
    tb    = _esc(bug.get("traceback", ""))
    shot  = bug.get("screenshot_b64", "")
    video = bug.get("video_path", "")
    tdata = bug.get("test_data", "")
    bug_id = bug.get("id", f"BUG-{idx:03d}")
    env_b = bug.get("browser", "Chromium")
    env_v = bug.get("viewport", "1280x720")
    env_e = bug.get("env", "Staging")

    priority_label     = bug.get("priority_label", "")
    sla                = bug.get("sla", "")
    board_section      = bug.get("board_section", "")
    priority_rationale = bug.get("priority_rationale", "")
    priority_action    = bug.get("priority_action", "")
    biz_escalate       = bug.get("biz_escalate", False)

    board_cls = "expedite" if board_section == "Expedite" else "else"
    biz_html  = '<span class="biz-badge">[BIZ-ESCALATE]</span>' if biz_escalate else ""
    pri_label_html = f" · {priority_label}" if priority_label else ""

    # Steps
    steps_html = ""
    if steps:
        items = "".join(f"<li>{_esc(s)}</li>" for s in steps)
        steps_html = f"""
<div style="margin-bottom:16px">
  <div style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.6px;
              color:var(--ink-3);margin-bottom:8px">Steps to Reproduce</div>
  <ol class="steps">{items}</ol>
</div>"""

    # Expected/Actual
    exp_act = f"""
<div class="two-col">
  <div class="info-block expected">
    <div class="ib-label">What should happen</div>
    <div>{_esc(exp) or "<em style='color:var(--ink-3)'>Not specified</em>"}</div>
  </div>
  <div class="info-block actual">
    <div class="ib-label">What actually happened</div>
    <div>{_esc(act) or "<em style='color:var(--ink-3)'>See error below</em>"}</div>
  </div>
</div>"""

    # Screenshot
    if shot:
        shot_html = f"""
<div class="shot-wrap">
  <div class="shot-label">Proof of Concept — Screenshot</div>
  <img class="screenshot" src="{shot}" alt="Test failure screenshot" title="Click to enlarge"/>
</div>"""
    else:
        shot_html = """
<div class="shot-wrap">
  <div class="shot-label">Proof of Concept — Screenshot</div>
  <div class="no-shot">No screenshot captured (test may have failed before page loaded)</div>
</div>"""

    # Video
    if video:
        video_html = f"""
<div class="video-wrap">
  <div class="video-label">Proof of Concept — Screen Recording</div>
  <video class="poc-video" controls preload="metadata" src="{_esc(video)}" type="video/webm">
    Your browser does not support embedded video.
  </video>
  <div><a href="{_esc(video)}" download style="font-size:11px;color:var(--accent)">Download .webm</a></div>
</div>"""
    else:
        video_html = ""

    # Test data
    td_html = ""
    if tdata:
        td_html = f"""
<div class="info-block analysis" style="margin-bottom:16px">
  <div class="ib-label">Test data used</div>
  <div style="font-family:var(--mono);color:var(--accent);font-size:12px">{_esc(tdata)}</div>
</div>"""

    # Error collapsible
    err_id = f"err-{idx}"
    if err or tb:
        err_section = f"""
<button class="err-toggle" onclick="toggleErr('{err_id}')">
  <span>▶ Show error details</span>
  <span style="font-size:11px;color:var(--ink-3)">AssertionError / Traceback</span>
</button>
<div class="err-body" id="{err_id}">
  <pre style="margin-top:8px"><strong style="color:var(--bad)">{err}</strong>

{tb}</pre>
</div>"""
    else:
        err_section = ""

    # Evidence panels
    ev_html = ""
    ev_idx  = idx

    perf = bug.get("performance", {})
    if perf:
        def _perf_class(ms, warn=1500, bad=3000):
            if ms >= bad:  return "pval bad"
            if ms >= warn: return "pval warn"
            return "pval"
        dom_ms  = perf.get("dom_load_ms",  0)
        load_ms = perf.get("page_load_ms", 0)
        ttfb_ms = perf.get("ttfb_ms",      0)
        ev_html += f"""
<button class="ev-toggle" onclick="toggleEv('perf-{ev_idx}')">
  <span>Performance Timing</span>
  <span style="font-size:11px;color:var(--ink-3)">▶ Show</span>
</button>
<div class="ev-body" id="perf-{ev_idx}">
  <div class="perf-grid" style="margin:8px 0">
    <div class="perf-stat"><div class="{_perf_class(ttfb_ms,300,1000)}">{ttfb_ms}ms</div>
      <div class="plbl">TTFB</div></div>
    <div class="perf-stat"><div class="{_perf_class(dom_ms)}">{dom_ms}ms</div>
      <div class="plbl">DOM Ready</div></div>
    <div class="perf-stat"><div class="{_perf_class(load_ms,2000,4000)}">{load_ms}ms</div>
      <div class="plbl">Page Load</div></div>
  </div>
</div>"""

    errs = bug.get("error_log", [])
    if errs:
        items = "".join(
            f'<div class="console-{e.get("type","error")}">'
            f'<b>{_esc(e.get("type","").upper())}:</b> {_esc(e.get("text","")[:200])}</div>'
            for e in errs[:10]
        )
        ev_html += f"""
<button class="ev-toggle" onclick="toggleEv('console-{ev_idx}')" style="border-color:var(--bad);color:var(--bad)">
  <span>Console Errors ({len(errs)})</span>
  <span style="font-size:11px;color:var(--ink-3)">▶ Show</span>
</button>
<div class="ev-body" id="console-{ev_idx}">
  <div style="margin:8px 0">{items}</div>
</div>"""

    net_log = [n for n in bug.get("network_log", []) if "/api/" in n.get("url", "")]
    if net_log:
        rows_net = "".join(
            f'<tr><td>{_esc(n.get("method",""))}</td>'
            f'<td style="color:{"var(--ok)" if 200<=n.get("status",0)<300 else "var(--bad)"}">'\
            f'{n.get("status","")}</td>'
            f'<td>{_esc(n.get("url","")[-80:])}</td></tr>'
            for n in net_log[:15] if n.get("type") == "response"
        )
        if rows_net:
            ev_html += f"""
<button class="ev-toggle" onclick="toggleEv('net-{ev_idx}')">
  <span>Network Log ({len(net_log)} API calls)</span>
  <span style="font-size:11px;color:var(--ink-3)">▶ Show</span>
</button>
<div class="ev-body" id="net-{ev_idx}">
  <table class="ev-table" style="margin:8px 0">
    <thead><tr><th>Method</th><th>Status</th><th>URL</th></tr></thead>
    <tbody>{rows_net}</tbody>
  </table>
</div>"""

    analysis_fix = ""
    if root:
        analysis_fix += f"""
<div class="info-block rootcause" style="margin-bottom:12px">
  <div class="ib-label">Root Cause Analysis (AI)</div>
  <div>{_esc(root)}</div>
</div>"""
    if fix:
        analysis_fix += f"""
<div class="info-block fix">
  <div class="ib-label">Suggested Fix for Developer</div>
  <div>{_esc(fix)}</div>
</div>"""

    desc_html = ""
    if desc:
        desc_html = f"""
<div class="info-block analysis" style="margin-bottom:16px">
  <div class="ib-label">What this test was checking</div>
  <div>{_esc(desc)}</div>
</div>"""

    priority_html = ""
    if priority_rationale:
        action_line = (f'<div style="margin-top:6px;font-size:11px;color:var(--ink-3)">'
                       f'Action: {_esc(priority_action)}</div>') if priority_action else ""
        priority_html = f"""
<div class="info-block priority" style="margin-bottom:16px">
  <div class="ib-label">Priority Rationale</div>
  <div>{_esc(priority_rationale)}</div>
  {action_line}
</div>"""

    return f"""
<div class="bug-card" id="{bug_id}" data-priority="{pri}">
  <div class="bug-card-hdr">
    <div>
      <div class="left">
        <span class="bug-id">{bug_id}</span>
        <span class="badge {sev}">{sev}</span>
        <span class="badge {pri}">{pri}{pri_label_html}</span>
        {biz_html}
      </div>
      <div class="bug-title">{_esc(title)}</div>
      <div class="bug-meta">
        <span><a href="{_esc(url)}" target="_blank">{_esc(url)}</a></span>
        <span><code>{_esc(test)}</code></span>
        <span>{ts}</span>
        {'<span>' + dur + '</span>' if dur else ''}
        {f'<span><span class="sla-chip">SLA: {_esc(sla)}</span></span>' if sla else ''}
        {f'<span><span class="board-chip {board_cls}">{_esc(board_section)}</span></span>' if board_section else ''}
      </div>
    </div>
  </div>
  <div class="bug-body">
    {priority_html}
    {desc_html}
    {td_html}
    {steps_html}
    {exp_act}
    {shot_html}
    {video_html}
    {err_section}
    {ev_html}
    <div style="margin-top:16px">{analysis_fix}</div>
    <div class="env-strip">
      <span><b>Browser:</b> {env_b}</span>
      <span><b>Viewport:</b> {env_v}</span>
      <span><b>Env:</b> {env_e}</span>
    </div>
  </div>
</div>"""


# ─────────────────────────────────────────────────────────────────────────────
# Gaps block
# ─────────────────────────────────────────────────────────────────────────────

def _gaps_block(name: str, gaps: str) -> str:
    if not gaps:
        return ""
    lines = [f"<p>{_esc(l.strip())}</p>" if l.strip() else "" for l in gaps.splitlines()]
    return f"""<div class="gap-block">
  <h3>{_esc(name.replace('-', ' ').title())}</h3>
  {''.join(lines)}
</div>"""


# ─────────────────────────────────────────────────────────────────────────────
# Root-cause cluster summary
# ─────────────────────────────────────────────────────────────────────────────

def _build_cluster_summary(all_bugs: list) -> str:
    if not all_bugs:
        return ""
    by_fp: dict = {}
    for bug in all_bugs:
        fp = bug.get("fingerprint", "")
        if not fp:
            continue
        if fp not in by_fp:
            by_fp[fp] = {
                "title":    bug.get("category_title", "(uncategorized)"),
                "severity": bug.get("severity", "MEDIUM"),
                "priority": bug.get("priority", "P2"),
                "bugs":     [],
                "recurrence": bug.get("recurrence_count", 1),
            }
        by_fp[fp]["bugs"].append(bug)
        sev_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        if sev_order.get(bug.get("severity", "MEDIUM"), 9) < \
           sev_order.get(by_fp[fp]["severity"], 9):
            by_fp[fp]["severity"] = bug.get("severity")
            by_fp[fp]["priority"] = bug.get("priority", "P2")

    if not by_fp:
        return ""

    sev_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    sorted_clusters = sorted(
        by_fp.items(),
        key=lambda kv: (sev_order.get(kv[1]["severity"], 9), -len(kv[1]["bugs"]))
    )

    rows_html = []
    for fp, c in sorted_clusters:
        bugs   = c["bugs"]
        sev    = c["severity"]
        pri    = c["priority"]
        n      = len(bugs)
        recur  = c["recurrence"]
        title  = _esc(c["title"])
        bug_links = " ".join(
            f'<a href="#{_esc(b.get("id",""))}" class="cluster-bug-link">'
            f'{_esc(b.get("id",""))}</a>'
            for b in bugs
        )
        recur_badge = (f'<span class="recurrence-badge">{recur}x consecutive</span>'
                       if recur >= 3 else "")
        rows_html.append(f"""
<div class="cluster-row">
  <div class="cluster-meta">
    <span class="badge {sev}">{sev}</span>
    <span class="badge {pri}">{pri}</span>
    <span class="cluster-count">{n}x affected</span>
    {recur_badge}
  </div>
  <div class="cluster-title">{title}</div>
  <div class="cluster-tickets">{bug_links}</div>
</div>""")

    n_clusters = len(by_fp)
    n_bugs     = sum(len(c["bugs"]) for c in by_fp.values())
    headline   = (f"{n_bugs} bug ticket(s) → "
                  f"<strong>{n_clusters} unique root cause(s)</strong>")

    return f"""
<section class="card">
  <div class="card-head"><h4>Root-Cause Summary</h4><span style="font-size:12px;color:var(--ink-3)">{n_clusters} clusters</span></div>
  <div class="card-body">
    <div class="cluster-headline">{headline}</div>
    <div class="cluster-list">{"".join(rows_html)}</div>
    <div class="cluster-help">
      Bugs sharing a root cause are grouped here. Click any ticket ID to jump to its full bug card.
    </div>
  </div>
</section>"""


# ─────────────────────────────────────────────────────────────────────────────
# Public entry point
# ─────────────────────────────────────────────────────────────────────────────

def generate_report(all_results: dict, base_url: str, model: str,
                    output_filename: str = "bug-report.html",
                    extra_section_html: str = "",
                    base_path_prefix: str = "") -> Path:
    """Render the master or per-agent HTML report with the new Commit Report design."""

    run_num = os.environ.get("GITHUB_RUN_NUMBER") or os.environ.get("CI_RUN_NUMBER") or "latest"
    run_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    all_bugs = [b for r in all_results.values() for b in r.get("bugs", [])]

    total_passed = sum(r.get("passed", 0) for r in all_results.values())
    total_failed = sum(r.get("failed", 0) for r in all_results.values())
    total_tests  = sum(r.get("total",  0) for r in all_results.values())
    total_specs  = len(all_results)
    passed_specs = sum(1 for r in all_results.values() if r.get("failed", 0) == 0)

    cnt     = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    pri_cnt = {"P0": 0, "P1": 0, "P2": 0, "P3": 0}
    for b in all_bugs:
        sev = b.get("severity", "MEDIUM").upper()
        cnt[sev] = cnt.get(sev, 0) + 1
        pri = b.get("priority", "P2")
        pri_cnt[pri] = pri_cnt.get(pri, 0) + 1

    cnt_p0 = pri_cnt["P0"]
    cnt_p1 = pri_cnt["P1"]
    cnt_p2 = pri_cnt["P2"]
    cnt_p3 = pri_cnt["P3"]

    # Pass rate
    pass_rate = round(total_passed / total_tests * 100, 1) if total_tests > 0 else 0.0

    # Ring gauge
    ring_offset = round(113.1 * (1 - pass_rate / 100), 2)
    if pass_rate >= 80:
        ring_color = "oklch(0.85 0.14 155)"
    elif pass_rate >= 50:
        ring_color = "oklch(0.92 0.14 85)"
    else:
        ring_color = "oklch(0.85 0.18 25)"

    # Verdict
    if cnt_p0 > 0:
        verdict_label    = "No-Go"
        stamp_cls        = ""
        verdict_pill_cls = "fail"
        verdict_pill     = "No-Go for production"
        verdict_sub      = f"{cnt_p0} critical · {cnt_p1} high"
    elif total_failed > 0:
        verdict_label    = "Review"
        stamp_cls        = ""
        verdict_pill_cls = "fail"
        verdict_pill     = "Needs review"
        verdict_sub      = f"{total_failed} failing"
    else:
        verdict_label    = "Ready"
        stamp_cls        = "pass-stamp"
        verdict_pill_cls = "ok"
        verdict_pill     = "Ready for production"
        verdict_sub      = "all passing"

    # Summary title & description
    if total_failed > 0:
        run_summary_title = f"{pass_rate}% — {total_failed} test(s) need attention"
        run_description   = (
            f"AI-driven spec validation completed on {base_url}. "
            f"{cnt_p0} critical, {cnt_p1} high, {cnt_p2} medium, {cnt_p3} low priority bugs "
            f"found across {total_specs} spec(s)."
        )
    else:
        run_summary_title = f"all {total_tests} tests passed"
        run_description   = (
            f"AI-driven spec validation completed successfully on {base_url}. "
            f"All {total_tests} tests passed across {total_specs} spec(s)."
        )

    # Diff-row classes
    if pass_rate > 80:
        pass_rate_cls = "up"
        pass_rate_sym = "+"
    elif pass_rate > 50:
        pass_rate_cls = "neutral"
        pass_rate_sym = "·"
    else:
        pass_rate_cls = "add"
        pass_rate_sym = "−"

    fail_cls = "add" if total_failed > 0 else "neutral"
    fail_sym = "+" if total_failed > 0 else "·"

    p0_cls = "add" if cnt_p0 > 0 else "neutral"
    p0_sym = "+" if cnt_p0 > 0 else "·"
    p0_label = str(cnt_p0)

    p1_cls = "add" if cnt_p1 > 0 else "neutral"
    p1_sym = "+" if cnt_p1 > 0 else "·"
    p1_label = str(cnt_p1)

    # Mini-stat classes
    p0_ms_cls = "bad" if cnt_p0 > 0 else ""
    p1_ms_cls = "warn" if cnt_p1 > 0 else ""
    p2_ms_cls = "ok" if cnt_p2 > 0 else ""

    # URL short form
    base_url_short = re.sub(r"^https?://", "", base_url).rstrip("/")

    # Build HTML sections
    spec_trace_rows = _build_spec_trace(all_results)
    tests_body_html = _build_tests_body(all_results)

    cluster_html = _build_cluster_summary(all_bugs)

    if all_bugs:
        bug_items = "".join(_bug_ticket(b, i + 1) for i, b in enumerate(all_bugs))
        bug_section_html = (
            f'<section class="card" id="bugs">'
            f'<div class="card-head"><h4>Bug Tickets</h4>'
            f'<span style="font-size:12px;color:var(--ink-3)">{len(all_bugs)} total</span></div>'
            f'<div class="card-body" style="padding:0">'
            f'{cluster_html}'
            f'<div id="bug-list" style="padding:20px">{bug_items}</div>'
            f'</div>'
            f'</section>'
        )
    else:
        bug_section_html = (
            '<section class="card" id="bugs">'
            '<div class="card-head"><h4>Bug Tickets</h4>'
            '<span style="font-size:12px;color:var(--ok)">0 bugs found</span></div>'
            '<div class="card-body" style="text-align:center;color:var(--ok);padding:32px">'
            'No bugs detected — all tests passed.'
            '</div></section>'
        )

    gaps_parts = [_gaps_block(name, r.get("gaps", "")) for name, r in all_results.items()]
    gaps_inner = "".join(g for g in gaps_parts if g)
    if gaps_inner:
        gaps_section_html = (
            '<section class="card" id="gaps">'
            '<div class="card-head"><h4>Coverage Gaps</h4><span style="font-size:12px;color:var(--ink-3)">AI Analysis</span></div>'
            f'<div class="card-body">{gaps_inner}</div>'
            '</section>'
        )
    else:
        gaps_section_html = ""

    html = _PAGE.format(
        run_num          = run_num,
        run_date         = run_date,
        base_url         = _esc(base_url),
        base_url_short   = _esc(base_url_short),
        model            = _esc(model),
        total_tests      = total_tests,
        total_passed     = total_passed,
        total_failed     = total_failed,
        total_bugs       = len(all_bugs),
        total_specs      = total_specs,
        passed_specs     = passed_specs,
        pass_rate        = pass_rate,
        cnt_p0           = cnt_p0,
        cnt_p1           = cnt_p1,
        cnt_p2           = cnt_p2,
        cnt_p3           = cnt_p3,
        cnt_critical     = cnt["CRITICAL"],
        cnt_high         = cnt["HIGH"],
        cnt_medium       = cnt["MEDIUM"],
        cnt_low          = cnt["LOW"],
        verdict_label    = verdict_label,
        verdict_sub      = verdict_sub,
        verdict_pill_cls = verdict_pill_cls,
        verdict_pill     = verdict_pill,
        stamp_cls        = stamp_cls,
        pass_rate_cls    = pass_rate_cls,
        pass_rate_sym    = pass_rate_sym,
        fail_cls         = fail_cls,
        fail_sym         = fail_sym,
        p0_cls           = p0_cls,
        p0_sym           = p0_sym,
        p0_label         = p0_label,
        p1_cls           = p1_cls,
        p1_sym           = p1_sym,
        p1_label         = p1_label,
        run_summary_title= run_summary_title,
        run_description  = run_description,
        ring_offset      = ring_offset,
        ring_color       = ring_color,
        p0_ms_cls        = p0_ms_cls,
        p1_ms_cls        = p1_ms_cls,
        p2_ms_cls        = p2_ms_cls,
        spec_trace_rows  = spec_trace_rows,
        tests_body_html  = tests_body_html,
        bug_section_html = bug_section_html,
        gaps_section_html= gaps_section_html,
        extra_section_html = extra_section_html,
    )

    REPORTS_DIR.mkdir(exist_ok=True)
    out = REPORTS_DIR / output_filename
    out.write_text(html, encoding="utf-8")
    return out
