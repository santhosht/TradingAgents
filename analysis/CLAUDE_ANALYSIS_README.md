# Analyse stocks with Claude (no API needed)

## One-time setup

```bash
cp .env.example .env
# Edit .env — set GOOGLE_API_KEY and uncomment the 3 Gemini lines
```

## Daily usage

```bash
source .venv/bin/activate
python fetch_data.py AMD        # replace AMD with any ticker
```

Then tell Claude Code:

> Analyse AMD using ANALYSIS_PROCESS.md

Claude Code reads `ANALYSIS_PROCESS.md` as its playbook and runs the full analysis, writing reports to `analysis/data/reports/`.

---

## Reports Viewer

A local web UI for browsing analysis reports in `analysis/data/reports/`. Reads files on-the-fly — new reports appear automatically without restarting.

### Start the viewer

```bash
nohup .venv/bin/python reports_viewer.py > reports_viewer.log 2>&1 &
```

Open **`http://<your-server-ip>:5555`** in a browser.

### Features

- **By Date / By Symbol** toggle — switch grouping in the sidebar; preference saved across sessions
- **4-level tree**: Day → Symbol → Run (time) → individual files
- **AJAX navigation** — clicking a file loads content without page reload; sidebar stays expanded
- **Timestamps in ET** — UTC folder names are converted to Eastern Time for display and grouping
- **Dark / light theme** toggle (top-right of sidebar); preference saved
- **Live** — new run folders appear on the next page load, no restart needed

### Stop the viewer

```bash
pkill -f reports_viewer.py
```

### Check logs

```bash
tail -f reports_viewer.log
```
