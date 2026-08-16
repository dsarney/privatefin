"""Tests for technical indicator calculations and summaries.

These checks lock in the engine's public contract: RSI stays on a 0–100 scale,
MACD columns stay consistent, and the latest-value summary uses the same
classification rules as the UI and prompt builder.
"""

import pandas as pd
import pytest

from src.engine.indicator_engine import (
    compute_macd,
    compute_rsi,
    enrich_with_indicators,
    summarize_latest_indicators,
)


def test_compute_rsi_stays_within_expected_bounds():
    """RSI is a 0–100 oscillator, even on a short synthetic price series."""
    close = pd.Series([100, 101, 102, 103, 102, 101, 102, 103, 104, 103, 104, 105])

    rsi = compute_rsi(close, period=5)

    assert ((rsi >= 0) & (rsi <= 100)).all()


def test_compute_macd_contains_expected_columns_and_histogram_relation():
    """MACD output must expose line, signal, and histogram, with histogram = line − signal."""
    close = pd.Series([100, 101, 102, 101, 103, 104, 105, 106, 104, 103])

    result = compute_macd(close)

    assert list(result.columns) == ["MACD", "MACD_Signal", "MACD_Histogram"]
    pd.testing.assert_series_equal(
        result["MACD_Histogram"],
        result["MACD"] - result["MACD_Signal"],
        check_names=False,
    )


def test_enrich_with_indicators_adds_indicator_columns():
    """Enrichment should attach RSI/MACD columns without dropping price rows."""
    prices = pd.DataFrame({"Close": [100, 101, 103, 102, 104, 106, 107]})

    enriched = enrich_with_indicators(prices)

    assert "RSI_14" in enriched.columns
    assert "MACD" in enriched.columns
    assert "MACD_Signal" in enriched.columns
    assert "MACD_Histogram" in enriched.columns
    assert len(enriched) == len(prices)


def test_enrich_with_indicators_requires_close_column():
    """Close prices are required because every indicator is derived from them."""
    with pytest.raises(ValueError, match="must include a 'Close' column"):
        enrich_with_indicators(pd.DataFrame({"Open": [1, 2, 3]}))


def test_summarize_latest_indicators_classifies_bullish_overbought():
    """The last row drives classification: MACD above signal and RSI >= 70."""
    # Latest MACD (1.2) > signal (0.9) => bullish; latest RSI (75) => overbought.
    # Close moves 100 → 110, so the one-session change should be +10%.
    frame = pd.DataFrame(
        {
            "Close": [100.0, 110.0],
            "RSI_14": [65.0, 75.0],
            "MACD": [0.5, 1.2],
            "MACD_Signal": [0.6, 0.9],
            "MACD_Histogram": [-0.1, 0.3],
        }
    )

    summary = summarize_latest_indicators(frame)

    assert summary["trend"] == "bullish"
    assert summary["momentum"] == "overbought"
    assert summary["price_change_pct"] == pytest.approx(10.0)


def test_summarize_latest_indicators_rejects_empty_frame():
    """An empty frame has no latest row, so summarising it should fail clearly."""
    with pytest.raises(ValueError, match="Cannot summarize an empty frame"):
        summarize_latest_indicators(pd.DataFrame())
