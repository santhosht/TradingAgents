"""
score_candidates.py — Score near-5yr-low candidates on fundamental quality.

Reads sp500_lows.csv by default (output of find_5yr_lows.py --sp500).
Scores each symbol on 5 dimensions, ranks them, flags likely value traps.

Usage:
    python3 scripts/score_candidates.py
    python3 scripts/score_candidates.py --input sp500_lows.csv
    python3 scripts/score_candidates.py --symbols NKE LULU INTU
    python3 scripts/score_candidates.py --output scored.csv

Scoring (max 14 pts):
    FCF         (0-3)  positive & growing > positive flat > negative
    EPS Trend   (0-3)  growing YoY > flat > declining > negative
    Debt (D/E)  (0-3)  low debt rewarded, negative equity = 0
    Analyst     (0-3)  buy > hold > underperform > sell
    Revenue     (0-2)  growing > flat > declining
"""

import argparse
import os
import sys
import time
import warnings

import pandas as pd
import yfinance as yf

warnings.filterwarnings("ignore")

DEFAULT_INPUT = os.path.join(os.path.dirname(__file__), "..", "sp500_lows.csv")


# ── Scoring helpers ───────────────────────────────────────────────────────────

def score_fcf(info: dict, cashflow: pd.DataFrame) -> tuple[int, str]:
    fcf = info.get("freeCashflow")
    if fcf is None:
        return 0, "N/A"

    # Try to get prior year FCF from quarterly cashflow
    trend = "stable"
    if cashflow is not None and not cashflow.empty:
        try:
            fcf_row = None
            for key in ["Free Cash Flow", "FreeCashFlow"]:
                if key in cashflow.index:
                    fcf_row = cashflow.loc[key]
                    break
            if fcf_row is not None and len(fcf_row) >= 4:
                recent  = fcf_row.iloc[:2].sum()   # last 2 quarters
                prior   = fcf_row.iloc[2:4].sum()  # prior 2 quarters
                if prior != 0:
                    chg = (recent - prior) / abs(prior)
                    trend = "growing" if chg > 0.05 else ("declining" if chg < -0.05 else "stable")
        except Exception:
            pass

    if fcf > 0 and trend == "growing":
        return 3, f"${fcf/1e9:.1f}B ↑"
    if fcf > 0 and trend == "stable":
        return 2, f"${fcf/1e9:.1f}B →"
    if fcf > 0:
        return 1, f"${fcf/1e9:.1f}B ↓"
    return 0, f"${fcf/1e9:.1f}B (neg)"


def score_eps(info: dict, income: pd.DataFrame) -> tuple[int, str]:
    eps_ttm = info.get("trailingEps")
    if eps_ttm is None:
        return 0, "N/A"

    # EPS trend from quarterly income statement
    trend = "unknown"
    if income is not None and not income.empty:
        try:
            eps_row = None
            for key in ["Diluted EPS", "Basic EPS"]:
                if key in income.index:
                    eps_row = income.loc[key]
                    break
            if eps_row is not None and len(eps_row) >= 4:
                recent = eps_row.iloc[:2].sum()
                prior  = eps_row.iloc[2:4].sum()
                if prior != 0 and not pd.isna(prior) and not pd.isna(recent):
                    chg = (recent - prior) / abs(prior)
                    trend = "growing" if chg > 0.05 else ("declining" if chg < -0.05 else "stable")
        except Exception:
            pass

    if eps_ttm > 0 and trend == "growing":  return 3, f"${eps_ttm:.2f} ↑"
    if eps_ttm > 0 and trend in ("stable", "unknown"): return 2, f"${eps_ttm:.2f} →"
    if eps_ttm > 0:                         return 1, f"${eps_ttm:.2f} ↓"
    return 0, f"${eps_ttm:.2f} (neg)"


def score_debt(info: dict) -> tuple[int, str]:
    de = info.get("debtToEquity")
    if de is None:
        return 1, "N/A"
    # yfinance returns D/E as a percentage (e.g. 150 = 1.5x)
    de_ratio = de / 100 if de > 10 else de
    if de_ratio < 0:    return 0, f"{de_ratio:.1f}x (neg equity)"
    if de_ratio < 0.5:  return 3, f"{de_ratio:.1f}x"
    if de_ratio < 1.5:  return 2, f"{de_ratio:.1f}x"
    if de_ratio < 3.0:  return 1, f"{de_ratio:.1f}x"
    return 0, f"{de_ratio:.1f}x (high)"


def score_analyst(info: dict) -> tuple[int, str]:
    rec = (info.get("recommendationKey") or "").lower()
    mapping = {
        "strong_buy": (3, "Strong Buy"),
        "buy":        (3, "Buy"),
        "hold":       (2, "Hold"),
        "underperform": (1, "Underperform"),
        "sell":       (0, "Sell"),
    }
    return mapping.get(rec, (1, rec.title() or "N/A"))


