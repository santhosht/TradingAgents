# TradingAgents Analysis Process
**How to use:** Run `fetch_data.py TICKER`, paste the output into Claude chat, then paste this file and say "follow this process."

---

## CLAUDE INSTRUCTIONS — READ THIS FIRST

### ABSOLUTE RULES — NO EXCEPTIONS

1. **Run isolation:** Every analysis run is completely independent. Do NOT use memory, prior conversation context, or recollections from previous runs to influence this analysis. Each run must be derived solely from the current data file.

2. **File isolation:** Only read the current stock data file and this file. Do NOT read any files in `reports/`, any `*_ANALYSIS_*.md` files, or any prior run output. Reading prior outputs contaminates the current analysis with stale intelligence.

3. **No cross-run influence:** Do not recall, reference, or be influenced by previous analysis conclusions — even if you remember them from this session. If a prior run said "entry $499", that number must be independently derived from the current data, not copied.

4. **Data file is the only source of truth:** All prices, indicators, sentiment scores, news, and fundamentals must come from the current data file header timestamp. Do not use any external knowledge about the stock's current price or recent events beyond what is in the file.

5. **Convergence is validation, not copying:** If independent runs produce the same result, that is meaningful signal. If they differ, that reflects new data — both outcomes are correct.

When this file is shared, do the following **before starting any analysis**:

**Step 1 — Check for data**

**In Claude Code mode (tools available):** If the user has not explicitly provided or named a specific data file, ALWAYS run `fetch_data.py` to generate fresh data. Do NOT reuse existing `*_YYYYMMDD_HHMMSS.txt` files sitting in the directory — those are stale runs. A request like "run analysis for AMD" means fetch fresh data now.

```bash
source /root/sant/app/TradingAgents/.venv/bin/activate
python /root/sant/app/TradingAgents/fetch_data.py TICKER
```

**In Web chat mode (no tools):** If the user has not provided stock data, ask them:
> "Please share the stock data file. Run this command and share the file here:
> ```bash
> source /root/sant/app/TradingAgents/.venv/bin/activate
> python /root/sant/app/TradingAgents/fetch_data.py TICKER
> ```
> Replace TICKER with the stock symbol (e.g. AMD, NVDA, SPY).
> The script saves a timestamped file like `AMD_20260605_043116.txt` — share that file."

When data is available, read the `Run ID` and `Report dir` fields from the file header. Use them exactly — do not generate a new timestamp. Example header fields:
```
Run ID    : AMD_20260605_043116
Report dir: reports/AMD_20260605_043116/
```

**Step 2 — Ask for analysis mode**
Once data is available, ask the user:
> "Which analysis mode do you want?
> - **Fast** — 1 Bull/Bear debate round. No risk panel. Quick decision. (~5 min read)
> - **Medium** — 2 Bull/Bear debate rounds. No risk panel. Balanced depth. (~8 min read)
> - **Deep** — 3 Bull/Bear debate rounds + full risk panel (Aggressive→Conservative→Neutral). Most thorough. (~12 min read)
>
> Type Fast, Medium, or Deep."

**Step 3 — Run the pipeline**
Only after both data and mode are confirmed, proceed through the agents in order.

---

## HOW TO RUN

1. Fetch data:
```bash
source /root/sant/app/TradingAgents/.venv/bin/activate
python /root/sant/app/TradingAgents/fetch_data.py AMD
```
2. The script saves a timestamped file, e.g. `AMD_20260605_043116.txt`, and prints the report dir: `reports/AMD_20260605_043116/`
3. Open Claude chat (claude.ai — no API needed)
4. Share the timestamped `.txt` file and this file
5. Claude reads the Run ID from the file header — no new timestamp is generated
6. Claude will ask for mode — reply Fast / Medium / Deep

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

**Execution (Claude Code mode):** Main agent writes directly — no sub-agent spawn. The fetch_data.py output is already in the main context; pass the data directly from context, do not re-read the file.

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

