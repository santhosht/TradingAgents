# Agent Account — Work in Progress Notes

## What this folder is

Process files for managing a $1000 Robinhood agent account (separate from main portfolio).
These are NOT yet wired into CLAUDE.md — still being refined.

---

## What we built

### SWING_CHECK.md
- Triggered manually: "swing check SYMBOL"
- Reads existing decision.md (no full re-analysis)
- Fetches live price + Finviz news
- Answers 5 swing questions: momentum, catalyst, entry trigger, ATR days to T1, resistance
- Scores conviction: High / Medium / Low
- Outputs exact order parameters (entry, stop, target, shares, R:R)
- If no analysis found → stops, tells user to run full analysis first
- Output written to: `analysis/data/checks/swing/SYMBOL.md`

### AGENT_ACCOUNT.md
- Triggered manually: "agent scan" or "agent account"
- Step 1: Fetch agent account state via Robinhood MCP (cash, positions, open orders)
- Step 2: Scan all report folders, filter stale (>10 days) + Underweight + already trading
- Step 3: Run swing check on all candidates in parallel
- Step 4: Rank by conviction, allocate (not equal — by conviction score)
- Step 5: Place 3 orders per symbol via MCP (buy limit + stop sell + target sell)
- Step 6: Print summary
- Step 7: Re-run every 2–3 days

---

## Key decisions made

- Fractional shares are fine — no minimum
- Do NOT force deploy all cash — idle cash is okay if signals are weak
- Swing target = T1 from existing analysis (not T2)
- If ATR days to T1 > 14 → use midpoint between entry and T1 instead
- Agent account is completely separate from main POSITIONS.md — never update POSITIONS.md for agent trades
- Conviction scoring: High ($250–300) / Medium ($150–200) / Low ($75–100)
- Stale analysis cutoff: 10 trading days

---

## What is NOT done yet / pending

1. **MCP connection not verified** — Robinhood MCP needs to be confirmed in Claude Code session
   - Run: `! cat .claude/settings.json` to check
   - Need to confirm: can MCP read portfolio state (positions, cash)?
   - Need to confirm: does MCP support stop-loss and limit sell orders?

2. **CLAUDE.md not updated** — intentionally held back until process is solid
   - When ready, add SWING_CHECK.md and AGENT_ACCOUNT.md entries
   - Triggers: "swing check SYMBOL" and "agent scan"

3. **Swing check outputs need conviction score added** — the 4 outputs already written
   (AMZN, AAPL, GOOGL, NVDA in `analysis/data/checks/swing/`) were written before
   conviction scoring was added. They need updating when re-run.

4. **Process not tested end-to-end** — swing check was tested manually on 4 symbols.
   Agent account full scan (AGENT_ACCOUNT.md) has NOT been tested yet.

---

## Current swing check results (as of 2026-06-15)

| Symbol | Decision | Conviction | Reason |
|--------|----------|-----------|--------|
| NVDA | 🟢 BUY | High | S&P upgrade, GPU deals, volume collapsing |
| GOOGL | 🟢 BUY | Medium-High | 2 green days, selling exhaustion |
| AMZN | ⏳ WAIT | — | MACD still falling |
| AAPL | ⏳ WAIT | — | Tata contamination key risk active |

Next action: verify MCP → place NVDA and GOOGL orders.

---

## Next session — where to start

1. Check MCP connection (`! cat .claude/settings.json`)
2. If MCP connected → run "agent scan" to test full process
3. If MCP not connected → set it up first (Robinhood MCP settings)
4. After successful test → update CLAUDE.md to wire in both process files
