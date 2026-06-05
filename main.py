from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# DEFAULT_CONFIG already applies TRADINGAGENTS_* env-var overrides
# (llm_provider, deep_think_llm, quick_think_llm, backend_url, etc.),
# so users can switch models or endpoints purely via .env without
# editing this script. Override individual keys here only when you
# want a hard-coded value that should ignore the environment.
config = DEFAULT_CONFIG.copy()

# Initialize with custom config
ta = TradingAgentsGraph(debug=True, config=config)

# forward propagate
final_state, decision = ta.propagate("AMD", "2026-06-05")
print("\n" + "="*60)
print("FINAL PORTFOLIO DECISION")
print("="*60)
print(final_state.get("final_trade_decision", "No decision recorded"))
print("="*60)
print(f"Extracted signal: {decision}")

# Memorize mistakes and reflect
# ta.reflect_and_remember(1000) # parameter is the position returns