**Execution (Claude Code mode):** Main agent writes directly — no sub-agent spawn. Data already in main context.

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

**Execution (Claude Code mode):** Main agent writes directly — no sub-agent spawn. Data already in main context.

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

**Execution (Claude Code mode):** Main agent writes directly — no sub-agent spawn. Data already in main context.

**Output stored as:** `fundamentals_report`

---

## AGENTS 5 & 6 — BULL / BEAR DEBATE (rounds depend on mode)

**Rounds by mode:**
- **Fast** — 1 round: Bull R1 → Bear R1
- **Medium** — 2 rounds: Bull R1 → Bear R1 → Bull R2 → Bear R2
- **Deep** — 3 rounds: Bull R1 → Bear R1 → Bull R2 → Bear R2 → Bull R3 → Bear R3

Run strictly alternating — Bull always opens, Bear always responds. Each round's output is passed as input to the next round's opponent. This is what makes it a real debate — not two independent monologues.

**Data flow — disk files are the communication channel:**
- Bull writes `bull_r1.md` → Bear polls for it, reads it, writes `bear_r1.md`
- Bear writes `bear_r1.md` → Bull polls for it, reads it, writes `bull_r2.md`
- Bull writes `bull_r2.md` → Bear polls for it, reads it, writes `bear_r2.md`
- Bear writes `bear_r2.md` → Bull polls for it, reads it, writes `bull_r3.md` (Deep only)
- Bull writes `bull_r3.md` → Bear polls for it, reads it, writes `bear_r3.md` (Deep only)

Each agent reads the opponent's latest file from disk before writing its next round. No arguments are passed inline — the disk is the shared state.

---

### EXECUTION — Claude Code mode vs Web chat mode

**In Claude Code mode (Agent tool available):**

Spawn Bull and Bear as **two persistent parallel agents** — each handles ALL rounds for its side. They coordinate through disk files using a polling loop between rounds. **No SendMessage needed. No re-spawning between rounds. Two spawns total for the entire debate regardless of mode.**

The number of rounds `{N}` is determined by mode: Fast=1, Medium=2, Deep=3. Pass `{N}` into each agent's prompt at spawn time.

**File naming per round:**
```
Bull writes: reports/{RUN_ID}/2_research/bull_r{round}.md
Bear writes: reports/{RUN_ID}/2_research/bear_r{round}.md
```
After all rounds complete, main agent concatenates into `bull.md` and `bear.md`, then deletes the per-round files.

