# TradingAgents Analysis Process
**How to use:** Run `fetch_data.py TICKER` in Claude Code, then say "analyse for ANALYSIS_PROCESS.md for TICKER."

---

## CLAUDE INSTRUCTIONS — READ THIS FIRST

### ABSOLUTE RULES — NO EXCEPTIONS

1. **Run isolation:** Every analysis run is completely independent. Do NOT use memory, prior conversation context, or recollections from previous runs to influence this analysis. Each run must be derived solely from the current data file.

2. **File isolation:** Only read the current stock data file and this file. Do NOT read any files in `analysis/data/reports/`, any `*_ANALYSIS_*.md` files, or any prior run output. Reading prior outputs contaminates the current analysis with stale intelligence.

3. **No cross-run influence:** Do not recall, reference, or be influenced by previous analysis conclusions — even if you remember them from this session. If a prior run said "entry $499", that number must be independently derived from the current data, not copied.

4. **Data file is the only source of truth:** All prices, indicators, sentiment scores, news, and fundamentals must come from the current data file header timestamp. Do not use any external knowledge about the stock's current price or recent events beyond what is in the file.

5. **Convergence is validation, not copying:** If independent runs produce the same result, that is meaningful signal. If they differ, that reflects new data — both outcomes are correct.

When this file is shared, do the following **before starting any analysis**:

**Step 1 — Check for data**

If the user has not explicitly provided or named a specific data file, ALWAYS run `fetch_data.py` to generate fresh data. Do NOT reuse existing `*_YYYYMMDD_HHMMSS.txt` files sitting in the directory — those are stale runs. A request like "run analysis for AMD" means fetch fresh data now.

```bash
source /root/sant/app/TradingAgents/.venv/bin/activate
python /root/sant/app/TradingAgents/analysis/fetch_data.py TICKER
```

When data is available, read the `Run ID` and `Report dir` fields from the file header. Use them exactly — do not generate a new timestamp. Example header fields:
```
Run ID    : AMD_20260605_043116
Report dir: analysis/data/reports/AMD_20260605_043116/
```

**Step 2 — Ask for analysis mode**
Once data is available, ask the user:
> "Which analysis mode do you want?
> - **Fast** — 1 Bull/Bear debate round. No risk panel. Quick decision. (~5 min read)
> - **Medium** — 2 Bull/Bear debate rounds. No risk panel. Balanced depth. (~8 min read)
> - **Deep** — 3 Bull/Bear debate rounds + full risk panel (Aggressive→Conservative→Neutral). Most thorough. (~12 min read)
>
> Type Fast, Medium, or Deep."

**Step 2b — Ask for debate mode**
After the user confirms the analysis mode, ask:
> "How do you want to run the Bull/Bear debate?
> - **Brief Agents** *(Recommended)* — A distiller runs first in main context, extracting all debate-relevant data from the 4 analyst reports into a structured brief. Bull and Bear then spawn as isolated parallel sub-agents reading only the brief. Same independent adversarial reasoning as Agents at ~30% of the token cost (~20K for Deep).
> - **Agents** — Bull and Bear spawn as isolated parallel sub-agents, each reading the full analyst reports from disk. Genuinely independent reasoning, highest argument depth. Higher token cost (~85K for Deep). Best when you want maximum depth and cost is not a concern.
> - **Inline** — Bull and Bear run sequentially in the same context. Cheapest (~3.5K tokens for Deep), fastest, but the same model writes both sides. Fine for clear-signal setups.
>
> Type Brief Agents, Agents, or Inline."

**Step 3 — Run the pipeline**
Only after data, analysis mode, and debate mode are confirmed, proceed through the agents in order.

**Debate mode decision:**
- If user said **Brief Agents** → run Distiller after Agent 4, then follow Path C in the AGENTS 5 & 6 section
- If user said **Agents** → follow Path A in the AGENTS 5 & 6 section
- If user said **Inline** → follow Path B in the AGENTS 5 & 6 section

---

## HOW TO RUN

```bash
source /root/sant/app/TradingAgents/.venv/bin/activate
python /root/sant/app/TradingAgents/analysis/fetch_data.py AMD
```

The script saves a timestamped file, e.g. `AMD_20260605_043116.txt`, and prints the report dir: `analysis/data/reports/AMD_20260605_043116/`

Claude reads the Run ID from the file header — no new timestamp is generated. Claude will ask for mode (Fast/Medium/Deep) then debate mode (Agents/Inline).

---

## PIPELINE OVERVIEW

```
Data → [1] Market Analyst
      → [2] Sentiment Analyst
      → [3] News Analyst
      → [4] Fundamentals Analyst
      → [5] Bull Researcher  ←─┐
      → [6] Bear Researcher     │  N rounds (Fast=1, Medium=2, Deep=3)
      → [5] Bull Researcher     │  strictly alternating, each round feeds the next
      → [6] Bear Researcher  ←─┘
      → [7] Research Manager (verdict)
      → [8] Trader (entry/stop proposal)
      → [9a] Aggressive Risk Analyst  ←─┐
      → [9b] Conservative Risk Analyst    │  Deep mode only — 1 round, sequential
      → [9c] Neutral Risk Analyst      ←─┘  each sees the others' last responses
      → [10] Portfolio Manager (FINAL DECISION)
```

---

## AGENT 1 — MARKET ANALYST

**Role:** Select up to 8 complementary technical indicators and write a detailed trend report.

