# TradingAgents — Agent Architecture & Data Flow

## Overview

The system uses **LangGraph** to orchestrate 12 agents across 5 sequential phases.
All inter-agent communication happens through a single shared `AgentState` dict —
no agent calls another directly. External data (market, news, social) is fetched
either via LLM tool calls or pre-fetched into the prompt before the LLM is invoked.

---

## Shared State (`AgentState`)

Every agent reads from and writes to fields in this single state object.

| Field | Type | Description |
|---|---|---|
| `company_of_interest` | str | Ticker symbol (e.g. `AMD`) |
| `trade_date` | str | Analysis date (e.g. `2026-06-07`) |
| `asset_type` | str | `"stock"` or `"crypto"` |
| `instrument_context` | str | Resolved company identity from yfinance (injected at run start) |
| `past_context` | str | Memory log from prior same-ticker runs |
| `messages` | list | LangChain message list (tool calls / responses) |
| `market_report` | str | Written by Market Analyst |
| `sentiment_report` | str | Written by Sentiment Analyst |
| `news_report` | str | Written by News Analyst |
| `fundamentals_report` | str | Written by Fundamentals Analyst |
| `investment_debate_state` | dict | Bull/Bear debate transcript and round count |
| `investment_plan` | str | Written by Research Manager |
| `trader_investment_plan` | str | Written by Trader |
| `risk_debate_state` | dict | Aggressive/Conservative/Neutral debate transcript |
| `final_trade_decision` | str | Written by Portfolio Manager |

### Debate Sub-States

**`InvestDebateState`** (inside `investment_debate_state`):
- `bull_history`, `bear_history`, `history` — cumulative transcripts
- `current_response` — last argument (used by the opposing side)
- `judge_decision` — Research Manager verdict
- `count`, `last_speaker`

**`RiskDebateState`** (inside `risk_debate_state`):
- `aggressive_history`, `conservative_history`, `neutral_history`, `history`
- `current_aggressive_response`, `current_conservative_response`, `current_neutral_response`
- `judge_decision` — Portfolio Manager verdict
- `count`, `latest_speaker`

---

## LLM Assignment

| LLM Role | Used By |
|---|---|
| `quick_thinking_llm` | All 4 analysts, Bull, Bear, Trader, Aggressive, Conservative, Neutral |
| `deep_thinking_llm` | Research Manager, Portfolio Manager (the two judge agents) |

---

## Phase 1 — Analyst Team

Analysts run sequentially (or in parallel if `analyst_concurrency_limit > 1`).
Each analyst clears the `messages` list after writing its report so the next
analyst starts with a clean context.

---

### 1. Market Analyst

**LLM:** `quick_thinking_llm`

**Tools (via LLM tool calls):**
- `get_stock_data` — OHLCV price history from yfinance
- `get_indicators` — stockstats technical indicators (SMA, EMA, MACD, RSI, Bollinger Bands, ATR, VWMA)
- `get_verified_market_snapshot` — authoritative price/indicator snapshot for fact-checking

**Input from state:** `trade_date`, `instrument_context`, `messages`

**Prompt summary:**
> Select up to 8 complementary indicators. Call `get_stock_data` first, then
> `get_indicators`. Call `get_verified_market_snapshot` before writing the final
> report and treat it as the source of truth. Do not claim support/resistance
> bounces or percentage moves unless backed by tool output with concrete dates
> and prices.

**Writes to state:** `market_report`

---

### 2. Sentiment Analyst

**LLM:** `quick_thinking_llm` (with structured output fallback)

**Tools:** None — all data is pre-fetched *before* the LLM is called.

**External data pre-fetched into prompt:**
| Source | What |
|---|---|
| Yahoo Finance news | Institutional headlines, past 7 days |
| StockTwits | Retail posts indexed by cashtag, with user-labeled Bullish/Bearish tags |
| Reddit | Posts from r/wallstreetbets, r/stocks, r/investing — weighted by upvote/comment count |

**Input from state:** `company_of_interest`, `trade_date`, `instrument_context`

**Prompt summary:**
> Analyze three data sources already in this prompt. Read StockTwits
> Bullish/Bearish ratio as a leading retail signal. Look for cross-source
> divergences. Weight Reddit posts by engagement. Distinguish events from
> opinions. Flag data limits honestly in the `confidence` field.
> Output structured fields: `overall_band` (Bullish / Mildly Bullish / Neutral /
> Mixed / Mildly Bearish / Bearish), `overall_score` (0–10), `confidence`
> (low/medium/high), `narrative`.

