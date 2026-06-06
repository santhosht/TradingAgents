#!/usr/bin/env python3
"""Dynamic reports viewer — reads files on-the-fly, no conversion needed."""

from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from flask import Flask, abort, render_template_string
import markdown as md

ET = ZoneInfo("America/New_York")

REPORTS_DIR = Path(__file__).parent / "reports"

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
    }
    :root[data-theme="light"] {
      --bg: #f5f6fa; --sidebar-bg: #ffffff; --border: #dde1f0;
      --text: #1a1d2e; --muted: #999; --accent: #4a52e0;
      --code-bg: #eef0fb; --code-color: #b05c00; --even-row: #f0f2fc;
      --pre-color: #2a2d3e; --heading: #2a2d8e;
      --hover-bg: #eef0fb; --current-bg: #dde4ff;
      --day-bg: #f0f2fc; --symbol-bg: #e8eaf8;
      --welcome-border: #dde1f0;
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
  </style>
</head>
<body>
<div class="sidebar">
  <div class="sidebar-top">
    <div class="sidebar-title-row">
      <span class="sidebar-title">Trading Reports</span>
      <button class="theme-btn" id="theme-btn" onclick="toggleTheme()">☀️</button>
    </div>
    <div class="view-toggle">
      <button class="view-btn" data-view="date" onclick="setView('date')">By Date</button>
      <button class="view-btn" data-view="symbol" onclick="setView('symbol')">By Symbol</button>
    </div>
  </div>
  <div class="sidebar-scroll">
    {{ nav_date | safe }}
    {{ nav_symbol | safe }}
    {{ nav_top | safe }}
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
  bindToggle('.nav-section-hdr');
  bindToggle('.nav-symbol-hdr');
  bindToggle('.nav-date-hdr');
  bindToggle('.nav-run-hdr');

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
      // open first section of active panel only on initial load
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
    // walk up and open every collapsed ancestor
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
    try {
      const res = await fetch('/fragment' + href.replace(/^\/view/, ''));
      if (!res.ok) { window.location = href; return; }
      const html = await res.text();
      mainEl.innerHTML = html;
      if (pushState) history.pushState({ href }, '', href);
      activateFile(href);
      document.title = href.split('/').pop();
      // scroll main to top
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

  // seed history state for current page
  history.replaceState({ href: location.pathname }, '', location.pathname);
</script>
</body>
</html>"""


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


def get_runs():
    runs = []
    for entry in sorted(REPORTS_DIR.iterdir(), reverse=True):
        if entry.is_dir():
            files = sorted(entry.rglob("*.md")) + sorted(entry.rglob("*.txt"))
            if files:
                ticker, date_str, time_str = parse_run(entry)
                runs.append({
                    "name": entry.name, "path": entry, "files": files,
                    "ticker": ticker, "date": date_str, "time": time_str,
                })
    top = sorted(REPORTS_DIR.glob("*.md"), reverse=True)
    return runs, top


def run_row(run, current_path):
    """Expandable run row showing time + all files inside."""
    files = run["files"]
    count = len(files)
    # check if any file in this run is the current one
    has_current = current_path and any(f == current_path for f in files)
    hdr_cls = " has-current" if has_current else ""

    html = (f'<div class="nav-run-hdr{hdr_cls}">'
            f'<span class="nav-run-chevron">▶</span>'
            f'<span class="nav-run-time">{fmt_time(run["time"])}</span>'
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
        total = sum(len(v) for v in by_ticker.values())
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


def build_nav_top(top, current_path):
    if not top:
        return ""
    html = '<div class="nav-top-files"><div class="nav-top-label">Top-level</div>'
    for f in top:
        rel = f.relative_to(REPORTS_DIR)
        cls = " current" if current_path and f == current_path else ""
        html += f'<a class="{cls}" href="/view/{rel}">{f.name}</a>'
    html += '</div>'
    return html


@app.route("/")
def index():
    runs, top = get_runs()
    nav_date = build_nav_date(runs, None)
    nav_symbol = build_nav_symbol(runs, None)
    nav_top = build_nav_top(top, None)
    total = len(runs)
    content = (
        '<div class="welcome">'
        '<h2>Trading Analysis Reports</h2>'
        f'<p>{total} run{"s" if total != 1 else ""} — select one from the sidebar</p>'
        '</div>'
    )
    return render_template_string(
        BASE_HTML, title="Reports",
        nav_date=nav_date, nav_symbol=nav_symbol, nav_top=nav_top,
        content=content, current_path=None,
    )


@app.route("/view/<path:relpath>")
def view_file(relpath):
    filepath = REPORTS_DIR / relpath
    if not filepath.exists() or not filepath.is_file():
        abort(404)
    try:
        filepath.resolve().relative_to(REPORTS_DIR.resolve())
    except ValueError:
        abort(403)

    runs, top = get_runs()
    nav_date = build_nav_date(runs, filepath)
    nav_symbol = build_nav_symbol(runs, filepath)
    nav_top = build_nav_top(top, filepath)

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
        nav_date=nav_date, nav_symbol=nav_symbol, nav_top=nav_top,
        content=content, current_path=str(filepath),
    )


def render_file_content(relpath):
    """Return just the main content HTML for a file (no full page wrapper)."""
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
    """Return only the file content HTML — used by AJAX navigation."""
    html = render_file_content(relpath)
    if html is None:
        abort(404)
    return html


if __name__ == "__main__":
    print(f"Serving reports from: {REPORTS_DIR}")
    print("Open: http://<your-server-ip>:5555")
    app.run(host="0.0.0.0", port=5555, debug=False)