**Step 1 — Spawn Bull agent (run_in_background: true):**
```
You are the Bull Analyst for {TICKER}. You will run {N} debate round(s). Your task is to build a strong, evidence-based case emphasizing growth potential, competitive advantages, and positive market indicators. Leverage the analyst reports to address concerns and counter bearish arguments with specific data.

Read analyst files from disk before Round 1:
- reports/{RUN_ID}/1_analysts/market.md
- reports/{RUN_ID}/1_analysts/sentiment.md
- reports/{RUN_ID}/1_analysts/news.md
- reports/{RUN_ID}/1_analysts/fundamentals.md

ROUND LOOP — execute for round = 1 to {N}:

  Round 1:
    - Build your strongest opening bull case from the analyst reports
    - Write your full argument to: reports/{RUN_ID}/2_research/bull_r1.md

  Round 2+ (only if N > 1):
    - Poll for bear's previous round file before writing:
        Use Bash: while [ ! -f reports/{RUN_ID}/2_research/bear_r{prev_round}.md ]; do sleep 5; done
    - Read reports/{RUN_ID}/2_research/bear_r{prev_round}.md
    - Lead with direct rebuttals to every bear claim, then add new arguments
    - Write your full argument to: reports/{RUN_ID}/2_research/bull_r{round}.md

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
- reports/{RUN_ID}/1_analysts/market.md
- reports/{RUN_ID}/1_analysts/sentiment.md
- reports/{RUN_ID}/1_analysts/news.md
- reports/{RUN_ID}/1_analysts/fundamentals.md

ROUND LOOP — execute for round = 1 to {N}:

  Every round — poll for bull's current round file first:
    Use Bash: while [ ! -f reports/{RUN_ID}/2_research/bull_r{round}.md ]; do sleep 5; done
    Read reports/{RUN_ID}/2_research/bull_r{round}.md

  Round 1:
    - Lead with direct rebuttals to the bull's opening, then make your strongest bear case
    - Write your full argument to: reports/{RUN_ID}/2_research/bear_r1.md

  Round 2+ (only if N > 1):
    - Lead with direct rebuttals to every bull claim, then add new arguments
    - Write your full argument to: reports/{RUN_ID}/2_research/bear_r{round}.md

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
RUN_DIR="reports/{RUN_ID}/2_research"

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

**In Web chat mode (no Agent tool):**

Write Bull and Bear sequentially in the same context using the prompts below. Acknowledge that debate quality is reduced in this mode — the Research Manager should account for this by applying independent judgment rather than relying solely on debate outcomes.

### BULL ANALYST prompt (each round):
> You are a Bull Analyst advocating for investing in this stock. Build a strong, evidence-based case using the market report, sentiment report, news report, and fundamentals report provided.
>
> Debate history so far: {full_debate_history}
> Last bear argument: {last_bear_argument}  ← (empty in Round 1)
>
> ROLE RULES: You are a committed bull. Do NOT acknowledge the bear is correct on any point — refute every claim with data. Do NOT say "the bear makes a fair point." Be adversarial. Pull no punches.
>
> Focus on:
> - **Growth Potential**: Market opportunities, revenue projections, scalability
> - **Competitive Advantages**: Unique products, strong branding, dominant market positioning
> - **Positive Indicators**: Financial health, industry trends, recent positive news
> - **Bear Counterpoints**: From Round 2 onward, directly attack every bear point with specific data.
> - **Style**: Conversational, engaging, debating — not just listing data
>
> Use the actual numbers. Be specific. Start Round 1 with your opening case. From Round 2 onward, lead with rebuttals before making new points.

### BEAR ANALYST prompt (each round):
> You are a Bear Analyst making the case against investing in this stock. Present a well-reasoned argument using the market report, sentiment report, news report, and fundamentals report provided.
>
> Debate history so far: {full_debate_history}
> Last bull argument: {last_bull_argument}  ← (always provided — Bear never goes first)
>
> ROLE RULES: You are a committed bear. Do NOT acknowledge the bull is correct on any point — expose every claim's weakness with data. Do NOT say "the bull makes a fair point." Be adversarial. Pull no punches.
>
> Focus on:
> - **Risks and Challenges**: Market saturation, financial instability, macroeconomic threats
> - **Competitive Weaknesses**: Vulnerabilities, declining innovation, threats from competitors
> - **Negative Indicators**: Financial data, market trends, adverse news
> - **Bull Counterpoints**: Directly attack every bull point with specific data. Expose overconfidence.
> - **Style**: Conversational, engaging, debating — not just listing facts
>
> Use the actual numbers. Be specific. Lead with rebuttals to the bull's last argument before making new points.

**Output stored as:** `investment_debate_history` (append each round in order)

---

## AGENT 7 — RESEARCH MANAGER

**Execution (Claude Code mode):** Main agent writes directly — no sub-agent spawn. By this point the main agent has all analyst reports and the full debate history in context.

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

**Execution (Claude Code mode):** Main agent writes directly — no sub-agent spawn. Has Research Manager verdict and market report in context.

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
- Aggressive opens based on trader's proposal + market.md + fundamentals.md + full debate history
- Conservative reads same files from disk + reads `aggressive.md` written by main after Aggressive returns
- Neutral written by main directly — already has both outputs in context, zero extra token cost

Note: news.md and sentiment.md are intentionally excluded from Risk agents — those insights are already synthesized in the full Bull/Bear debate history passed to each agent.

---

### EXECUTION — Claude Code mode vs Web chat mode

**In Claude Code mode (Agent tool available):**

Spawn Aggressive and Conservative as **two separate sequential sub-agents from main**. Main writes `aggressive.md` to disk after Aggressive returns so Conservative can read it. Neutral is written by main directly — no spawn needed.

**Step 1 — Main spawns Aggressive:**
```
You are the Aggressive Risk Analyst evaluating a trader's proposal for {TICKER}.

