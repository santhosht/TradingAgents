# TradingAgents — Project Instructions

## Process Files

- `analysis/ANALYSIS_PROCESS.md` — full pipeline for running a new stock analysis. Never skip steps, never carry state between runs.
- `analysis/POSITION_TRACKING.md` — how to manage, review, and update positions. Read this before any position-related response.
- `analysis/STOP_CHECK.md` — quick intraday snapshot: all open positions + orders placed vs stops and targets. Read when user says "stop check" or "check stops".
- `analysis/DAILY_SCAN.md` — start-of-day full portfolio scan: open positions, orders placed, pending entries, news. Read when user says "daily scan".
- `analysis/THESIS_CHECK.md` — deep dive on a specific symbol before acting: reads existing report, fresh price, deep news, gives one clear action recommendation. Read when user says "thesis check SYMBOL".
- `analysis/STALE_CLEANUP.md` — cleanup stale pending positions. Read when user says "cleanup stale", "clean pending", or "stale cleanup".
- `analysis/TRADING_LEARNINGS.md` — log of lessons from real trades. Context only — not a rulebook. Suggest additions when new lessons emerge from analysis or real trades.

## Data Files

- `analysis/data/POSITIONS.md` — user's live open/closed/pending positions. Always check this when the user asks about a ticker or position.
- `analysis/data/checks/LAST_STOP_CHECK.md` — latest stop check snapshot output
- `analysis/data/checks/LAST_DAILY_SCAN.md` — latest daily scan output (thesis check reads this)
- `analysis/data/checks/thesis/SYMBOL.md` — latest thesis check output per symbol

## Knowledge Base

- `analysis/data/knowledge_base/` — macro and industry research documents. Not stock-specific. Use when user asks about sectors, themes, or industries, or when context from a knowledge base doc would improve stock analysis.
- When user asks to save/add industry research or a thematic analysis, write it here as a new `.md` file.

## Daily Routine (for reference)

| When | What to run | How |
|---|---|---|
| Throughout day | Stop check | "stop check" |
| Start of day | Daily scan | "daily scan" |
| When daily scan flags something | Thesis check | "thesis check SYMBOL" |
| New trade research | Full analysis | "analyse TICKER" |

## POSITIONS.md — Section Definitions

| Section | Meaning |
|---|---|
| **Open Positions** | Limit/order filled; position is live in the broker |
| **Orders Placed** | Limit order submitted to broker; awaiting fill — NOT pending analysis |
| **Pending** | Analysis done, entry recommended, but NO order placed yet |
| **Closed** | Exited positions |

- When user says "I placed a limit order for X": move X from Pending → Orders Placed
- When user says "filled" or "it filled": move from Orders Placed → Open Positions (add actual fill price)
- Orders Placed entries are NOT stale in the same way as Pending — do not clean them up on stale sweeps; only remove if user cancels the order or it expires

## When to Read What

| User says... | Read |
|---|---|
| "analyse TICKER" / new stock | `analysis/ANALYSIS_PROCESS.md` |
| About an existing position / ticker | `analysis/POSITION_TRACKING.md` |
| "stop check" / "check stops" | `analysis/STOP_CHECK.md` |
| "daily scan" | `analysis/DAILY_SCAN.md` |
| "thesis check SYMBOL" | `analysis/THESIS_CHECK.md` |
| "cleanup stale" / "clean pending" / "stale cleanup" | `analysis/STALE_CLEANUP.md` |
| Review past trade learnings | `analysis/TRADING_LEARNINGS.md` |

## MANDATORY: Position Review Protocol

When the user asks ANYTHING about how a position is doing, its status, or whether to hold/exit — you MUST:

1. Read `analysis/data/POSITIONS.md` (get entry price, stop, targets, report folder)
2. Read `analysis/POSITION_TRACKING.md` (follow every step — do NOT skip)
3. Read `analysis/data/reports/SYMBOL_.../5_portfolio/decision.md`
4. Fetch all 4 data URLs in parallel (Yahoo Finance quote, Finviz, StockAnalysis financials, StockAnalysis overview)
5. Deliver the update in the exact format defined in `analysis/POSITION_TRACKING.md` Step 4

**Skipping any of these steps is wrong.** The format and data fetching are not optional.

## MANDATORY: Daily Scan Protocol

When the user says **"daily scan"**:

1. Read `analysis/DAILY_SCAN.md` — follow every step exactly
2. Fetch all symbols in parallel — do not serialize
3. Never update POSITIONS.md unless user confirms an action
4. Always write `analysis/data/checks/LAST_DAILY_SCAN.md` at the end

## MANDATORY: Thesis Check Protocol

When the user says **"thesis check SYMBOL"**:

1. Read `analysis/THESIS_CHECK.md` — follow every step exactly
2. Check if `analysis/data/checks/LAST_DAILY_SCAN.md` was written today — reuse data if so
3. Always fetch a fresh live price regardless
4. Never block on stale analysis — highlight it in output and continue
5. Always write `analysis/data/checks/thesis/SYMBOL.md` at the end