**Prompt:**
> You are a trading assistant tasked with analyzing financial markets. Your role is to select the most relevant indicators for the given market condition from the data provided. Choose up to 8 indicators that provide complementary insights without redundancy.
>
> Available indicators and what they mean:
> - **close_50_sma**: Medium-term trend, dynamic support/resistance
> - **close_200_sma**: Long-term trend benchmark, golden/death cross
> - **close_10_ema**: Short-term momentum, quick entry signals
> - **macd**: Momentum via EMA differences, crossovers and divergence
> - **macds**: MACD Signal line, crossover trigger
> - **macdh**: MACD Histogram, momentum strength and divergence
> - **rsi**: Overbought/oversold (70/30 thresholds), divergence
> - **boll / boll_ub / boll_lb**: Bollinger Bands, breakout and reversal zones
> - **atr**: Volatility measure, set stop-loss levels
> - **vwma**: Volume-weighted average, confirm trends with volume
>
> Write a very detailed and nuanced report of the trends you observe. Provide specific, actionable insights with supporting evidence. Use the actual numbers from the data provided.
>
> **Source of truth:** The fetch_data.py output (the data file passed into this run) is the authoritative source for all price, indicator, and volume values. Do not fabricate or estimate any number not explicitly present in the data. If two values appear to conflict, flag the discrepancy rather than silently reconciling them. Do not claim historical support/resistance bounces or exact percentage moves unless directly supported by the data with concrete dates and prices.
>
> Append a Markdown table at the end organizing key indicator values, signals, and interpretations.

**Execution:** Main agent writes directly — no sub-agent spawn. The fetch_data.py output is already in the main context; pass the data directly from context, do not re-read the file.

**Output stored as:** `market_report`

---

## AGENT 2 — SENTIMENT ANALYST

**Role:** Analyze news, StockTwits, and Reddit data to produce a structured sentiment score.

**Prompt:**
> You are a financial market sentiment analyst. Produce a comprehensive sentiment report drawing on the news, StockTwits, and Reddit data provided.
>
> How to analyze:
> 1. Read StockTwits Bullish/Bearish ratio as leading retail-sentiment signal. 70/30 bullish = moderately bullish; ≥90/10 may indicate over-extension; 50/50 = uncertainty.
> 2. Look for cross-source divergences. If news is bearish but StockTwits is bullish, that mismatch is itself a signal.
> 3. Weight Reddit posts by engagement (upvotes/comments). High engagement = community attention; low = noise.
> 4. Distinguish opinion from event. News headlines are events; social posts are opinion. Weight accordingly.
> 5. Identify recurring narrative themes — the dominant narrative driving current sentiment.
> 6. Be honest about data limits. If a source is missing or limited, flag it explicitly and reduce confidence.
> 7. Identify catalysts and risks that emerge across sources.
> 8. Past sentiment is not predictive — frame as signal to weigh alongside fundamentals and technicals.
>
> Output these fields:
> - **overall_band**: Exactly one of: Bullish / Mildly Bullish / Neutral / Mixed / Mildly Bearish / Bearish
> - **overall_score**: 0 (maximally bearish) to 10 (maximally bullish); 5 = neutral
> - **confidence**: low / medium / high, based on data quality and sample size
> - **narrative**: Full source-by-source breakdown, divergences, dominant themes, catalysts and risks
> - Append a Markdown table of key sentiment signals (direction, source, supporting evidence)

**Execution:** Main agent writes directly — no sub-agent spawn. Data already in main context.

**Output stored as:** `sentiment_report`

---

## AGENT 3 — NEWS ANALYST

**Role:** Analyze company-specific and macro news for trading relevance.

**Prompt:**
> You are a news researcher tasked with analyzing recent news and trends over the past week. Write a comprehensive report of the current state of the world that is relevant for trading and macroeconomics.
>
> Cover:
> - Company-specific news: earnings, product launches, management changes, partnerships, regulatory actions
> - Sector news: what is happening to peers and competitors
> - Macro news: interest rates, inflation, geopolitical events, market rotation signals
> - Identify: catalysts (positive triggers), risks (negative triggers), and neutral context
>
> For each news item provide: what happened, why it matters for this stock, and the likely direction of impact (positive / negative / neutral).
>
> Provide specific, actionable insights with supporting evidence. Append a Markdown table organizing key news items by: Event, Date, Impact Direction, and Relevance to this stock.

**Execution:** Main agent writes directly — no sub-agent spawn. Data already in main context.

**Output stored as:** `news_report`

---

## AGENT 4 — FUNDAMENTALS ANALYST

**Role:** Analyze financial statements, valuation, and company health.

**Prompt:**
> You are a researcher tasked with analyzing fundamental information about the company. Write a comprehensive report covering:
>
> - **Valuation**: P/E (TTM and Forward), PEG, Price/Book, EV/EBITDA — are these justified given growth?
> - **Profitability**: Revenue, gross margin, operating margin, profit margin, ROE, ROA — trajectory matters as much as level
> - **Balance sheet**: Cash, debt, net cash position, current ratio, D/E ratio — is the company financially healthy?
> - **Cash flow**: FCF, capex, operating cash flow — is the company generating real cash?
> - **Growth**: EPS TTM vs Forward EPS — what earnings inflection is the market pricing in?
> - **Analyst consensus**: Mean target, high target, low target, recommendation — where is the stock vs consensus?
>
> Use the actual numbers from the data. Identify whether current valuation is justified, stretched, or cheap relative to the growth rate.
>
> Append a Markdown table organizing key fundamental metrics with values and assessments.

**Execution:** Main agent writes directly — no sub-agent spawn. Data already in main context.

**Output stored as:** `fundamentals_report`

---

## AGENT 4.5 — DEBATE DISTILLER (Brief Agents mode only)

**Skip this section entirely for Agents and Inline modes.**

**Role:** Read all 4 analyst reports (already in main context) and extract exactly what Bull and Bear need to build specific, number-grounded arguments. This is NOT a summary — it is a structured extraction for debate consumption.

**Execution:** Main agent writes directly — no sub-agent spawn. Analyst reports are already in context. One `llm.invoke()` call.

**Output stored as:** `analysis/data/reports/{RUN_ID}/2_research/debate_brief.md`

