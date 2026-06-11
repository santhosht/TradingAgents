#!/usr/bin/env python3
"""Dynamic reports viewer — reads files on-the-fly, no conversion needed."""

import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from flask import Flask, abort, render_template_string, request
import markdown as md

ET = ZoneInfo("America/New_York")

REPORTS_DIR = Path(__file__).parent / "data" / "reports"
KB_DIR = Path(__file__).parent / "data" / "knowledge_base"
CHECKS_DIR = Path(__file__).parent / "data" / "checks"

app = Flask(__name__)

BASE_HTML = """<!DOCTYPE html>
<html data-theme="dark">
<head>
  <meta charset="utf-8">
  <title>{{ title }}</title>
  <style>
    :root[data-theme="dark"] {
      --bg: #0f1117; --sidebar-bg: #1a1d2e; --border: #2a2d3e;
      --text: #e0e0e0; --muted: #666; --accent: #7c83ff;
      --code-bg: #1e2235; --code-color: #f8c555; --even-row: #15182a;
      --pre-color: #d0d0d0; --heading: #c8d0ff;
      --hover-bg: #2a2d3e; --current-bg: #2a3a6e;
      --day-bg: #151824; --symbol-bg: #1c1f30;
      --welcome-border: #2a2d3e;
      --select-bg: #1e2235;
    }
    :root[data-theme="light"] {
      --bg: #f5f6fa; --sidebar-bg: #ffffff; --border: #dde1f0;
      --text: #1a1d2e; --muted: #999; --accent: #4a52e0;
      --code-bg: #eef0fb; --code-color: #b05c00; --even-row: #f0f2fc;
      --pre-color: #2a2d3e; --heading: #2a2d8e;
      --hover-bg: #eef0fb; --current-bg: #dde4ff;
      --day-bg: #f0f2fc; --symbol-bg: #e8eaf8;
      --welcome-border: #dde1f0;
      --select-bg: #eef0fb;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
           background: var(--bg); color: var(--text);
           transition: background 0.2s, color 0.2s; }

    /* ── Sidebar ── */
    .sidebar { width: 300px; position: fixed; top: 0; left: 0; bottom: 0;
               background: var(--sidebar-bg); display: flex; flex-direction: column;
               border-right: 1px solid var(--border); overflow: hidden; }

    .sidebar-top { padding: 12px 14px; border-bottom: 1px solid var(--border);
                   display: flex; flex-direction: column; gap: 8px; flex-shrink: 0; }

    .sidebar-title-row { display: flex; align-items: center; justify-content: space-between; }
    .sidebar-title { font-size: 12px; font-weight: 700; text-transform: uppercase;
                     letter-spacing: 1px; color: var(--accent); }
    .theme-btn { background: none; border: 1px solid var(--border); border-radius: 5px;
                 padding: 2px 7px; cursor: pointer; font-size: 13px; color: var(--muted); }
    .theme-btn:hover { border-color: var(--accent); }

    /* Program dropdown */
    .program-select { width: 100%; background: var(--select-bg); color: var(--text);
                      border: 1px solid var(--border); border-radius: 5px;
                      padding: 5px 8px; font-size: 12px; cursor: pointer;
                      appearance: none; -webkit-appearance: none;
                      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6'%3E%3Cpath d='M0 0l5 6 5-6z' fill='%23666'/%3E%3C/svg%3E");
                      background-repeat: no-repeat; background-position: right 8px center; }
    .program-select:focus { outline: none; border-color: var(--accent); }

    .view-toggle { display: flex; border: 1px solid var(--border); border-radius: 5px;
                   overflow: hidden; }
    .view-btn { flex: 1; background: none; border: none; padding: 5px 0; font-size: 11px;
                font-weight: 600; cursor: pointer; color: var(--muted);
                transition: background 0.15s, color 0.15s; }
    .view-btn.active { background: var(--accent); color: #fff; }
    .view-btn:not(.active):hover { background: var(--hover-bg); color: var(--text); }

    .sidebar-scroll { flex: 1; overflow-y: auto; padding: 8px 0; }

    /* top-level .md files */
    .nav-top-files { padding: 4px 14px 8px; border-bottom: 1px solid var(--border); margin-bottom: 4px; }
    .nav-top-label { font-size: 10px; font-weight: 700; text-transform: uppercase;
                     letter-spacing: 0.8px; color: var(--muted); margin-bottom: 4px; }
    .nav-top-files a { display: block; font-size: 12px; padding: 3px 6px;
                       color: var(--muted); text-decoration: none; border-radius: 3px; }
    .nav-top-files a:hover { background: var(--hover-bg); color: var(--text); }
    .nav-top-files a.current { background: var(--current-bg); color: var(--accent); }

    /* Day / Symbol section headers */
    .nav-section { margin-bottom: 2px; }
    .nav-section-hdr { display: flex; align-items: center; gap: 6px; padding: 5px 14px;
                       cursor: pointer; user-select: none; }
    .nav-section-hdr:hover { background: var(--hover-bg); }
    .nav-chevron { font-size: 9px; color: var(--muted); margin-right: 5px;
                   transition: transform 0.15s; display: inline-block; }
    .nav-section-hdr.open .nav-chevron { transform: rotate(90deg); }
    .nav-section-label { font-size: 12px; font-weight: 700; color: var(--text); }
    .nav-section-meta { font-size: 10px; color: var(--muted); margin-left: auto; }
    .nav-section-body { display: none; }
    .nav-section-body.open { display: block; }

    /* Symbol sub-group inside a day section (date view) */
    .nav-symbol-hdr { display: flex; align-items: center; padding: 3px 14px 3px 26px;
                      cursor: pointer; user-select: none; }
    .nav-symbol-hdr:hover { background: var(--hover-bg); }
    .nav-symbol-chevron { font-size: 9px; color: var(--muted); margin-right: 5px;
                          transition: transform 0.15s; display: inline-block; }
    .nav-symbol-hdr.open .nav-symbol-chevron { transform: rotate(90deg); }
    .nav-symbol-name { font-size: 11px; font-weight: 700; color: var(--accent); }
    .nav-symbol-count { font-size: 10px; color: var(--muted); margin-left: auto; }
    .nav-symbol-body { display: none; }
    .nav-symbol-body.open { display: block; }

    /* Date sub-group inside a symbol section (symbol view) */
    .nav-date-hdr { display: flex; align-items: center; padding: 3px 14px 3px 26px;
                    cursor: pointer; user-select: none; }
    .nav-date-hdr:hover { background: var(--hover-bg); }
    .nav-date-chevron { font-size: 9px; color: var(--muted); margin-right: 5px;
                        transition: transform 0.15s; display: inline-block; }
    .nav-date-hdr.open .nav-date-chevron { transform: rotate(90deg); }
    .nav-date-label { font-size: 11px; font-weight: 600; color: var(--text); }
    .nav-date-count { font-size: 10px; color: var(--muted); margin-left: auto; }
    .nav-date-body { display: none; }
    .nav-date-body.open { display: block; }

    /* Run row (expandable time entry) */
    .nav-run-hdr { display: flex; align-items: center; gap: 5px; padding: 3px 14px 3px 38px;
                   cursor: pointer; user-select: none; color: var(--muted); }
    .nav-run-hdr:hover { background: var(--hover-bg); color: var(--text); }
    .nav-run-hdr.has-current { color: var(--accent); }
    .nav-run-chevron { font-size: 9px; color: var(--muted); transition: transform 0.15s;
                       display: inline-block; }
    .nav-run-hdr.open .nav-run-chevron { transform: rotate(90deg); }
    .nav-run-time { font-size: 11px; font-weight: 600; font-family: monospace; min-width: 38px; }
    .nav-run-count { font-size: 10px; color: var(--muted); margin-left: auto; }
    .nav-run-body { display: none; padding-left: 48px; }
    .nav-run-body.open { display: block; }
    /* Individual file links inside a run */
    .nav-file { display: block; font-size: 11px; padding: 2px 14px 2px 0;
                text-decoration: none; color: var(--muted); border-left: 2px solid transparent;
                white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .nav-file:hover { color: var(--text); }
    .nav-file.current { color: var(--accent); border-left-color: var(--accent);
                        padding-left: 6px; }

    /* ── Main ── */
    .main { margin-left: 300px; padding: 40px 52px; max-width: 1100px; min-height: 100vh; }

    /* Welcome */
    .welcome { display: flex; flex-direction: column; align-items: center; justify-content: center;
               min-height: 60vh; text-align: center; gap: 12px; }
    .welcome h2 { font-size: 24px; color: var(--text); }
    .welcome p { color: var(--muted); font-size: 14px; }

    /* Breadcrumb + file */
    .breadcrumb { font-size: 12px; color: var(--muted); margin-bottom: 20px; }
    .breadcrumb a { color: var(--accent); text-decoration: none; }
    .breadcrumb a:hover { text-decoration: underline; }
    h1 { font-size: 20px; color: var(--text); margin-bottom: 24px; }

    /* Markdown */
    .content h1, .content h2, .content h3 { color: var(--heading); }
    .content h1 { font-size: 20px; margin: 24px 0 12px; }
    .content h2 { font-size: 17px; border-bottom: 1px solid var(--border);
                  padding-bottom: 6px; margin: 20px 0 10px; }
    .content h3 { font-size: 14px; margin: 16px 0 8px; }
    .content p { line-height: 1.7; margin-bottom: 12px; }
    .content code { background: var(--code-bg); padding: 2px 6px; border-radius: 3px;
                    font-size: 13px; color: var(--code-color); }
    .content pre { background: var(--code-bg); padding: 16px; border-radius: 6px;
                   overflow-x: auto; border: 1px solid var(--border); margin-bottom: 16px; }
    .content pre code { background: none; padding: 0; color: var(--text); }
    .content blockquote { border-left: 3px solid var(--accent); padding-left: 16px;
                          color: var(--muted); margin: 12px 0; }
    .content table { border-collapse: collapse; width: 100%; margin-bottom: 16px; }
    .content th, .content td { border: 1px solid var(--border); padding: 8px 12px; }
    .content th { background: var(--code-bg); color: var(--heading); }
    .content tr:nth-child(even) { background: var(--even-row); }
    .content a { color: var(--accent); }
    .content hr { border: none; border-top: 1px solid var(--border); margin: 16px 0; }
    .content ul, .content ol { padding-left: 24px; margin-bottom: 12px; }
    .content li { line-height: 1.7; }
    .pre { background: var(--code-bg); padding: 20px; border-radius: 6px;
           font-size: 13px; white-space: pre-wrap; line-height: 1.6; color: var(--pre-color); }

    /* Rating / mode badges */
    .badge { font-size: 9px; font-weight: 700; padding: 1px 4px; border-radius: 3px;
             text-transform: uppercase; letter-spacing: 0.4px; flex-shrink: 0; }
    .badge-ow  { background: #1a4a2e; color: #4ade80; }
    .badge-uw  { background: #4a1a1a; color: #f87171; }
    .badge-hold{ background: #3a3010; color: #facc15; }
    .badge-unk { background: #2a2a2a; color: #888; }
    .badge-deep{ background: #2a1a4a; color: #c084fc; }
    .badge-med { background: #1a2a4a; color: #60a5fa; }
    .badge-fast{ background: #0a3030; color: #34d399; }

    /* ── Knowledge Base section ── */
    .nav-kb { border-top: 1px solid var(--border); margin-top: 8px; padding: 8px 14px 12px; }
    .nav-kb-label { font-size: 10px; font-weight: 700; text-transform: uppercase;
                    letter-spacing: 0.8px; color: var(--muted); margin-bottom: 6px; }
    .nav-kb a { display: block; font-size: 12px; padding: 4px 6px;
                color: var(--muted); text-decoration: none; border-radius: 3px;
                white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .nav-kb a:hover { background: var(--hover-bg); color: var(--text); }
    .nav-kb a.current { background: var(--current-bg); color: var(--accent); }

    /* ── Live Checks section ── */
    .nav-checks { border-top: 1px solid var(--border); padding: 8px 14px 12px; }
    .nav-checks-label { font-size: 10px; font-weight: 700; text-transform: uppercase;
                        letter-spacing: 0.8px; color: var(--muted); margin-bottom: 6px; }
    .nav-checks a { display: block; font-size: 12px; padding: 4px 6px;
                    color: var(--muted); text-decoration: none; border-radius: 3px; }
    .nav-checks a:hover { background: var(--hover-bg); color: var(--text); }
    .nav-checks a.current { background: var(--current-bg); color: var(--accent); }
  </style>
</head>
<body>
<div class="sidebar">
  <div class="sidebar-top">
    <div class="sidebar-title-row">
      <span class="sidebar-title">Trading Reports</span>
      <button class="theme-btn" id="theme-btn" onclick="toggleTheme()">☀️</button>
    </div>
    <select class="program-select" id="program-select" onchange="setProgram(this.value)">
      {{ program_options | safe }}
    </select>
    <div class="view-toggle">
      <button class="view-btn" data-view="date" onclick="setView('date')">By Date</button>
      <button class="view-btn" data-view="symbol" onclick="setView('symbol')">By Symbol</button>
    </div>
  </div>
  <div class="sidebar-scroll" id="sidebar-scroll">
    {{ nav_top | safe }}
    {{ nav_date | safe }}
    {{ nav_symbol | safe }}
    {{ nav_checks | safe }}
    {{ nav_kb | safe }}
  </div>
</div>
<div class="main">
  {{ content | safe }}
</div>
<script>
  const root = document.documentElement;

  // ── Theme ──────────────────────────────────────────────────────────────
  function applyTheme(t) {
    root.setAttribute('data-theme', t);
    const btn = document.getElementById('theme-btn');
    if (btn) btn.textContent = t === 'dark' ? '☀️' : '🌙';
  }
  applyTheme(localStorage.getItem('theme') || 'dark');
  function toggleTheme() {
    const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    localStorage.setItem('theme', next);
    applyTheme(next);
  }

  // ── Program filter ─────────────────────────────────────────────────────
  let currentProgram = localStorage.getItem('program') || 'all';
  let currentHref = location.pathname;

  function applyProgram(p) {
    const sel = document.getElementById('program-select');
    if (sel) sel.value = p;
  }

  async function setProgram(p) {
    currentProgram = p;
    localStorage.setItem('program', p);
    try {
      const res = await fetch('/nav_fragment?program=' + encodeURIComponent(p));
      if (!res.ok) return;
      const html = await res.text();
      document.getElementById('sidebar-scroll').innerHTML = html;
      rebindToggles();
      activateFile(currentHref);
      autoExpand();
      // re-apply view after nav swap
      setView(localStorage.getItem('indexView') || 'date');
    } catch(e) { /* silently ignore */ }
  }

  // init program on load
  applyProgram(currentProgram);

  // ── View toggle (date / symbol) ────────────────────────────────────────
  function setView(v) {
    localStorage.setItem('indexView', v);
    document.querySelectorAll('.nav-panel').forEach(p => p.style.display = 'none');
    const panel = document.getElementById('nav-' + v);
    if (panel) panel.style.display = 'block';
    document.querySelectorAll('.view-btn').forEach(b =>
      b.classList.toggle('active', b.dataset.view === v));
  }
  setView(localStorage.getItem('indexView') || 'date');

  // ── Collapse toggles ───────────────────────────────────────────────────
  function bindToggle(sel) {
    document.querySelectorAll(sel).forEach(hdr => {
      hdr.addEventListener('click', () => {
        hdr.classList.toggle('open');
        hdr.nextElementSibling.classList.toggle('open');
      });
    });
  }
  function rebindToggles() {
    bindToggle('.nav-section-hdr');
    bindToggle('.nav-symbol-hdr');
    bindToggle('.nav-date-hdr');
    bindToggle('.nav-run-hdr');
  }
  rebindToggles();

  // ── Highlight current file & auto-expand ──────────────────────────────
  function activateFile(href) {
    document.querySelectorAll('.nav-file').forEach(a => {
      a.classList.toggle('current', a.getAttribute('href') === href);
    });
    const cur = document.querySelector('.nav-file.current');
    if (cur) cur.scrollIntoView({ block: 'nearest' });
  }

  function autoExpand() {
    const cur = document.querySelector('.nav-file.current');
    if (!cur) {
      ['nav-date', 'nav-symbol'].forEach(id => {
        const panel = document.getElementById(id);
        if (panel && panel.style.display !== 'none') {
          const first = panel.querySelector('.nav-section-hdr');
          if (first && !first.classList.contains('open')) {
            first.classList.add('open');
            first.nextElementSibling.classList.add('open');
          }
        }
      });
      return;
    }
    let el = cur.parentElement;
    while (el) {
      const c = el.classList;
      if (c.contains('nav-run-body') || c.contains('nav-symbol-body') ||
          c.contains('nav-section-body') || c.contains('nav-date-body')) {
        if (!c.contains('open')) {
          c.add('open');
          const hdr = el.previousElementSibling;
          if (hdr) hdr.classList.add('open');
        }
      }
      el = el.parentElement;
    }
    cur.scrollIntoView({ block: 'nearest' });
  }
  autoExpand();

  // ── AJAX file navigation — sidebar never reloads ───────────────────────
  const mainEl = document.querySelector('.main');

  async function navigateTo(href, pushState = true) {
    currentHref = href;
    try {
      const fragmentUrl = href.startsWith('/kb/')
        ? '/kb_fragment/' + href.slice(4)
        : href.startsWith('/checks/')
        ? '/checks_fragment/' + href.slice(8)
        : '/fragment' + href.replace(/^[/]view/, '');
      const res = await fetch(fragmentUrl);
      if (!res.ok) { window.location = href; return; }

      const html = await res.text();
      mainEl.innerHTML = html;
      if (pushState) history.pushState({ href }, '', href);
      activateFile(href);
      document.title = href.split('/').pop();
      mainEl.scrollTop = 0;
      window.scrollTo(0, 0);
    } catch(e) {
      window.location = href;
    }
  }

  // intercept all nav-file clicks
  document.querySelector('.sidebar').addEventListener('click', e => {
    const a = e.target.closest('.nav-file');
    if (!a) return;
    e.preventDefault();
    navigateTo(a.getAttribute('href'));
  });

  // handle browser back/forward
  window.addEventListener('popstate', e => {
    if (e.state && e.state.href) navigateTo(e.state.href, false);
    else { mainEl.innerHTML = '<div class="welcome"><h2>Trading Analysis Reports</h2></div>'; }
  });

  history.replaceState({ href: location.pathname }, '', location.pathname);
</script>
</body>
</html>"""