Read your inputs from these files (already written to disk):
- reports/{RUN_ID}/3_trading/trader.md
- reports/{RUN_ID}/1_analysts/market.md
- reports/{RUN_ID}/1_analysts/fundamentals.md

Note: news and sentiment insights are already embedded in the debate history below.

Additional context passed directly:
- Full Bull/Bear debate history: {full_debate_history}

ROLE RULES — NO EXCEPTIONS:
- You champion high-reward, high-risk opportunities. You believe bold action is the right call.
- Do NOT acknowledge downside risks as decisive. Frame every risk as manageable or overstated.
- Do NOT soften your position. Be forceful and data-driven.
- Present your opening case for why the trader should take maximum position size and aggressive entry.
- Use actual numbers from the files as evidence.

Return ONLY your analysis. Do not spawn further agents.
```
→ Main receives output, writes to `reports/{RUN_ID}/4_risk/aggressive.md`

**Step 2 — Main spawns Conservative:**
```
You are the Conservative Risk Analyst evaluating a trader's proposal for {TICKER}.

Read your inputs from these files (already written to disk):
- reports/{RUN_ID}/3_trading/trader.md
- reports/{RUN_ID}/1_analysts/market.md
- reports/{RUN_ID}/1_analysts/fundamentals.md
- reports/{RUN_ID}/4_risk/aggressive.md  ← Aggressive's full argument

ROLE RULES — NO EXCEPTIONS:
- You prioritize capital protection above all else. You believe caution is always warranted.
- Do NOT acknowledge upside as the primary consideration. Frame every opportunity as carrying hidden risk.
- Directly attack the aggressive analyst's argument point by point — expose where their optimism ignores real threats.
- Do NOT soften your position. Be forceful in defending a smaller position size, tighter stop, or no entry.
- Use actual numbers from the files as evidence.

Return ONLY your analysis. Do not spawn further agents.
```
→ Main receives output, writes to `reports/{RUN_ID}/4_risk/conservative.md`

**Step 3 — Main writes Neutral directly** (has both outputs in context, no spawn):
```
You are the Neutral Risk Analyst for {TICKER}. Provide a genuinely balanced, independent assessment.

You have already seen:
- Aggressive argument: {aggressive_output}
- Conservative argument: {conservative_output}
- Trader's proposal and analyst reports: already in your context from this run