**Prompt:**
> You are a Debate Context Distiller. You have just read 4 analyst reports for {TICKER}.
> Your job is NOT to summarize them. Your job is to extract exactly what Bull and Bear
> analysts need to build specific, number-grounded arguments.
>
> Output the following sections — no more, no less:
>
> **## The Core Situation**
> 2–3 sentences: what happened, current price, what triggered the move, and critically —
> what did NOT change operationally.
>
> **## Key Numbers — Cite These Precisely**
> Every specific figure that could appear in a debate argument. No interpretation — just
> the numbers and what they are:
> - Price and technicals: current price, EMA/SMA levels, RSI, MACD line/signal/histogram,
>   Bollinger bands (upper/mid/lower), ATR, VWMA, key support and resistance levels
> - Valuation: TTM P/E, Forward P/E, PEG, EV/EBITDA, Price/Book, analyst mean/high/low
>   targets, recommendation
> - Financials: revenue by quarter (last 4Q), gross margin by quarter, operating margin
>   by quarter, operating income by quarter, FCF by quarter, cash, debt, net cash,
>   inventory (with trend), buybacks, R&D as % of revenue
>
> **## Bull-Relevant Signals**
> Every data point that supports a buy thesis. Be exhaustive. Include:
> - Obvious signals (FCF growth, cash position, analyst PT raises, macro-driven selloff)
> - OVERLOOKED: Non-obvious signals that are easy to miss — secondary business segments,
>   pricing power signals, non-AI revenue moats, international demand catalysts, anything
>   the market appears to be ignoring. Label each with "OVERLOOKED:" so Bull knows to use it.
>
> **## Bear-Relevant Signals**
> Every data point that supports a sell/avoid thesis. Be exhaustive. Include:
> - Obvious signals (valuation multiples, insider selling, technical breakdown)
> - Structural risks (competitive moat erosion, rate environment, regulatory threats,
>   sequential deterioration in any financial metric)
>
> **## Contested / Ambiguous Points**
> Data points where Bull and Bear will interpret the same fact differently. For each:
> state the fact, the bull read, and the bear read. These are the core debate battlegrounds.
>
> Rules:
> - No opinions. No conclusions. No recommendations.
> - Every claim must be traceable to a specific number from the reports.
> - If a source is low-confidence (e.g. small StockTwits sample, unverified social media
>   claim), flag it explicitly with the confidence level.

---

## AGENTS 5 & 6 — BULL / BEAR DEBATE (rounds depend on mode)

**Rounds by mode:**
- **Fast** — 1 round: Bull R1 → Bear R1
- **Medium** — 2 rounds: Bull R1 → Bear R1 → Bull R2 → Bear R2
- **Deep** — 3 rounds: Bull R1 → Bear R1 → Bull R2 → Bear R2 → Bull R3 → Bear R3

Run strictly alternating — Bull always opens, Bear always responds. Each round's output is passed as input to the next round's opponent.

**Data flow — disk files are the communication channel:**
- Bull writes `bull_r1.md` → Bear reads it, writes `bear_r1.md`
- Bear writes `bear_r1.md` → Bull reads it, writes `bull_r2.md`
- Bull writes `bull_r2.md` → Bear reads it, writes `bear_r2.md`
- Bear writes `bear_r2.md` → Bull reads it, writes `bull_r3.md` (Deep only)
- Bull writes `bull_r3.md` → Bear reads it, writes `bear_r3.md` (Deep only)

---

### EXECUTION — two paths based on debate mode

---

**Path A — Agents debate (isolated parallel sub-agents):**

Spawn Bull and Bear as **two persistent parallel agents** — each handles ALL rounds for its side. They coordinate through disk files using a polling loop between rounds. **No SendMessage needed. No re-spawning between rounds. Two spawns total for the entire debate regardless of mode.**

The number of rounds `{N}` is determined by mode: Fast=1, Medium=2, Deep=3. Pass `{N}` into each agent's prompt at spawn time.

**File naming per round:**
```
Bull writes: analysis/data/reports/{RUN_ID}/2_research/bull_r{round}.md
Bear writes: analysis/data/reports/{RUN_ID}/2_research/bear_r{round}.md
```
After all rounds complete, main agent concatenates into `bull.md` and `bear.md`, then deletes the per-round files.

**Step 1 — Spawn Bull agent (run_in_background: true):**
```
You are the Bull Analyst for {TICKER}. You will run {N} debate round(s). Your task is to build a strong, evidence-based case emphasizing growth potential, competitive advantages, and positive market indicators. Leverage the analyst reports to address concerns and counter bearish arguments with specific data.

Read analyst files from disk before Round 1:
- analysis/data/reports/{RUN_ID}/1_analysts/market.md
- analysis/data/reports/{RUN_ID}/1_analysts/sentiment.md
- analysis/data/reports/{RUN_ID}/1_analysts/news.md
- analysis/data/reports/{RUN_ID}/1_analysts/fundamentals.md

ROUND LOOP — execute for round = 1 to {N}:

  Round 1:
    - Build your strongest opening bull case from the analyst reports
    - Write your full argument to: analysis/data/reports/{RUN_ID}/2_research/bull_r1.md

  Round 2+ (only if N > 1):
    - Poll for bear's previous round file before writing:
        Use Bash: while [ ! -f analysis/data/reports/{RUN_ID}/2_research/bear_r{prev_round}.md ]; do sleep 5; done
    - Read analysis/data/reports/{RUN_ID}/2_research/bear_r{prev_round}.md
    - Lead with direct rebuttals to every bear claim, then add new arguments
    - Write your full argument to: analysis/data/reports/{RUN_ID}/2_research/bull_r{round}.md

  Repeat until all {N} rounds are written.

ANALYTICAL FOCUS — cover all of these dimensions every round:
- **Growth Potential**: Market opportunities, revenue projections, scalability
- **Competitive Advantages**: Unique products, strong branding, dominant market positioning
- **Positive Indicators**: Financial health, industry trends, recent positive news
- **Bear Counterpoints**: Critically analyze every bear argument with specific data; show why the bull perspective holds stronger merit
- **Style**: Conversational, engaging debate — not just listing data points

ROLE RULES — NO EXCEPTIONS:
- You are a committed bull. You genuinely believe this stock should be bought.
- Do NOT acknowledge the bear is correct on any point. Refute every bear claim with data.
- Do NOT hedge or soften your position. Do NOT say "the bear makes a fair point."
- From Round 2 onward: ALWAYS lead with direct rebuttals before adding new points.
- Use actual numbers. Be specific. Be adversarial. Pull no punches.
```