**Writes to state:** `sentiment_report`

---

### 3. News Analyst

**LLM:** `quick_thinking_llm`

**Tools (via LLM tool calls):**
- `get_news(query, start_date, end_date)` — company-specific or targeted news
- `get_global_news(curr_date, look_back_days, limit)` — broader macro headlines

**Input from state:** `trade_date`, `asset_type`, `instrument_context`, `messages`

**Prompt summary:**
> Research recent news and world trends relevant to trading and macroeconomics
> over the past week. Use both tools — targeted for company-specific queries,
> global for macro context.

**Writes to state:** `news_report`

---

### 4. Fundamentals Analyst

**LLM:** `quick_thinking_llm`

**Tools (via LLM tool calls):**
- `get_fundamentals` — comprehensive company profile and financials
- `get_balance_sheet` — balance sheet data
- `get_cashflow` — cash flow statement
- `get_income_statement` — income statement

**Input from state:** `trade_date`, `instrument_context`, `messages`

**Prompt summary:**
> Write a comprehensive report covering financial documents, company profile,
> financial history. Include balance sheet, cash flow, and income statement
> detail. End with a markdown summary table.

**Writes to state:** `fundamentals_report`

---

## Phase 2 — Research Debate (Bull ↔ Bear)

Both researchers receive all 4 analyst reports from state. They alternate via
LangGraph conditional edges for `max_debate_rounds` rounds.

---

### 5. Bull Researcher

**LLM:** `quick_thinking_llm`

**Tools:** None

**Input from state:**
- `market_report`, `sentiment_report`, `news_report`, `fundamentals_report`
- `investment_debate_state.history` — full debate so far
- `investment_debate_state.current_response` — the Bear's last argument

**Prompt summary:**
> You are a Bull Analyst advocating for investing. Build an evidence-based case
> emphasising growth potential, competitive advantages, and positive indicators.
> Directly counter the Bear's last argument point-by-point. Engage conversationally.

**Writes to state:** Appends to `investment_debate_state.history` and `bull_history`;
sets `current_response` to this argument.

---

### 6. Bear Researcher

**LLM:** `quick_thinking_llm`

**Tools:** None

**Input from state:**
- Same 4 reports + full debate history + last Bull argument

**Prompt summary:**
> You are a Bear Analyst making the case against investing. Emphasise risks,
> challenges, market saturation, financial instability, and negative indicators.
> Directly counter the Bull's last argument. Expose over-optimistic assumptions.

**Writes to state:** Appends to `investment_debate_state.history` and `bear_history`.

---

### 7. Research Manager _(debate judge)_

Runs once after the Bull/Bear debate completes.

**LLM:** `deep_thinking_llm` (with structured output)

**Tools:** None

**Input from state:**
- `investment_debate_state.history` — the complete bull/bear transcript

**Prompt summary:**
> As debate facilitator, critically evaluate the arguments and deliver a clear
> investment plan. Pick exactly one rating from:
> **Buy / Overweight / Hold / Underweight / Sell**
> Commit to a clear stance when evidence warrants; reserve Hold for genuinely
> balanced cases.

**Writes to state:** `investment_plan`, `investment_debate_state.judge_decision`

---

## Phase 3 — Trader

### 8. Trader

**LLM:** `quick_thinking_llm` (with structured output)

**Tools:** None

**Input from state:**
- `investment_plan` — Research Manager's verdict
- `instrument_context`, `company_of_interest`

**Prompt summary:**
> Based on the analysts' investment plan, produce a specific transaction
> proposal: Buy, Sell, or Hold. Ground reasoning in the plan's evidence.

**Writes to state:** `trader_investment_plan`

---

## Phase 4 — Risk Panel Debate

All three risk analysts receive the **trader's proposal** plus all 4 analyst
reports. They cycle via conditional edges for `max_risk_discuss_rounds` rounds
in the order: Aggressive → Conservative → Neutral → Aggressive…

Each agent reads the other two's most recent responses from `risk_debate_state`.

---

### 9. Aggressive Analyst

**LLM:** `quick_thinking_llm`

**Input from state:**
- `trader_investment_plan`
- All 4 analyst reports
- `risk_debate_state.history`
- `current_conservative_response`, `current_neutral_response`