# ── Helpers ────────────────────────────────────────────────────────────────

def is_run_folder(name):
    """True if name matches TICKER_YYYYMMDD_HHMMSS pattern."""
    parts = name.split("_")
    return (len(parts) >= 3
            and len(parts[1]) == 8 and parts[1].isdigit()
            and len(parts[2]) >= 6 and parts[2][:6].isdigit())


def prog_label(name):
    """SPACEX_ECOSYSTEM -> SpaceX Ecosystem (best-effort)."""
    return name.replace("_", " ").title()


def parse_run(entry):
    """Return (ticker, et_date YYYYMMDD, et_time HHMMSS) converted from UTC folder name."""
    parts = entry.name.split("_")
    ticker = parts[0] if parts else entry.name
    date_str = parts[1] if len(parts) >= 2 else ""
    time_str = parts[2] if len(parts) >= 3 else "000000"

    if len(date_str) == 8 and len(time_str) >= 6:
        try:
            utc_dt = datetime(
                int(date_str[:4]), int(date_str[4:6]), int(date_str[6:]),
                int(time_str[:2]), int(time_str[2:4]), int(time_str[4:6]),
                tzinfo=timezone.utc,
            )
            et_dt = utc_dt.astimezone(ET)
            return ticker, et_dt.strftime("%Y%m%d"), et_dt.strftime("%H%M%S")
        except ValueError:
            pass
    return ticker, date_str, time_str


