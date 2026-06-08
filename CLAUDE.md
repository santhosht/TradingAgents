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
