# TradingAgents — Project Instructions

## Process Files
- `analysis/ANALYSIS_PROCESS.md` — full pipeline for running a new stock analysis. Never skip steps, never carry state between runs.
- `analysis/POSITION_TRACKING.md` — how to manage, review, and update positions. Read this before any position-related response.
- `analysis/MORNING_CHECK.md` — daily morning check process. Read this when user says "morning check".
- `analysis/TRADING_LEARNINGS.md` — log of lessons from real trades. Context only — not a rulebook. Suggest additions when new lessons emerge from analysis or real trades.

## Data Files
- `analysis/data/POSITIONS.md` — user's live open/closed/pending positions. Always check this when the user asks about a ticker or position.

## When to Read What

| User asks... | Read first |
|---|---|
| Analyze a new stock | `analysis/ANALYSIS_PROCESS.md` |
| About an existing position / ticker | `analysis/POSITION_TRACKING.md` |
| Review past trade learnings | `analysis/TRADING_LEARNINGS.md` |
| Says "morning check" | `analysis/MORNING_CHECK.md` |

## MANDATORY: Position Review Protocol

When the user asks ANYTHING about how a position is doing, its status, or whether to hold/exit — you MUST:

1. Read `analysis/data/POSITIONS.md` (get entry price, stop, targets, report folder)
2. Read `analysis/POSITION_TRACKING.md` (follow every step — do NOT skip)
3. Read `analysis/data/reports/SYMBOL_.../5_portfolio/decision.md`
4. Fetch all 4 data URLs in parallel (Yahoo Finance quote, Finviz, StockAnalysis financials, StockAnalysis overview)
5. Deliver the update in the exact format defined in `analysis/POSITION_TRACKING.md` Step 4

**Skipping any of these steps is wrong.** The format and data fetching are not optional.

## MANDATORY: Morning Check Protocol

When the user says **"morning check"**:

1. Read `analysis/MORNING_CHECK.md` — follow every step exactly
2. Follow every step exactly — do NOT skip or shortcut
3. Never update any MD files during morning check unless user explicitly asks
4. Only update analysis/data/POSITIONS.md at end of session when user asks to
