# Stale Positions Cleanup Process

**Trigger:** User says "cleanup stale", "clean pending", or "stale cleanup"

**Key rules:**
- Only affects **Pending** positions — never touch Open, Orders Placed, or Closed positions
- Orders Placed are active broker orders — do NOT remove them during stale cleanup; they expire on their own GTC date
- Always show the full stale list before taking any action
- Only update POSITIONS.md after user confirms action for each symbol
- Re-run means triggering ANALYSIS_PROCESS.md — do not do it silently

---

## Step 1 — Read POSITIONS.md and find stale pending symbols

Read POSITIONS.md. For each **Pending** symbol extract (skip Open and Orders Placed entirely):
- Report age (trading days only, Mon–Fri) — from the report folder date
- Entry zone
- Any catalyst noted (e.g. "STALE AFTER date" or "post-earnings" notes)

Stale = report age > 10 trading days.

If no stale pending symbols found:
```
"No stale pending positions. All pending reports are within 10 trading days."
```
Stop here.

---

## Step 2 — List stale symbols and ask what to do

Show all stale pending symbols with their age, entry zone, and any passed catalyst noted in POSITIONS.md:

```
"Stale pending positions (>10 trading days old):

  1. ADBE  — 14 trading days old — entry zone $248–$252 — ⚠ earnings passed Jun 11
  2. LULU  — 12 trading days old — entry zone $110–$114.50

  For each symbol choose:
  A) Remove — delete from POSITIONS.md
  B) Re-run — run fresh analysis (say 'analyse SYMBOL')
  C) Keep   — leave as-is for now

  What would you like to do with each?"
```

Wait for user to respond for all symbols before taking any action.

---

## Step 3 — Execute per symbol

For each symbol based on user's choice:

| Choice | Action |
|--------|--------|
| Remove | Delete the symbol's entry from POSITIONS.md Pending section |
| Re-run | Note to re-run — tell user "say 'analyse SYMBOL' to start fresh analysis" |
| Keep   | No change |

Execute all Removes first, then report what needs re-running.

---

## Step 4 — Confirm and show updated list

After all actions are done, show the updated pending list:

```
"Done. Updated pending positions:

 Removed: ADBE, LULU
 Re-run needed: (none)
 Kept: INTU, NKE

 Remaining pending positions:
   1. INTU — 8 trading days old — entry zone $293–$297
   2. NKE  — 8 trading days old — entry zone $42.50–$43.50"
```
