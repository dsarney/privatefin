"""Compare PrivateFin RSI/MACD output with TA-Lib on fixed market-data windows.

Run from the repository root:
    python documentation/evaluation/validate_indicators.py

The script writes machine-readable row-level results and a compact JSON summary.  Yahoo
Finance's historical data can be revised, so the run date and fixed date ranges are
recorded alongside every result.
"""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import talib

from src.engine.data_loader import download_stock_data
from src.engine.indicator_engine import enrich_with_indicators


OUTPUT_DIR = Path("documentation/evaluation/results")
END_DATE = date(2026, 7, 20)
WINDOW_DAYS = (365, 182, 90)
TICKERS: dict[str, str | list[str]] = {
    "AAPL": "AAPL",
    "MSFT": "MSFT",
    "TSLA": "TSLA",
    "JPM": "JPM",
    "JNJ": "JNJ",
    "XOM": "XOM",
    "GOOG_GOOGL": ["GOOG", "GOOGL"],
    "AMZN": "AMZN",
    "NVDA": "NVDA",
    "KO": "KO",
}


def _last_finite_pair(left: pd.Series, right: pd.Series) -> tuple[float, float]:
    paired = pd.concat([left.rename("privatefin"), right.rename("reference")], axis=1)
    paired = paired.replace([np.inf, -np.inf], np.nan).dropna()
    if paired.empty:
        raise ValueError("No overlapping finite values were produced.")
    latest = paired.iloc[-1]
    return float(latest["privatefin"]), float(latest["reference"])


def _difference_metrics(left: pd.Series, right: pd.Series) -> tuple[float, float]:
    paired = pd.concat([left.rename("privatefin"), right.rename("reference")], axis=1)
    paired = paired.replace([np.inf, -np.inf], np.nan).dropna()
    differences = (paired["privatefin"] - paired["reference"]).abs()
    return float(differences.mean()), float(differences.max())


def evaluate_window(
    label: str, ticker: str | list[str], days: int
) -> list[dict[str, object]]:
    start_date = END_DATE - timedelta(days=days)
    frame = download_stock_data(
        ticker,
        start_date.isoformat(),
        END_DATE.isoformat(),
        save=False,
    )
    if frame is None or frame.empty:
        raise RuntimeError(f"No market data returned for {label}, {days} days.")

    enriched = enrich_with_indicators(frame)
    close = enriched["Close"].astype(float)
    reference_rsi = pd.Series(
        talib.RSI(close.to_numpy(), timeperiod=14), index=close.index
    )
    reference_macd_values, reference_signal_values, reference_hist_values = talib.MACD(
        close.to_numpy(), fastperiod=12, slowperiod=26, signalperiod=9
    )
    references = {
        "RSI_14": reference_rsi,
        "MACD": pd.Series(reference_macd_values, index=close.index),
        "MACD_Signal": pd.Series(reference_signal_values, index=close.index),
        "MACD_Histogram": pd.Series(reference_hist_values, index=close.index),
    }

    rows: list[dict[str, object]] = []
    for metric, reference in references.items():
        privatefin_value, reference_value = _last_finite_pair(
            enriched[metric], reference
        )
        mean_absolute_error, maximum_absolute_error = _difference_metrics(
            enriched[metric], reference
        )
        rows.append(
            {
                "ticker": label,
                "source_tickers": (
                    ",".join(ticker) if isinstance(ticker, list) else ticker
                ),
                "window_days": days,
                "start_date": start_date.isoformat(),
                "end_date_exclusive": END_DATE.isoformat(),
                "observations": len(frame),
                "metric": metric,
                "privatefin_latest": privatefin_value,
                "talib_latest": reference_value,
                "latest_absolute_difference": abs(
                    privatefin_value - reference_value
                ),
                "latest_agrees_4dp": round(privatefin_value, 4)
                == round(reference_value, 4),
                "mean_absolute_error_over_overlap": mean_absolute_error,
                "maximum_absolute_error_over_overlap": maximum_absolute_error,
            }
        )
    return rows


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    failures: list[dict[str, object]] = []

    for label, ticker in TICKERS.items():
        for days in WINDOW_DAYS:
            try:
                rows.extend(evaluate_window(label, ticker, days))
            except Exception as exc:  # Preserve partial evidence if a provider call fails.
                failures.append(
                    {"ticker": label, "window_days": days, "error": str(exc)}
                )

    result_frame = pd.DataFrame(rows)
    result_path = OUTPUT_DIR / "indicator-validation.csv"
    result_frame.to_csv(result_path, index=False)

    agreement_by_metric = (
        result_frame.groupby("metric")["latest_agrees_4dp"]
        .agg(["sum", "count"])
        .reset_index()
        .to_dict(orient="records")
        if not result_frame.empty
        else []
    )
    summary = {
        "run_date": date.today().isoformat(),
        "reference": "TA-Lib 0.7.1",
        "fixed_end_date_exclusive": END_DATE.isoformat(),
        "ticker_groups_requested": len(TICKERS),
        "windows_per_ticker_requested": len(WINDOW_DAYS),
        "comparisons_completed": len(rows),
        "window_failures": failures,
        "agreement_to_four_decimal_places_by_metric": agreement_by_metric,
        "important_interpretation": (
            "A disagreement does not by itself show an algebraic error. TA-Lib and "
            "pandas EWM can use different seed/initialisation conventions, especially "
            "for RSI and the MACD signal line. Report observed differences and the "
            "chosen convention rather than claiming equivalence."
        ),
    }
    summary_path = OUTPUT_DIR / "indicator-validation-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2))
    print(f"Wrote {result_path}")
    print(f"Wrote {summary_path}")


if __name__ == "__main__":
    main()