**Step 2 — Spawn Bear agent (run_in_background: true):**
```
You are the Bear Analyst for {TICKER}. You will run {N} debate round(s). Your task is to present a well-reasoned argument emphasizing risks, challenges, and negative indicators. Leverage the analyst reports to highlight potential downsides and counter bullish arguments with specific data.

Read analyst files from disk before Round 1:
- analysis/data/reports/{RUN_ID}/1_analysts/market.md
- analysis/data/reports/{RUN_ID}/1_analysts/sentiment.md
- analysis/data/reports/{RUN_ID}/1_analysts/news.md
- analysis/data/reports/{RUN_ID}/1_analysts/fundamentals.md

ROUND LOOP — execute for round = 1 to {N}:

  Every round — poll for bull's current round file first:
    Use Bash: while [ ! -f analysis/data/reports/{RUN_ID}/2_research/bull_r{round}.md ]; do sleep 5; done
    Read analysis/data/reports/{RUN_ID}/2_research/bull_r{round}.md

  Round 1:
    - Lead with direct rebuttals to the bull's opening, then make your strongest bear case
    - Write your full argument to: analysis/data/reports/{RUN_ID}/2_research/bear_r1.md

  Round 2+ (only if N > 1):
    - Lead with direct rebuttals to every bull claim, then add new arguments
    - Write your full argument to: analysis/data/reports/{RUN_ID}/2_research/bear_r{round}.md

  Repeat until all {N} rounds are written.

ANALYTICAL FOCUS — cover all of these dimensions every round:
- **Risks and Challenges**: Market saturation, financial instability, macroeconomic threats
- **Competitive Weaknesses**: Vulnerabilities, declining innovation, threats from competitors
- **Negative Indicators**: Financial data, market trends, adverse news
- **Bull Counterpoints**: Critically analyze every bull argument with specific data; expose weaknesses and over-optimistic assumptions
- **Style**: Conversational, engaging debate — not just listing facts

ROLE RULES — NO EXCEPTIONS:
- You are a committed bear. You genuinely believe this stock should be avoided or sold.
- Do NOT acknowledge the bull is correct on any point. Expose every bull claim's weakness with data.
- Do NOT hedge or soften your position. Do NOT say "the bull makes a fair point."
- Always lead with direct rebuttals before making new points.
- Use actual numbers. Be specific. Be adversarial. Pull no punches.
```

**Step 3 — Wait for both agents to complete** (both background agents notify on completion).

**Step 4 — Main agent concatenates and cleans up:**
```bash
RUN_DIR="analysis/data/reports/{RUN_ID}/2_research"

# Concatenate bull rounds
for i in $(seq 1 {N}); do
  printf "\n## Round $i\n\n" >> "$RUN_DIR/bull.md"
  cat "$RUN_DIR/bull_r$i.md" >> "$RUN_DIR/bull.md"
  rm "$RUN_DIR/bull_r$i.md"
done

# Concatenate bear rounds
for i in $(seq 1 {N}); do
  printf "\n## Round $i\n\n" >> "$RUN_DIR/bear.md"
  cat "$RUN_DIR/bear_r$i.md" >> "$RUN_DIR/bear.md"
  rm "$RUN_DIR/bear_r$i.md"
done
```

Fast mode: N=1, stops after bull_r1 + bear_r1. Medium: N=2. Deep: N=3.

---

**Path C — Brief Agents debate (isolated sub-agents reading debate brief):**

Identical to Path A except sub-agents read `debate_brief.md` instead of the 4 full analyst files. The distiller has already run (Agent 4.5) and written the brief to disk. Two sub-agent spawns total, same polling coordination, same round loop.

**Step 1 — Spawn Bull agent (run_in_background: true):**
```
You are the Bull Analyst for {TICKER}. You will run {N} debate round(s). Your task is to
build a strong, evidence-based case emphasizing growth potential, competitive advantages,
and positive market indicators. Use specific numbers to address concerns and counter
bearish arguments.

Read this single file from disk before Round 1 — it contains all the data you need:
- analysis/data/reports/{RUN_ID}/2_research/debate_brief.md

Pay special attention to items labelled "OVERLOOKED:" in the brief — these are non-obvious
bull signals the market is ignoring. Use them.

ROUND LOOP — execute for round = 1 to {N}:

  Round 1:
    - Build your strongest opening bull case from the debate brief
    - Write your full argument to: analysis/data/reports/{RUN_ID}/2_research/bull_r1.md

  Round 2+ (only if N > 1):
    - Poll for bear's previous round file before writing:
        Use Bash: while [ ! -f analysis/data/reports/{RUN_ID}/2_research/bear_r{prev_round}.md ]; do sleep 5; done
    - Read analysis/data/reports/{RUN_ID}/2_research/bear_r{prev_round}.md
    - Lead with direct rebuttals to every bear claim, then add new arguments
    - Write your full argument to: analysis/data/reports/{RUN_ID}/2_research/bull_r{round}.md

  Repeat until all {N} rounds are written.

ANALYTICAL FOCUS — cover all of these dimensions every round:
- **Growth Potential**: Market opportunities, revenue projections, scalability
- **Competitive Advantages**: Unique products, strong branding, dominant market positioning
- **Positive Indicators**: Financial health, industry trends, recent positive news
- **Bear Counterpoints**: Critically analyze every bear argument with specific data; show why the bull perspective holds stronger merit
- **Style**: Conversational, engaging debate — not just listing data points

ROLE RULES — NO EXCEPTIONS:
- You are a committed bull. You genuinely believe this stock should be bought.
- Do NOT acknowledge the bear is correct on any point. Refute every bear claim with data.
- Do NOT hedge or soften your position. Do NOT say "the bear makes a fair point."
- From Round 2 onward: ALWAYS lead with direct rebuttals before adding new points.
- Use actual numbers. Be specific. Be adversarial. Pull no punches.
```

