# TradingAgents — Project Instructions

## Process Files
- `ANALYSIS_PROCESS.md` — full pipeline for running a new stock analysis. Never skip steps, never carry state between runs.
- `POSITION_TRACKING.md` — how to manage, review, and update positions. Read this before any position-related response.
- `TRADING_RULES.md` — living playbook of rules and lessons from real trades. Suggest updates when new lessons emerge.

## Data Files
- `POSITIONS.md` — user's live open/closed/pending positions. Always check this when the user asks about a ticker or position.

## When to Read What

| User asks... | Read first |
|---|---|
| Analyze a new stock | `ANALYSIS_PROCESS.md` |
| About an existing position / ticker | `POSITIONS.md` → `POSITION_TRACKING.md` |
| What rules apply to a trade | `TRADING_RULES.md` |

## MANDATORY: Position Review Protocol

When the user asks ANYTHING about how a position is doing, its status, or whether to hold/exit — you MUST:

1. Read `POSITIONS.md` (get entry price, stop, targets, report folder)
2. Read `POSITION_TRACKING.md` (follow every step — do NOT skip)
3. Read `reports/SYMBOL_.../5_portfolio/decision.md`
4. Fetch all 4 data URLs in parallel (Yahoo Finance quote, Finviz, StockAnalysis financials, StockAnalysis overview)
5. Deliver the update in the exact format defined in `POSITION_TRACKING.md` Step 4

**Skipping any of these steps is wrong.** The format and data fetching are not optional.