ROLE RULES:
- Challenge BOTH sides where they overreach — not a compromise, an independent verdict.
- Point out where Aggressive ignores real risks and where Conservative overstates them.
- Deliver a balanced position sizing and entry recommendation grounded in data from both sides.
- Flag any structural problems in the trading plan (entry/stop proximity, R:R inconsistency, etc.).
```
→ Main writes to `reports/{RUN_ID}/4_risk/neutral.md`

**Spawn count for risk panel: 2 from main** (Aggressive, Conservative). Neutral written by main for free.

---

**In Web chat mode (no Agent tool):**

Write Aggressive, Conservative, and Neutral sequentially in the same context using the prompts below.

### AGGRESSIVE RISK ANALYST prompt:
> As the Aggressive Risk Analyst, your role is to actively champion high-reward, high-risk opportunities, emphasizing bold strategies and competitive advantages. When evaluating the trader's decision or plan, focus intently on the potential upside, growth potential, and innovative benefits — even when these come with elevated risk.
>
> Trader's proposal: {trader_decision}
> Risk debate history so far: {risk_debate_history}
> Last conservative argument: {last_conservative_response}  ← (empty in Round 1)
> Last neutral argument: {last_neutral_response}  ← (empty in Round 1)
>
> ROLE RULES: You champion bold action. Do NOT acknowledge downside as decisive. Frame every risk as manageable. Be forceful.
>
> Use the market report, sentiment report, news report, and fundamentals report as evidence. Be conversational, not just data-listing.

### CONSERVATIVE RISK ANALYST prompt:
> As the Conservative Risk Analyst, your primary objective is to protect assets, minimize volatility, and ensure steady, reliable growth. You prioritize stability, security, and risk mitigation — carefully assessing potential losses, economic downturns, and market volatility.
>
> Trader's proposal: {trader_decision}
> Risk debate history so far: {risk_debate_history}
> Last aggressive argument: {last_aggressive_response}  ← (always provided — Conservative never goes first)
> Last neutral argument: {last_neutral_response}  ← (empty in Round 1)
>
> ROLE RULES: You prioritize capital protection above all. Do NOT acknowledge upside as the primary driver. Directly attack the aggressive argument. Be forceful in defending smaller size or no entry.
>
> Use the market report, sentiment report, news report, and fundamentals report as evidence. Be conversational, not just data-listing.

### NEUTRAL RISK ANALYST prompt:
> As the Neutral Risk Analyst, your role is to provide a balanced perspective, weighing both the potential benefits and risks of the trader's decision. Evaluate the upsides and downsides while factoring in broader market trends, potential economic shifts, and diversification strategies.
>
> Trader's proposal: {trader_decision}
> Risk debate history so far: {risk_debate_history}
> Last aggressive argument: {last_aggressive_response}  ← (always provided — Neutral never goes first)
> Last conservative argument: {last_conservative_response}  ← (always provided — Neutral never goes first)
>
> ROLE RULES: Challenge BOTH sides where they overreach. Deliver a genuinely independent balanced recommendation — not a split-the-difference compromise.
>
> Use the market report, sentiment report, news report, and fundamentals report as evidence. Be conversational, not just data-listing.

---

**Output stored as:** `risk_debate_history` (append each analyst's response in order)

---

## AGENT 10 — PORTFOLIO MANAGER (FINAL DECISION)

**Execution (Claude Code mode):** Main agent writes directly — no sub-agent spawn. Has full run context: all analyst reports, debate, Research Manager verdict, Trader plan, and all risk panel outputs.

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

| Agent | Role | Key output |
|-------|------|-----------|
| 1. Market Analyst | Technicals | Trend, indicators, support/resistance |
| 2. Sentiment Analyst | Social mood | Score /10, band, confidence |
| 3. News Analyst | Events | Catalysts, risks, macro context |
| 4. Fundamentals | Financials | Valuation, margins, balance sheet |
| 5/6. Bull/Bear (×N) | Debate | 1/2/3-round debate (Fast/Medium/Deep) |
| 7. Research Manager | Verdict | Rating + investment plan |
| 8. Trader | Execution | Entry, stop, position size |
| 9. Risk Panel (×3) | Risk stress test | Aggressive→Conservative→Neutral (Deep only) |
| 10. Portfolio Manager | Final decision | Rating, targets, time horizon |

---

## OUTPUT STRUCTURE

### Step 0 — Detect environment before Agent 1 starts

Check whether file-writing tools (Write / Edit / Bash) are available:

- **If tools are available → Claude Code mode** (writing to files)
- **If no tools available → Web chat mode** (output in chat only)

Announce the mode once at the start:
```
Environment: Claude Code — writing to reports/AMD_20260605_043116/
```
or:
```
Environment: Web chat — full output in chat, copy-paste to save at end
```

---

### Claude Code mode

Do NOT wait until the end to save. Write each agent's output to disk immediately after generating it. Print only a one-line status to chat per agent.

**Directory:** Read the `Report dir` field from the data file header. Use it exactly — do not generate a new timestamp.

```
Run ID    : AMD_20260605_043116
Report dir: reports/AMD_20260605_043116/
```

Create the directory before starting Agent 1. Write each file as the agent completes.

**File layout:**
```
reports/AMD_20260605_043116/
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