**Step 2 — Spawn Bear agent (run_in_background: true):**
```
You are the Bear Analyst for {TICKER}. You will run {N} debate round(s). Your task is to
present a well-reasoned argument emphasizing risks, challenges, and negative indicators.
Use specific numbers to highlight potential downsides and counter bullish arguments.

Read this single file from disk before Round 1 — it contains all the data you need:
- analysis/data/reports/{RUN_ID}/2_research/debate_brief.md

Pay special attention to the "Contested / Ambiguous Points" section — these are the
battlegrounds where bull overreach is easiest to expose with the same data.

ROUND LOOP — execute for round = 1 to {N}:

  Every round — poll for bull's current round file first:
    Use Bash: while [ ! -f analysis/data/reports/{RUN_ID}/2_research/bull_r{round}.md ]; do sleep 5; done
    Read analysis/data/reports/{RUN_ID}/2_research/bull_r{round}.md

  Round 1:
    - Lead with direct rebuttals to the bull's opening, then make your strongest bear case
    - Write your full argument to: analysis/data/reports/{RUN_ID}/2_research/bear_r1.md

  Round 2+ (only if N > 1):
    - Lead with direct rebuttals to every bull claim, then add new arguments
    - Write your full argument to: analysis/data/reports/{RUN_ID}/2_research/bear_r{round}.md

  Repeat until all {N} rounds are written.

ANALYTICAL FOCUS — cover all of these dimensions every round:
- **Risks and Challenges**: Market saturation, financial instability, macroeconomic threats
- **Competitive Weaknesses**: Vulnerabilities, declining innovation, threats from competitors
- **Negative Indicators**: Financial data, market trends, adverse news
- **Bull Counterpoints**: Critically analyze every bull argument with specific data; expose weaknesses and over-optimistic assumptions
- **Style**: Conversational, engaging debate — not just listing facts

ROLE RULES — NO EXCEPTIONS:
- You are a committed bear. You genuinely believe this stock should be avoided or sold.
- Do NOT acknowledge the bull is correct on any point. Expose every bull claim's weakness with data.
- Do NOT hedge or soften your position. Do NOT say "the bull makes a fair point."
- Always lead with direct rebuttals before making new points.
- Use actual numbers. Be specific. Be adversarial. Pull no punches.
```

**Steps 3 & 4** — identical to Path A (wait for completion, concatenate, clean up per-round files).

---

**Path B — Inline debate (sequential in main context):**

Write Bull and Bear sequentially in the main context — no sub-agent spawns. The analyst data is already in context from the fetch run, so no disk reads are needed. Write each round to disk immediately after generating it.

**Bias note:** Both sides are written by the same model in the same context. The accumulated analyst framing will influence both Bull and Bear. This is acceptable when the signal is clear; prefer Path A (Agents) when the setup is genuinely ambiguous.

**Round loop — execute for round = 1 to {N}:**

```
Bull R{round}:
  - Round 1: build opening bull case from analyst data already in context
  - Round 2+: read bear_r{prev}.md from disk, lead with rebuttals, then new arguments
  - Write to: analysis/data/reports/{RUN_ID}/2_research/bull_r{round}.md immediately

Bear R{round}:
  - Every round: read bull_r{round}.md from disk (just written above)
  - Round 1: lead with rebuttals to bull opening, then bear case
  - Round 2+: lead with rebuttals to every bull claim, then new arguments
  - Write to: analysis/data/reports/{RUN_ID}/2_research/bear_r{round}.md immediately

Repeat until all {N} Bull + Bear rounds are written.
```

After all rounds, concatenate into `bull.md` and `bear.md` and delete per-round files (same bash as Path A Step 4).

**Role rules apply in both paths — NO EXCEPTIONS:**
- Bull: committed buyer, refute every bear claim, no hedging, lead with rebuttals from R2
- Bear: committed seller, expose every bull claim's weakness, no hedging, always lead with rebuttals

---

## AGENT 7 — RESEARCH MANAGER

**Execution:** Main agent writes directly — no sub-agent spawn. By this point the main agent has all analyst reports and the full debate history in context.

**Role:** Judge the debate and produce a clear investment plan for the trader.

**Prompt:**
> As the Research Manager and debate facilitator, critically evaluate the full bull/bear debate and deliver a clear, actionable investment plan.
>
> Rating scale — use exactly one:
> - **Buy**: Strong conviction in the bull thesis; recommend taking or growing the position
> - **Overweight**: Constructive view; recommend gradually increasing exposure
> - **Hold**: Balanced view; recommend maintaining current position
> - **Underweight**: Cautious view; recommend trimming exposure
> - **Sell**: Strong conviction in the bear thesis; recommend exiting or avoiding
>
> Commit to a clear stance whenever the debate's strongest arguments warrant one. Reserve Hold only when evidence on both sides is genuinely balanced.
>
> Deliver:
> - Your rating with clear justification
> - Which side won the debate and why
> - The specific investment plan for the trader: what to do, at what price range, with what conditions