def score_revenue(info: dict, income: pd.DataFrame) -> tuple[int, str]:
    trend = "unknown"
    if income is not None and not income.empty:
        try:
            rev_row = None
            for key in ["Total Revenue", "Operating Revenue"]:
                if key in income.index:
                    rev_row = income.loc[key]
                    break
            if rev_row is not None and len(rev_row) >= 4:
                recent = float(rev_row.iloc[:2].sum())
                prior  = float(rev_row.iloc[2:4].sum())
                if prior > 0:
                    chg = (recent - prior) / prior
                    trend = "growing" if chg > 0.03 else ("declining" if chg < -0.03 else "stable")
                    label = f"{chg*100:+.1f}% YoY"
                    if trend == "growing":   return 2, label + " ↑"
                    if trend == "stable":    return 1, label + " →"
                    return 0, label + " ↓"
        except Exception:
            pass

    rev = info.get("totalRevenue")
    if rev:
        return 1, f"${rev/1e9:.1f}B (trend N/A)"
    return 0, "N/A"


# ── Per-symbol fetch & score ──────────────────────────────────────────────────

def fetch_and_score(sym: str) -> dict | None:
    try:
        t       = yf.Ticker(sym)
        info    = t.info or {}
        try:
            income   = t.quarterly_income_stmt
        except Exception:
            income = None
        try:
            cashflow = t.quarterly_cashflow
        except Exception:
            cashflow = None

        fcf_score,  fcf_label  = score_fcf(info, cashflow)
        eps_score,  eps_label  = score_eps(info, income)
        debt_score, debt_label = score_debt(info)
        ana_score,  ana_label  = score_analyst(info)
        rev_score,  rev_label  = score_revenue(info, income)

        total = fcf_score + eps_score + debt_score + ana_score + rev_score
        trap  = total <= 5  # likely value trap if low score

        return {
            "Symbol":     sym,
            "Name":       info.get("shortName") or info.get("longName") or "",
            "Score":      total,
            "FCF":        fcf_label,
            "EPS Trend":  eps_label,
            "D/E":        debt_label,
            "Analyst":    ana_label,
            "Revenue":    rev_label,
            "Trap?":      "⚠ Trap" if trap else "",
            # raw scores for CSV
            "FCF_score":  fcf_score,
            "EPS_score":  eps_score,
            "Debt_score": debt_score,
            "Ana_score":  ana_score,
            "Rev_score":  rev_score,
        }
    except Exception as e:
        return {"Symbol": sym, "Score": -1, "Name": f"error: {e}"}


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Score near-5yr-low candidates")
    parser.add_argument("--input",   default=DEFAULT_INPUT,
                        help="CSV from find_5yr_lows.py (default: sp500_lows.csv)")
    parser.add_argument("--symbols", nargs="+", default=None,
                        help="Override: score these symbols directly")
    parser.add_argument("--output",  default=None,
                        help="Save full scored table to this CSV path")
    args = parser.parse_args()

    if args.symbols:
        symbols = [s.upper() for s in args.symbols]
    else:
        path = os.path.abspath(args.input)
        if not os.path.exists(path):
            print(f"Input file not found: {path}")
            sys.exit(1)
        df_in = pd.read_csv(path)
        # Filter to Near Low? == True if column exists
        if "Near Low?" in df_in.columns:
            df_in = df_in[df_in["Near Low?"] == True]
        symbols = df_in["Symbol"].tolist()

    print(f"\n{'='*60}")
    print(f"  FUNDAMENTAL SCORER — {len(symbols)} candidates")
    print(f"  Scoring: FCF(3) + EPS(3) + D/E(3) + Analyst(3) + Revenue(2) = 14 max")
    print(f"{'='*60}\n")

    rows = []
    for i, sym in enumerate(symbols, 1):
        print(f"  [{i}/{len(symbols)}] {sym:<8}", end=" ", flush=True)
        result = fetch_and_score(sym)
        if result:
            rows.append(result)
            score = result.get("Score", -1)
            trap  = result.get("Trap?", "")
            print(f"score={score}/14  {trap}")
        time.sleep(0.3)

    df = pd.DataFrame(rows).sort_values("Score", ascending=False).reset_index(drop=True)

    display_cols = ["Symbol", "Name", "Score", "FCF", "EPS Trend", "D/E", "Analyst", "Revenue", "Trap?"]
    df_disp = df[[c for c in display_cols if c in df.columns]]

    print(f"\n{'='*70}")
    print(f"  RESULTS — ranked by score (14 = strongest fundamentals)")
    print(f"{'='*70}")
    print(df_disp.to_string(index=False))

    strong  = df[df["Score"] >= 9]
    ok      = df[(df["Score"] >= 6) & (df["Score"] < 9)]
    traps   = df[df["Score"] < 6]

    print(f"\n  Tier 1 — Analyze first  (score ≥ 9): {len(strong)} symbols")
    if not strong.empty:
        print("   ", ", ".join(strong["Symbol"].tolist()))

    print(f"  Tier 2 — Analyze if time (score 6-8): {len(ok)} symbols")
    if not ok.empty:
        print("   ", ", ".join(ok["Symbol"].tolist()))

    print(f"  Tier 3 — Likely traps   (score < 6): {len(traps)} symbols")
    if not traps.empty:
        print("   ", ", ".join(traps["Symbol"].tolist()))

    if args.output:
        df.to_csv(args.output, index=False)
        print(f"\n  Saved to {args.output}")


if __name__ == "__main__":
    main()