def fmt_date(d):
    if len(d) == 8:
        return f"{d[:4]}-{d[4:6]}-{d[6:]}"
    return d


def fmt_time(t):
    if len(t) >= 4:
        return f"{t[:2]}:{t[2:4]}"
    return t


def best_file(files):
    for p in ["summary", "decision", "complete_report"]:
        f = next((f for f in files if p in f.name), None)
        if f:
            return f
    return files[0]


def load_meta(run_path):
    """Read meta.json from run folder; returns {} if missing or malformed."""
    meta_file = run_path / "meta.json"
    if not meta_file.exists():
        return {}
    try:
        return json.loads(meta_file.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def rating_badge(rating):
    r = (rating or "").lower()
    if r == "overweight":
        return '<span class="badge badge-ow">OW</span>'
    if r == "underweight":
        return '<span class="badge badge-uw">UW</span>'
    if r == "hold":
        return '<span class="badge badge-hold">Hold</span>'
    return '<span class="badge badge-unk">?</span>'


def mode_badge(mode):
    m = (mode or "").lower()
    if m == "deep":
        return '<span class="badge badge-deep">D</span>'
    if m == "medium":
        return '<span class="badge badge-med">M</span>'
    if m == "fast":
        return '<span class="badge badge-fast">F</span>'
    return ""


# ── Data loading ───────────────────────────────────────────────────────────

def get_runs():
    """
    Scan REPORTS_DIR for runs and program subfolders.

    Returns:
        runs       — list of run dicts, each with a 'program' key
        top_default — .md files at REPORTS_DIR root
        top_programs — {program_name: [Path, ...]} for program-level .md files
    """
    runs = []
    top_default = []
    top_programs = {}

    if not REPORTS_DIR.exists():
        return runs, top_default, top_programs

    try:
        entries = sorted(REPORTS_DIR.iterdir(), reverse=True)
    except PermissionError:
        return runs, top_default, top_programs

    for entry in entries:
        try:
            if entry.is_file() and entry.suffix == ".md":
                top_default.append(entry)

            elif entry.is_dir():
                if is_run_folder(entry.name):
                    # default (non-program) run
                    files = sorted(entry.rglob("*.md")) + sorted(entry.rglob("*.txt"))
                    if files:
                        ticker, date_str, time_str = parse_run(entry)
                        runs.append({
                            "name": entry.name, "path": entry, "files": files,
                            "ticker": ticker, "date": date_str, "time": time_str,
                            "program": "default",
                        })
                else:
                    # program folder — recurse one level
                    prog = entry.name
                    top_programs[prog] = {"files": [], "sessions": {}}
                    try:
                        for sub in sorted(entry.iterdir(), reverse=True):
                            if sub.is_file() and sub.suffix == ".md":
                                top_programs[prog]["files"].append(sub)
                            elif sub.is_dir():
                                if is_run_folder(sub.name):
                                    # standard TICKER_DATE_TIME run
                                    files = sorted(sub.rglob("*.md")) + sorted(sub.rglob("*.txt"))
                                    if files:
                                        ticker, date_str, time_str = parse_run(sub)
                                        runs.append({
                                            "name": sub.name, "path": sub, "files": files,
                                            "ticker": ticker, "date": date_str, "time": time_str,
                                            "program": prog,
                                        })
                                else:
                                    # non-standard subfolder — show as named collapsible session
                                    session_files = sorted(sub.rglob("*.md")) + sorted(sub.rglob("*.txt"))
                                    if session_files:
                                        top_programs[prog]["sessions"][sub.name] = session_files
                    except PermissionError:
                        pass
        except OSError:
            continue

    return runs, sorted(top_default, reverse=True), top_programs


def filter_runs(runs, program):
    if not program or program == "all":
        return runs
    return [r for r in runs if r["program"] == program]


# ── Nav builders ───────────────────────────────────────────────────────────

def run_row(run, current_path):
    files = run["files"]
    count = len(files)
    has_current = current_path and any(f == current_path for f in files)
    hdr_cls = " has-current" if has_current else ""

    meta = load_meta(run["path"])
    rb = rating_badge(meta.get("rating", ""))
    mb = mode_badge(meta.get("mode", ""))

    html = (f'<div class="nav-run-hdr{hdr_cls}">'
            f'<span class="nav-run-chevron">▶</span>'
            f'<span class="nav-run-time">{fmt_time(run["time"])}</span>'
            f'{rb}{mb}'
            f'<span class="nav-run-count">{count}f</span>'
            f'</div>')
    html += '<div class="nav-run-body">'
    for f in files:
        rel = f.relative_to(REPORTS_DIR)
        label = str(f.relative_to(run["path"]))
        cls = " current" if current_path and f == current_path else ""
        html += f'<a class="nav-file{cls}" href="/view/{rel}" title="{label}">{label}</a>'
    html += '</div>'
    return html


def build_nav_date(runs, current_path):
    by_date = defaultdict(lambda: defaultdict(list))
    for run in runs:
        by_date[run["date"]][run["ticker"]].append(run)

    html = '<div id="nav-date" class="nav-panel">'
    for date in sorted(by_date.keys(), reverse=True):
        by_ticker = by_date[date]
        tickers = " · ".join(sorted(by_ticker.keys()))
        html += '<div class="nav-section">'
        html += (f'<div class="nav-section-hdr">'
                 f'<span class="nav-chevron">▶</span>'
                 f'<span class="nav-section-label">{fmt_date(date)}</span>'
                 f'<span class="nav-section-meta">{tickers}</span>'
                 f'</div>')
        html += '<div class="nav-section-body">'
        for ticker in sorted(by_ticker.keys()):
            t_runs = sorted(by_ticker[ticker], key=lambda r: r["time"])
            html += (f'<div class="nav-symbol-hdr">'
                     f'<span class="nav-symbol-chevron">▶</span>'
                     f'<span class="nav-symbol-name">{ticker}</span>'
                     f'<span class="nav-symbol-count">{len(t_runs)}</span>'
                     f'</div>')
            html += '<div class="nav-symbol-body">'
            for run in t_runs:
                html += run_row(run, current_path)
            html += '</div>'
        html += '</div></div>'
    html += '</div>'
    return html


def build_nav_symbol(runs, current_path):
    by_ticker = defaultdict(lambda: defaultdict(list))
    for run in runs:
        by_ticker[run["ticker"]][run["date"]].append(run)

    html = '<div id="nav-symbol" class="nav-panel">'
    for ticker in sorted(by_ticker.keys()):
        by_date = by_ticker[ticker]
        total = sum(len(v) for v in by_date.values())
        html += '<div class="nav-section">'
        html += (f'<div class="nav-section-hdr">'
                 f'<span class="nav-chevron">▶</span>'
                 f'<span class="nav-section-label">{ticker}</span>'
                 f'<span class="nav-section-meta">{total} runs</span>'
                 f'</div>')
        html += '<div class="nav-section-body">'
        for date in sorted(by_date.keys(), reverse=True):
            d_runs = sorted(by_date[date], key=lambda r: r["time"])
            html += (f'<div class="nav-date-hdr">'
                     f'<span class="nav-date-chevron">▶</span>'
                     f'<span class="nav-date-label">{fmt_date(date)}</span>'
                     f'<span class="nav-date-count">{len(d_runs)}</span>'
                     f'</div>')
            html += '<div class="nav-date-body">'
            for run in d_runs:
                html += run_row(run, current_path)
            html += '</div>'
        html += '</div></div>'
    html += '</div>'
    return html


def build_nav_top(top_default, top_programs, current_path, program):
    html = ""

    # ── Direct .md files section (only for specific program or default) ──────
    if program == "default":
        files = list(top_default)
    elif program != "all":
        files = list(top_programs.get(program, {}).get("files", []))
    else:
        files = []

    if files:
        html += '<div class="nav-top-files"><div class="nav-top-label">Reference Files</div>'
        for f in sorted(files, key=lambda x: x.name, reverse=True):
            rel = f.relative_to(REPORTS_DIR)
            cls = "nav-file current" if current_path and f == current_path else "nav-file"
            html += f'<a class="{cls}" href="/view/{rel}">{f.name}</a>'
        html += '</div>'

    # ── Session folders (non-run subfolders) ───────────────────────────────
    if program == "all":
        sessions_by_prog = {}
    elif program == "default":
        sessions_by_prog = {}
    else:
        pdata = top_programs.get(program, {})
        sessions_by_prog = {program: pdata.get("sessions", {})} if pdata.get("sessions") else {}

    for prog_name, sessions in sessions_by_prog.items():
        for session_name, session_files in sorted(sessions.items(), reverse=True):
            has_current = current_path and any(f == current_path for f in session_files)
            hdr_cls = " has-current" if has_current else ""
            count = len(session_files)
            html += '<div class="nav-section">'
            html += (f'<div class="nav-section-hdr{hdr_cls}">'
                     f'<span class="nav-chevron">▶</span>'
                     f'<span class="nav-section-label">{session_name}</span>'
                     f'<span class="nav-section-meta">{count}f</span>'
                     f'</div>')
            html += '<div class="nav-section-body">'
            for f in session_files:
                rel = f.relative_to(REPORTS_DIR)
                cls = "nav-file current" if current_path and f == current_path else "nav-file"
                html += f'<a class="{cls}" href="/view/{rel}">{f.name}</a>'
            html += '</div></div>'

    return html


def build_program_options(top_programs, current_program):
    sel = lambda p: ' selected' if p == current_program else ''
    html = f'<option value="all"{sel("all")}>All Programs</option>'
    html += f'<option value="default"{sel("default")}>Default</option>'
    for prog in sorted(top_programs.keys()):
        html += f'<option value="{prog}"{sel(prog)}>{prog_label(prog)}</option>'
    return html


def build_nav(runs, top_default, top_programs, current_path, program):
    filtered = filter_runs(runs, program)
    nav_top = build_nav_top(top_default, top_programs, current_path, program)
    nav_date = build_nav_date(filtered, current_path)
    nav_symbol = build_nav_symbol(filtered, current_path)
    return nav_top, nav_date, nav_symbol


def build_nav_kb(current_path):
    if not KB_DIR.exists():
        return ""
    files = sorted(KB_DIR.glob("*.md"), key=lambda f: f.name)
    if not files:
        return ""
    html = '<div class="nav-kb"><div class="nav-kb-label">Knowledge Base</div>'
    for f in files:
        name = f.stem.replace("_", " ").title()
        cls = " current" if current_path and f == current_path else ""
        html += f'<a class="nav-file{cls}" href="/kb/{f.name}" title="{f.name}">{name}</a>'
    html += '</div>'
    return html


def build_nav_checks(current_path):
    files = sorted(CHECKS_DIR.glob("LAST_*.md"), key=lambda f: f.name)
    if not files:
        return ""
    html = '<div class="nav-checks"><div class="nav-checks-label">Live Checks</div>'
    for f in files:
        name = f.stem.replace("_", " ").title()
        cls = " current" if current_path and f == current_path else ""
        html += f'<a class="nav-file{cls}" href="/checks/{f.name}" title="{f.name}">{name}</a>'
    html += '</div>'
    return html


# ── Routes ─────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    runs, top_default, top_programs = get_runs()
    program = request.args.get("program", "all")
    nav_top, nav_date, nav_symbol = build_nav(runs, top_default, top_programs, None, program)
    nav_kb = build_nav_kb(None)
    nav_checks = build_nav_checks(None)
    program_options = build_program_options(top_programs, program)
    total = len(filter_runs(runs, program))
    content = (
        '<div class="welcome">'
        '<h2>Trading Analysis Reports</h2>'
        f'<p>{total} run{"s" if total != 1 else ""} — select one from the sidebar</p>'
        '</div>'
    )
    return render_template_string(
        BASE_HTML, title="Reports",
        nav_top=nav_top, nav_date=nav_date, nav_symbol=nav_symbol,
        nav_kb=nav_kb, nav_checks=nav_checks, program_options=program_options, content=content,
    )


@app.route("/nav_fragment")
def nav_fragment():
    """Return sidebar scroll content for the selected program — used by AJAX program filter."""
    runs, top_default, top_programs = get_runs()
    program = request.args.get("program", "all")
    nav_top, nav_date, nav_symbol = build_nav(runs, top_default, top_programs, None, program)
    nav_kb = build_nav_kb(None)
    nav_checks = build_nav_checks(None)
    return nav_top + nav_date + nav_symbol + nav_checks + nav_kb


@app.route("/view/<path:relpath>")
def view_file(relpath):
    filepath = REPORTS_DIR / relpath
    if not filepath.exists() or not filepath.is_file():
        abort(404)
    try:
        filepath.resolve().relative_to(REPORTS_DIR.resolve())
    except ValueError:
        abort(403)

    runs, top_default, top_programs = get_runs()
    program = request.args.get("program", "all")
    nav_top, nav_date, nav_symbol = build_nav(runs, top_default, top_programs, filepath, program)
    nav_kb = build_nav_kb(None)
    nav_checks = build_nav_checks(None)
    program_options = build_program_options(top_programs, program)

    text = filepath.read_text(encoding="utf-8", errors="replace")
    if filepath.suffix == ".md":
        body = md.markdown(text, extensions=["tables", "fenced_code", "nl2br"])
        file_content = f'<div class="content">{body}</div>'
    else:
        file_content = f'<div class="pre">{text}</div>'

    breadcrumb = f'<div class="breadcrumb"><a href="/">Home</a> / {relpath}</div>'
    content = breadcrumb + f"<h1>{filepath.name}</h1>" + file_content

    return render_template_string(
        BASE_HTML, title=filepath.name,
        nav_top=nav_top, nav_date=nav_date, nav_symbol=nav_symbol,
        nav_kb=nav_kb, nav_checks=nav_checks, program_options=program_options, content=content,
    )


def render_file_content(relpath):
    filepath = REPORTS_DIR / relpath
    if not filepath.exists() or not filepath.is_file():
        return None
    try:
        filepath.resolve().relative_to(REPORTS_DIR.resolve())
    except ValueError:
        return None
    text = filepath.read_text(encoding="utf-8", errors="replace")
    if filepath.suffix == ".md":
        body = md.markdown(text, extensions=["tables", "fenced_code", "nl2br"])
        file_content = f'<div class="content">{body}</div>'
    else:
        file_content = f'<div class="pre">{text}</div>'
    breadcrumb = f'<div class="breadcrumb"><a href="/">Home</a> / {relpath}</div>'
    return breadcrumb + f"<h1>{filepath.name}</h1>" + file_content


@app.route("/fragment/<path:relpath>")
def fragment(relpath):
    html = render_file_content(relpath)
    if html is None:
        abort(404)
    return html


@app.route("/kb/<path:filename>")
def view_kb_file(filename):
    filepath = KB_DIR / filename
    if not filepath.exists() or not filepath.is_file():
        abort(404)
    try:
        filepath.resolve().relative_to(KB_DIR.resolve())
    except ValueError:
        abort(403)

    runs, top_default, top_programs = get_runs()
    program = request.args.get("program", "all")
    nav_top, nav_date, nav_symbol = build_nav(runs, top_default, top_programs, None, program)
    nav_kb = build_nav_kb(filepath)
    nav_checks = build_nav_checks(None)
    program_options = build_program_options(top_programs, program)

    text = filepath.read_text(encoding="utf-8", errors="replace")
    body = md.markdown(text, extensions=["tables", "fenced_code", "nl2br"])
    file_content = f'<div class="content">{body}</div>'
    title = filepath.stem.replace("_", " ").title()
    breadcrumb = f'<div class="breadcrumb"><a href="/">Home</a> / Knowledge Base / {filepath.name}</div>'
    content = breadcrumb + f"<h1>{title}</h1>" + file_content

    return render_template_string(
        BASE_HTML, title=title,
        nav_top=nav_top, nav_date=nav_date, nav_symbol=nav_symbol,
        nav_kb=nav_kb, nav_checks=nav_checks, program_options=program_options, content=content,
    )


@app.route("/kb_fragment/<path:filename>")
def kb_fragment(filename):
    filepath = KB_DIR / filename
    if not filepath.exists() or not filepath.is_file():
        abort(404)
    try:
        filepath.resolve().relative_to(KB_DIR.resolve())
    except ValueError:
        abort(403)
    text = filepath.read_text(encoding="utf-8", errors="replace")
    body = md.markdown(text, extensions=["tables", "fenced_code", "nl2br"])
    file_content = f'<div class="content">{body}</div>'
    title = filepath.stem.replace("_", " ").title()
    breadcrumb = f'<div class="breadcrumb"><a href="/">Home</a> / Knowledge Base / {filepath.name}</div>'
    return breadcrumb + f"<h1>{title}</h1>" + file_content


@app.route("/checks/<path:filename>")
def view_checks_file(filename):
    filepath = CHECKS_DIR / filename
    if not filepath.exists() or not filepath.is_file():
        abort(404)
    try:
        filepath.resolve().relative_to(CHECKS_DIR.resolve())
    except ValueError:
        abort(403)

    runs, top_default, top_programs = get_runs()
    program = request.args.get("program", "all")
    nav_top, nav_date, nav_symbol = build_nav(runs, top_default, top_programs, None, program)
    nav_kb = build_nav_kb(None)
    nav_checks = build_nav_checks(filepath)
    program_options = build_program_options(top_programs, program)

    text = filepath.read_text(encoding="utf-8", errors="replace")
    body = md.markdown(text, extensions=["tables", "fenced_code", "nl2br"])
    file_content = f'<div class="content">{body}</div>'
    title = filepath.stem.replace("_", " ").title()
    breadcrumb = f'<div class="breadcrumb"><a href="/">Home</a> / Live Checks / {filepath.name}</div>'
    content = breadcrumb + f"<h1>{title}</h1>" + file_content

    return render_template_string(
        BASE_HTML, title=title,
        nav_top=nav_top, nav_date=nav_date, nav_symbol=nav_symbol,
        nav_kb=nav_kb, nav_checks=nav_checks, program_options=program_options, content=content,
    )


@app.route("/checks_fragment/<path:filename>")
def checks_fragment(filename):
    filepath = CHECKS_DIR / filename
    if not filepath.exists() or not filepath.is_file():
        abort(404)
    try:
        filepath.resolve().relative_to(CHECKS_DIR.resolve())
    except ValueError:
        abort(403)
    text = filepath.read_text(encoding="utf-8", errors="replace")
    body = md.markdown(text, extensions=["tables", "fenced_code", "nl2br"])
    file_content = f'<div class="content">{body}</div>'
    title = filepath.stem.replace("_", " ").title()
    breadcrumb = f'<div class="breadcrumb"><a href="/">Home</a> / Live Checks / {filepath.name}</div>'
    return breadcrumb + f"<h1>{title}</h1>" + file_content


if __name__ == "__main__":
    print(f"Serving reports from: {REPORTS_DIR}")
    print("Open: http://<your-server-ip>:5555")
    app.run(host="0.0.0.0", port=5555, debug=False)