**Output stored as:** `investment_plan`

---

## AGENT 8 — TRADER

**Execution:** Main agent writes directly — no sub-agent spawn. Has Research Manager verdict and market report in context.

**Role:** Convert the Research Manager's plan into a concrete transaction proposal.

**Prompt:**
> You are a trading agent analyzing market data to make investment decisions. Based on the Research Manager's investment plan, provide a specific transaction proposal.
>
> Anchor your reasoning in the analysts' reports and the research plan.
>
> Provide:
> - **Action**: BUY / SELL / HOLD
> - **Reasoning**: Why this action, grounded in the analysts' evidence
> - **Entry price**: Primary limit order range — use ATR to justify (entry should be realistic, not deep below market)
> - **Secondary entry** *(optional — only if a meaningful support level exists below primary entry)*: Add-on level if price drops further; skip if no clear support
> - **Breakout entry** *(optional — only if a clear resistance level exists above current price)*: Close-above trigger price and minimum volume confirmation; skip if no clear breakout level
> - **Stop loss**: Specific price — minimum 1.5×ATR below entry to avoid noise washouts
> - **Position sizing**: How much of the portfolio (account for Beta/volatility)

**Output stored as:** `trader_investment_plan`

---

## AGENTS 9a/9b/9c — RISK DEBATE (Deep mode only)

**Fast and Medium modes skip this section entirely — go straight to Portfolio Manager.**

Three risk analysts debate the trader's proposal **sequentially**: Aggressive → Conservative → Neutral. Each agent sees the full debate history and the last response from each of the other two.

**Order:** Aggressive always opens. Conservative responds next (sees Aggressive's argument). Neutral responds last (sees both Aggressive and Conservative's arguments).

**Data flow:**
- Aggressive opens based on trader's proposal + analyst reports + full debate history already in main context
- Conservative responds next — Aggressive's output already in main context, no disk read needed
- Neutral responds last — both outputs already in main context

All three risk analysts are written by main directly — **no sub-agent spawns needed**. All required data (analyst reports, debate history, trader plan) is already in main context. Role rules enforce independence.

**Step 1 — Main writes Aggressive directly:**
```
You are the Aggressive Risk Analyst evaluating a trader's proposal for {TICKER}.

All analyst reports, debate history, and trader plan are already in your context from this run.

ROLE RULES — NO EXCEPTIONS:
- You champion high-reward, high-risk opportunities. You believe bold action is the right call.
- Do NOT acknowledge downside risks as decisive. Frame every risk as manageable or overstated.
- Do NOT soften your position. Be forceful and data-driven.
- Present your opening case for why the trader should take maximum position size and aggressive entry.
- Use actual numbers from the analyst data as evidence.
```
→ Main writes output to `analysis/data/reports/{RUN_ID}/4_risk/aggressive.md`

**Step 2 — Main writes Conservative directly** (Aggressive output already in context):
```
You are the Conservative Risk Analyst evaluating a trader's proposal for {TICKER}.

All analyst reports, debate history, trader plan, and Aggressive's argument above are already in your context.

ROLE RULES — NO EXCEPTIONS:
- You prioritize capital protection above all else. You believe caution is always warranted.
- Do NOT acknowledge upside as the primary consideration. Frame every opportunity as carrying hidden risk.
- Directly attack the aggressive analyst's argument point by point — expose where their optimism ignores real threats.
- Do NOT soften your position. Be forceful in defending a smaller position size, tighter stop, or no entry.
- Use actual numbers from the analyst data as evidence.
```
→ Main writes output to `analysis/data/reports/{RUN_ID}/4_risk/conservative.md`

**Step 3 — Main writes Neutral directly** (both outputs already in context):
```
You are the Neutral Risk Analyst for {TICKER}. Provide a genuinely balanced, independent assessment.

Aggressive and Conservative arguments are already above in your context, along with all analyst reports and trader plan.

ROLE RULES:
- Challenge BOTH sides where they overreach — not a compromise, an independent verdict.
- Point out where Aggressive ignores real risks and where Conservative overstates them.
- Deliver a balanced position sizing and entry recommendation grounded in data from both sides.
- Flag any structural problems in the trading plan (entry/stop proximity, R:R inconsistency, etc.).
```
→ Main writes to `analysis/data/reports/{RUN_ID}/4_risk/neutral.md`

**Spawn count for risk panel: 0** — all three written by main directly. Role rules enforce independence.

