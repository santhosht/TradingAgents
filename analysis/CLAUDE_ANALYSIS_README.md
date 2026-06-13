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

---

## Process Comparison: Morning Check vs Stop Check vs Entry Check vs Position Tracking

| | Morning Check | Stop Check | Entry Check | Position Tracking |
|---|---|---|---|---|
| **Trigger** | "morning check" | "stop check" / "check stops" | "entry check" / "check positions" / "position monitor" | "how is X doing?" / ticker question |
| **Scope** | All positions | Open + Orders Placed | Open + Orders Placed + Pending | One symbol at a time |
| **Open positions** | ✓ | ✓ | ✓ | ✓ |
| **Orders Placed** | ✓ | ✓ | ✓ | ✓ |
| **Pending positions** | ✓ | ✗ | ✓ | ✓ |
| **Reads decision.md** | ✓ | ✗ | ✗ | ✓ (always) |
| **Reads manager.md** | ✓ | ✗ | ✗ | ✓ (if needed) |
| **Reads news.md** | ✓ | ✗ | ✗ | ✗ |
| **Reads fundamentals.md** | ✗ | ✗ | ✗ | ✓ (if needed) |
| **Live news fetch** | ✓ Finviz + WebSearch | ✗ | ✓ WebSearch | ✓ Finviz |
| **4-source web fetch** | ✗ | ✗ | ✗ | ✓ (Yahoo + Finviz + StockAnalysis ×2) |
| **Entry confidence rating** | ✓ HIGH/MED/LOW/NO ENTRY | ✗ | basic zone check | ✗ |
| **Interactive (asks which symbols)** | ✓ | ✗ | ✗ | ✓ |
| **Speed** | Slow | Fast | Medium | Medium |
| **Saves output file** | ✗ | `data/checks/LAST_STOP_CHECK.md` | `data/checks/LAST_ENTRY_CHECK.md` | ✗ |

### What each process is for

- **Morning Check** — Start-of-day review. Interactive, thesis-aware, reads full reports, gives entry confidence ratings. Most thorough.
- **Stop Check** — Fast price-only alert. Are stops hit? Targets near? No report reading, no news. Use intraday.
- **Entry Check** — Stop check + pending entry scan with live news. Are any pending entries now in zone or breaking out?
- **Position Tracking** — Deep dive on one stock. Reads the decision report, fetches 4 live data sources, full thesis + action recommendation.

### Who reads the output files

`LAST_STOP_CHECK.md` and `LAST_ENTRY_CHECK.md` are written by Stop Check and Entry Check respectively. They are **not read by any of the 4 processes** — they are consumed by the **Reports Viewer UI** (sidebar "Live Checks" section) for persistent reference between runs.