Create all subdirectories before starting Agent 1.

**Token tracking:** For every step, capture token usage as follows:
- **Sub-agent steps** (Bull R1, Bear R1, Aggressive, Conservative): read `subagent_tokens` from the Agent tool result — this is the exact isolated count
- **SendMessage steps** (Bull R2/R3, Bear R2/R3): read `subagent_tokens` from the SendMessage result
- **Main-agent steps** (Analysts 1–4, Research Manager, Trader, Neutral, Portfolio Manager): estimate by counting the approximate word count of the output × 1.3 (words-to-tokens ratio) — mark these as `~estimated`

Store each count in a `token_log` dict keyed by agent name. Print the full table at the end (see token summary format below).

**Chat output per agent** — one line only (repeat Bull/Bear block N times based on mode):
```
✓ Market Analyst    → 1_analysts/market.md           [~2,100 tokens estimated]
✓ Sentiment Analyst → 1_analysts/sentiment.md        [~1,800 tokens estimated]
✓ News Analyst      → 1_analysts/news.md             [~1,900 tokens estimated]
✓ Fundamentals      → 1_analysts/fundamentals.md     [~2,000 tokens estimated]
✓ Bull R1            → 2_research/bull.md (appended) [23,618 tokens]
✓ Bear R1            → 2_research/bear.md (appended) [23,729 tokens]
  ← Fast stops here
✓ Bull R2            → 2_research/bull.md (appended) [23,802 tokens]
✓ Bear R2            → 2_research/bear.md (appended) [24,480 tokens]
  ← Medium stops here
✓ Bull R3            → 2_research/bull.md (appended) [23,333 tokens]
✓ Bear R3            → 2_research/bear.md (appended) [23,344 tokens]
  ← Deep stops here
✓ Research Manager  → 2_research/manager.md          [~2,100 tokens estimated]
✓ Trader            → 3_trading/trader.md            [~1,800 tokens estimated]
✓ Aggressive Risk   → 4_risk/aggressive.md           [18,734 tokens]  ← Deep only
✓ Conservative Risk → 4_risk/conservative.md         [19,045 tokens]  ← Deep only
✓ Neutral Risk      → 4_risk/neutral.md              [~2,400 tokens estimated]  ← Deep only
✓ Portfolio Manager → 5_portfolio/decision.md        [~1,600 tokens estimated]
✓ Complete report   → complete_report.md
```

**After Portfolio Manager:** write `complete_report.md` (all agents concatenated in pipeline order), then print the token summary table, then print the final decision table to chat (see formats below).

**Token summary format** — print after complete_report.md is written:
```
## Token Usage — TICKER — RUN_ID

| Agent                | Type        | Tokens        |
|----------------------|-------------|---------------|
| Market Analyst       | main agent  | ~2,100 est.   |
| Sentiment Analyst    | main agent  | ~1,800 est.   |
| News Analyst         | main agent  | ~1,900 est.   |
| Fundamentals Analyst | main agent  | ~2,000 est.   |
| Bull R1              | sub-agent   | 23,618        |
| Bear R1              | sub-agent   | 23,729        |
| Bull R2              | SendMessage | 23,802        |
| Bear R2              | SendMessage | 24,480        |
| Bull R3              | SendMessage | 23,333        |  ← Deep only
| Bear R3              | SendMessage | 23,344        |  ← Deep only
| Research Manager     | main agent  | ~2,100 est.   |
| Trader               | main agent  | ~1,800 est.   |
| Aggressive Risk      | sub-agent   | 18,734        |  ← Deep only
| Conservative Risk    | sub-agent   | 19,045        |  ← Deep only
| Neutral Risk         | main agent  | ~2,400 est.   |  ← Deep only
| Portfolio Manager    | main agent  | ~1,600 est.   |
|----------------------|-------------|---------------|
| TOTAL                |             | 231,249       |
| (of which estimated) |             | (~7,900 est.) |
```