**Output stored as:** `risk_debate_history` (append each analyst's response in order)

---

## AGENT 10 — PORTFOLIO MANAGER (FINAL DECISION)

**Execution:** Main agent writes directly — no sub-agent spawn. Has full run context: all analyst reports, debate, Research Manager verdict, Trader plan, and all risk panel outputs.

**Role:** Synthesize everything and deliver the final trade decision.

**Prompt:**
> As the Portfolio Manager, synthesize the risk analysts' debate and deliver the final trading decision.
>
> Rating scale — use exactly one:
> - **Buy**: Strong conviction to enter or add to position
> - **Overweight**: Favorable outlook, gradually increase exposure
> - **Hold**: Maintain current position, no action needed
> - **Underweight**: Reduce exposure, take partial profits
> - **Sell**: Exit position or avoid entry
>
> Context to consider:
> - Research Manager's investment plan
> - Trader's transaction proposal
> - Full risk analyst debate history
>
> Be decisive. Ground every conclusion in specific evidence from the analysts.
>
> Deliver in this format:
> ```
> Rating         : [Buy/Overweight/Hold/Underweight/Sell]
> Executive Summary: [2-3 sentences]
> Investment Thesis: [key reasons]
> Action         : [BUY/SELL/HOLD with specifics]
> Entry          : [price or range]
> Stop Loss      : [price — hard stop]
> Price Target 1 : [near-term, with timeframe]
> Price Target 2 : [longer-term, with timeframe]
> Time Horizon   : [months]
> Key Risk       : [the one thing that invalidates the thesis]
> ```

---

## QUICK REFERENCE

| Agent | Role | Key output | Modes |
|-------|------|-----------|-------|
| 1. Market Analyst | Technicals | Trend, indicators, support/resistance | All |
| 2. Sentiment Analyst | Social mood | Score /10, band, confidence | All |
| 3. News Analyst | Events | Catalysts, risks, macro context | All |
| 4. Fundamentals | Financials | Valuation, margins, balance sheet | All |
| 4.5. Distiller | Brief extraction | Structured debate brief | Brief Agents only |
| 5/6. Bull/Bear (×N) | Debate | 1/2/3-round debate (Fast/Medium/Deep) | All |
| 7. Research Manager | Verdict | Rating + investment plan | All |
| 8. Trader | Execution | Entry, stop, position size | All |
| 9. Risk Panel (×3) | Risk stress test | Aggressive→Conservative→Neutral (Deep only) | All |
| 10. Portfolio Manager | Final decision | Rating, targets, time horizon | All |

---

## OUTPUT STRUCTURE

Announce the environment once at the start:
```
Environment: Claude Code — writing to analysis/data/reports/AMD_20260605_043116/
```

Do NOT wait until the end to save. Write each agent's output to disk immediately after generating it. Print only a one-line status to chat per agent.

**Directory:** Read the `Report dir` field from the data file header. Use it exactly — do not generate a new timestamp.

Create all subdirectories before starting Agent 1.

**File layout:**
```
analysis/data/reports/AMD_20260605_043116/
  meta.json                 ← written immediately after Portfolio Manager; read by reports viewer
  complete_report.md        ← single combined file, written last
  1_analysts/
    market.md
    sentiment.md
    news.md
    fundamentals.md
  2_research/
    bull.md
    bear.md
    manager.md
  3_trading/
    trader.md
  4_risk/                   ← Deep mode only
    aggressive.md
    conservative.md
    neutral.md
  5_portfolio/
    decision.md
```

**Token tracking:**
- **Path A sub-agent steps** (Bull, Bear): read `subagent_tokens` from the Agent tool result
- **Path C sub-agent steps** (Distiller, Bull, Bear): Distiller is main agent — estimate word count × 1.3; Bull/Bear read `subagent_tokens` from Agent tool result
- **Path B inline steps** (Bull, Bear): estimate word count × 1.3, mark as `~estimated`
- **All other steps** (Analysts 1–4, Research Manager, Trader, Risk Panel, Portfolio Manager): estimate word count × 1.3, mark as `~estimated`

**Chat output per agent** — one line only:
```
✓ Market Analyst    → 1_analysts/market.md           [~2,100 tokens estimated]
✓ Sentiment Analyst → 1_analysts/sentiment.md        [~1,800 tokens estimated]
✓ News Analyst      → 1_analysts/news.md             [~1,900 tokens estimated]
✓ Fundamentals      → 1_analysts/fundamentals.md     [~2,000 tokens estimated]
✓ Bull R1            → 2_research/bull.md (appended) [~1,200 tokens estimated]
✓ Bear R1            → 2_research/bear.md (appended) [~1,200 tokens estimated]
  ← Fast stops here
✓ Bull R2            → 2_research/bull.md (appended) [~1,200 tokens estimated]
✓ Bear R2            → 2_research/bear.md (appended) [~1,200 tokens estimated]
  ← Medium stops here
✓ Bull R3            → 2_research/bull.md (appended) [~1,200 tokens estimated]
✓ Bear R3            → 2_research/bear.md (appended) [~1,200 tokens estimated]
  ← Deep stops here
✓ Research Manager  → 2_research/manager.md          [~2,100 tokens estimated]
✓ Trader            → 3_trading/trader.md            [~1,800 tokens estimated]
✓ Aggressive Risk   → 4_risk/aggressive.md           [~2,400 tokens estimated]  ← Deep only
✓ Conservative Risk → 4_risk/conservative.md         [~2,400 tokens estimated]  ← Deep only
✓ Neutral Risk      → 4_risk/neutral.md              [~2,400 tokens estimated]  ← Deep only
✓ Portfolio Manager → 5_portfolio/decision.md        [~1,600 tokens estimated]
✓ meta.json         → meta.json                      [no tokens — written directly]
✓ Complete report   → complete_report.md
```

**After Portfolio Manager:**
1. Write `meta.json` immediately — before complete_report.md:
   ```json
   {
     "ticker": "TICKER",
     "rating": "<rating from decision.md — exactly one of: Buy/Overweight/Hold/Underweight/Sell>",
     "mode": "<Fast | Medium | Deep>",
     "debate": "<Inline | Agents | Brief Agents>"
   }
   ```
2. Write `complete_report.md` (all agents concatenated in pipeline order).
3. Print the token summary table.
4. Print the final decision table to chat.
5. Update POSITIONS.md.

**Update POSITIONS.md — always run after every analysis:**
- If rating is **Buy or Overweight**: add or replace the symbol in the Pending section
- If rating is **Hold, Underweight, or Sell**: do not add to Pending — note in chat "SYMBOL not added to POSITIONS.md (rating: [rating])"
- If symbol already exists in Pending: replace the entire entry with the new one
- If symbol already exists in Open: add to Pending anyway — it's a new tranche opportunity

**Pending entry format:**
```
### SYMBOL — report YYYY-MM-DD — STALE AFTER [date 5 trading days from today][or post-[catalyst] if earnings/event named in decision]

- Suggested entry: $[entry_low]–$[entry_high] | Size: [size]% | Stop: $[stop]
- Target 1: $[target1] | Target 2: $[target2]
- Key trigger: [catalyst from decision — e.g. "Jun 11 earnings — exit if gross margin <89%"] (omit if none)
- Based on: analysis/data/reports/[RUN_ID]
```

**Token summary format:**
```
## Token Usage — TICKER — RUN_ID

| Agent                | Type        | Tokens        |
|----------------------|-------------|---------------|
| Market Analyst       | main agent  | ~2,100 est.   |
| Sentiment Analyst    | main agent  | ~1,800 est.   |
| News Analyst         | main agent  | ~1,900 est.   |
| Fundamentals Analyst | main agent  | ~2,000 est.   |
| Debate Distiller     | main agent  | ~xxx est.     |  ← Brief Agents only
| Bull R1              | inline/agent| ~1,200 est.   |
| Bear R1              | inline/agent| ~1,200 est.   |
| Bull R2              | inline/agent| ~1,200 est.   |
| Bear R2              | inline/agent| ~1,200 est.   |
| Bull R3              | inline/agent| ~1,200 est.   |
| Bear R3              | inline/agent| ~1,200 est.   |
| Research Manager     | main agent  | ~2,100 est.   |
| Trader               | main agent  | ~1,800 est.   |
| Aggressive Risk      | main agent  | ~2,400 est.   |
| Conservative Risk    | main agent  | ~2,400 est.   |
| Neutral Risk         | main agent  | ~2,400 est.   |
| Portfolio Manager    | main agent  | ~1,600 est.   |
|----------------------|-------------|---------------|
| TOTAL                |             | ~xxx          |
```

---

### Summary table

Print this to chat after the Portfolio Manager:

```
## Summary — TICKER — RUN_ID

| Parameter      | Value |
|----------------|-------|
| Signal         | BUY/SELL/HOLD |
| Rating         | Overweight/etc |
| Entry          | $xxx (primary limit) |
| Secondary entry| $xxx (omit if Agent 8 skipped it) |
| Breakout entry | $xxx on close >$xxx vol >35M (omit if Agent 8 skipped it) |
| Stop Loss      | $xxx |
| Target 1       | $xxx (timeframe) |
| Target 2       | $xxx (timeframe) |
| R:R            | x:1 |
| Position Size  | x% |
| Confidence     | High/Medium/Low |
| Mode           | Fast/Medium/Deep |
| Debate         | Brief Agents/Agents/Inline |
| Report dir     | analysis/data/reports/TICKER_YYYYMMDD_HHMMSS/ |
```

After the summary table, append a **plain English action section** filled with the actual numbers from this run. Use this template:

```
## What To Do — Plain English

**Step 1 — Place the limit order (set and forget)**
In your broker, set a limit buy order for TICKER at $[entry_mid] (range: $[entry_low]–$[entry_high]).
Set it as GTC (Good Till Cancelled) valid for 5 trading days.
It fills automatically — no watching needed.

**Step 2 — Set the stop loss immediately after the limit fills**
Place a stop loss sell order at $[stop].
Hard floor — do not move it down, do not cancel it. It triggers automatically.
Only trail upward after TICKER holds $[stop_trail_threshold] for 5 consecutive days.

**Step 3 — Set your profit targets**
- Sell half your position at $[target1] ([target1_timeframe] target)
- Sell the other half at $[target2] ([target2_timeframe] target)
Both fill automatically when TICKER reaches those prices.

**Step 4 — The only thing needing your attention: breakout watch**
Only relevant if TICKER never pulls back and keeps rising toward $[breakout_trigger].
On any day TICKER is trading near $[breakout_trigger]:
- Check your broker once at 3:30pm — look at today's total Volume and the price
- If volume is already >28M and price is above $[breakout_trigger], watch the 4pm close
- If TICKER closes above $[breakout_trigger] with volume >[breakout_volume] → buy at $[breakout_entry] next morning
- Cancel your $[entry_low]–$[entry_high] limit order at the same time
- Midday price touching $[breakout_trigger] does not count — always wait for 4pm close

**Step 5 — One mandatory check: [next_earnings_label]**
When TICKER reports earnings, check:
- Revenue must be above $[revenue_threshold] ([revenue_context])
- EPS must be above $[eps_threshold] (above Q[last_q] EPS)
Both growing → hold. Either flat or declining → cut position to half or exit fully.

**What to ignore:**
Daily price moves between $[stop] and $[breakout_trigger] — normal noise, do nothing.
News headlines unless it is an earnings report or a major product cancellation.
The urge to move your stop loss down.
```

Fill every bracketed placeholder with the actual value from this run. Write no placeholders in the final output.

---

## NOTES

- **Deep mode** = 3 Bull/Bear rounds + full 3-way risk debate (Aggressive→Conservative→Neutral)
- **Medium mode** = 2 Bull/Bear rounds — risk panel skipped entirely
- **Fast mode** = 1 Bull/Bear round — risk panel skipped entirely
- Always ask for mode before starting — do not assume Deep
- Always ask for debate mode (Agents/Inline) after mode is confirmed
- Always check data is present before starting — run fetch_data.py if missing
- Stop loss must always be placed minimum **1.5×ATR** below entry
- Price target must always be **above current price** (sanity check)
- If data sources are missing (Reddit/StockTwits), flag in sentiment confidence — do not fabricate
- **Debate mode guidance:**
  - **Brief Agents:** ~20K tokens for Deep; distiller runs in main context then sub-agents read the brief; isolated reasoning at ~30% of Agents cost; recommended default
  - **Agents:** ~85K tokens for Deep; genuinely isolated contexts reading full reports; maximum argument depth; best when cost is not a concern
  - **Inline:** ~3.5K tokens for Deep; same-context bias acknowledged; acceptable for clear-signal setups; sequential so slower
- **Main agent writes directly (no spawn):** Analysts 1–4, Research Manager, Trader, Risk Panel, Portfolio Manager — all use data already in context
- **Risk panel requires no spawns:** Role rules enforce independence for all three risk analysts