**Prompt summary:**
> Champion high-reward, high-risk opportunities. Emphasise upside and growth
> potential. Directly rebut each point from the Conservative and Neutral
> analysts. Point out where their caution misses critical opportunities.

**Writes to state:** Appends to `risk_debate_state.aggressive_history` and `history`.

---

### 10. Conservative Analyst

**LLM:** `quick_thinking_llm`

**Input from state:**
- `trader_investment_plan`, all 4 reports, debate history
- `current_aggressive_response`, `current_neutral_response`

**Prompt summary:**
> Protect assets and minimise volatility. Highlight undue risk in the trader's
> plan. Counter the Aggressive analyst's optimism with evidence of potential
> downsides. Advocate for low-risk adjustments.

**Writes to state:** Appends to `risk_debate_state.conservative_history` and `history`.

---

### 11. Neutral Analyst

**LLM:** `quick_thinking_llm`

**Input from state:**
- `trader_investment_plan`, all 4 reports, debate history
- `current_aggressive_response`, `current_conservative_response`

**Prompt summary:**
> Provide a balanced perspective. Challenge both the Aggressive and Conservative
> analysts where each is overly optimistic or overly cautious. Advocate for a
> moderate, sustainable strategy.

**Writes to state:** Appends to `risk_debate_state.neutral_history` and `history`.

---

## Phase 5 — Final Decision

### 12. Portfolio Manager _(risk judge)_

**LLM:** `deep_thinking_llm` (with structured output)

**Tools:** None

**Input from state:**
- `risk_debate_state.history` — full three-way risk debate transcript
- `investment_plan` — Research Manager's verdict
- `trader_investment_plan` — Trader's proposal
- `past_context` — **memory log** of prior decisions and outcomes for this ticker

**Prompt summary:**
> Synthesise the risk analysts' debate and deliver the final trading decision.
> Pick exactly one rating from:
> **Buy / Overweight / Hold / Underweight / Sell**
> Be decisive. Ground every conclusion in specific evidence from the analysts.
> Use prior-run lessons from `past_context` to avoid repeating past mistakes.

**Writes to state:** `final_trade_decision`, `risk_debate_state.judge_decision`

---

## Data Flow Diagram

```
External World
──────────────────────────────────────────────────────────
yfinance / Alpha Vantage        StockTwits / Reddit / yfinance news
       ↓ (tool calls)                  ↓ (pre-fetched into prompt)
  Market Analyst                  Sentiment Analyst
  News Analyst                    (no tool calls)
  Fundamentals Analyst
       │                                │
       └──────────── state ─────────────┘
              market_report
              sentiment_report
              news_report
              fundamentals_report
                    │
                    ▼
          ┌─── Bull Researcher ───┐
          │   (reads all reports) │
          └──────── ↕ ────────────┘   ← N debate rounds
          ┌─── Bear Researcher ───┐
          │   (reads all reports) │
          └───────────────────────┘
                    │
                    ▼
          Research Manager (deep LLM)
          → investment_plan
                    │
                    ▼
               Trader
          → trader_investment_plan
                    │
          ┌─────────┴──────────┐
          ▼         ▼          ▼       ← N debate rounds
     Aggressive  Conservative Neutral
     (reads all 4 reports + trader plan)
          └─────────┬──────────┘
                    ▼
          Portfolio Manager (deep LLM)
          reads: risk debate + investment_plan
                + trader_plan + past_context
          → final_trade_decision
```

---

## Key Design Notes

| Point | Detail |
|---|---|
| **No direct agent calls** | All sharing is via `AgentState` fields — agents never call each other |
| **Sentiment is pre-fetch** | StockTwits + Reddit + Yahoo news are fetched before the LLM is invoked; no tool calls |
| **deep_thinking_llm reserved for judges** | Only Research Manager and Portfolio Manager use the expensive model |
| **past_context only reaches PM** | Memory log from prior runs is injected only into the Portfolio Manager prompt |
| **Debate rounds are configurable** | `max_debate_rounds` (Bull/Bear) and `max_risk_discuss_rounds` (risk panel) in config |
| **Checkpoint/resume** | If `checkpoint_enabled`, a SqliteSaver is compiled in so a crashed run resumes from the last completed node |
| **instrument_context** | Resolved once at run start via yfinance lookup; injected into every agent to prevent ticker hallucination |