---

### Web chat mode

No file tools available. Output each agent's content in chat inside a fenced markdown block so the user can read it as it generates. Do not suppress or shorten the output.

**Per agent:** output a fenced block with a path comment at the top:

~~~
```markdown
<!-- 1_analysts/market.md -->

[full agent output here]
```
~~~

**After Portfolio Manager:** output one final combined fenced block containing all agents concatenated — this is the single copy-paste block the user saves as `complete_report.md`:

~~~
```markdown
<!-- SAVE AS: reports/AMD_20260605_043116/complete_report.md -->

[all agent outputs combined]
```
~~~

Then print the summary table to chat (see summary format below).

---

### Summary table (both modes)

Print this to chat after the Portfolio Manager in both modes:

```
## Summary — TICKER — RUN_ID

| Parameter     | Value |
|---------------|-------|
| Signal        | BUY/SELL/HOLD |
| Rating        | Overweight/etc |
| Entry         | $xxx (primary limit) |
| Secondary entry| $xxx (omit this row if Agent 8 skipped it) |
| Breakout entry| $xxx on close >$xxx vol >35M (omit this row if Agent 8 skipped it) |
| Stop Loss     | $xxx |
| Target 1      | $xxx (timeframe) |
| Target 2      | $xxx (timeframe) |
| R:R           | x:1 |
| Position Size | x% |
| Confidence    | High/Medium/Low |
| Mode          | Fast/Medium/Deep |
| Report dir    | reports/TICKER_YYYYMMDD_HHMMSS/ |
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
- Always detect environment (Claude Code vs web chat) before Agent 1 — announce it once
- Always ask for mode before starting — do not assume Deep
- Always check data is present before starting — ask user to run fetch_data.py if missing
- Do NOT ask to save — in Claude Code mode write files automatically; in web chat output full blocks
- Stop loss must always be placed minimum **1.5×ATR** below entry
- Price target must always be **above current price** (sanity check)
- If data sources are missing (Reddit/StockTwits), flag in sentiment confidence — do not fabricate
- **Claude Code sub-agent strategy (token-efficient):**
  - **Main agent writes directly (no spawn):** Analysts 1–4, Research Manager, Trader, Neutral Risk, Portfolio Manager. Analysts 1–4 use data already in context from fetch_data.py — spawning sub-agents would duplicate the entire data payload per agent (4× waste). Synthesizer roles need full context anyway.
  - **Spawn as persistent parallel agents (2 for debate):** One Bull agent + one Bear agent, each handling ALL rounds for their side. They run concurrently, coordinate through disk files via polling loops, and are configurable by mode (N=1/2/3). **No SendMessage needed. No re-spawning between rounds.**
  - **Spawn as sequential sub-agents (2 for risk):** Main spawns Aggressive first, writes `aggressive.md` to disk, then spawns Conservative which reads `aggressive.md` from disk. Neutral written by main directly (already has both in context).
  - **Total spawns per Deep run: 4** (Bull debate agent, Bear debate agent, Aggressive Risk, Conservative Risk)
  - **Disk is the communication channel:** Sub-agents always read from disk files. Main agent always writes to disk. Sub-agents only return text.
  - Isolation is unnecessary for: Analysts (fetch data already in main context), synthesizer roles (Research Manager, Trader, Neutral, Portfolio Manager)
- **Web chat debate quality:** Single-context sequential writing is a known limitation. The Research Manager and Portfolio Manager should apply independent judgment and not over-rely on debate outcomes when running in web chat mode.
