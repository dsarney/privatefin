"""Deterministic technical-indicator calculations used by the UI and LLM prompt.

The language model never calculates or modifies these values.  This module is the
quantitative source of truth, allowing displayed figures and generated explanations to
be checked against the same summary dictionary.
"""

from __future__ import annotations

import pandas as pd


def _as_close_series(close: pd.Series | pd.DataFrame) -> pd.Series:
    """Normalise supported close-price inputs to one floating-point Series."""
    if isinstance(close, pd.DataFrame):
        if close.shape[1] != 1:
            raise ValueError("Expected a single close-price series.")
        # Accept single-column frames so callers can pass sliced data directly.
        close = close.iloc[:, 0]

    if not isinstance(close, pd.Series):
        close = pd.Series(close)

    return close.astype(float)


def _scalar_from_row(row: pd.Series, label: str, default: float) -> float:
    """Extract a float even when duplicate labels make pandas return a Series."""
    value = row.get(label, default)
    if isinstance(value, pd.Series):
        # Duplicate/grouped labels can occur after unusual yfinance column shapes.
        if value.empty:
            return float(default)
        value = value.iloc[0]
    return float(value)


def compute_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    """Compute RSI using recursive Wilder-style exponential smoothing.

    RSI maps relative average gains and losses onto a 0–100 scale.  PrivateFin uses
    ``alpha=1/period`` and a neutral value during the initial warm-up period.  This
    explicit convention matters because reference libraries may seed their averages
    differently on short input histories.
    """
    close = _as_close_series(close)

    # Positive and negative movements are separated before their rolling averages are
    # compared; losses are negated so both component series contain positive magnitudes.
    delta = close.diff()
    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)

    average_gain = gains.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    average_loss = losses.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()

    relative_strength = average_gain / average_loss
    rsi = 100 - (100 / (1 + relative_strength))

    # A period with no losses represents maximum upward strength; a period with no
    # gains represents maximum downward weakness.  Handle both before filling warm-up
    # values so infinities or missing values cannot reach the prompt.
    rsi = rsi.where(average_loss != 0, 100)
    rsi = rsi.where(average_gain != 0, 0)
    return rsi.fillna(50.0)


def compute_macd(
    close: pd.Series,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
) -> pd.DataFrame:
    """Compute the MACD line, signal line, and their difference.

    The default 12/26/9 periods are the conventional MACD parameters.  A positive
    histogram means the MACD line is above its signal line; a negative histogram means
    it is below.
    """
    close = _as_close_series(close)

    # MACD compares short- and long-horizon exponential averages.  The signal line is a
    # further EMA of that difference, and the histogram makes their separation explicit.
    fast_ema = close.ewm(span=fast_period, adjust=False).mean()
    slow_ema = close.ewm(span=slow_period, adjust=False).mean()
    macd = fast_ema - slow_ema
    signal = macd.ewm(span=signal_period, adjust=False).mean()
    histogram = macd - signal

    return pd.DataFrame(
        {
            "MACD": macd,
            "MACD_Signal": signal,
            "MACD_Histogram": histogram,
        }
    )


def enrich_with_indicators(price_frame: pd.DataFrame) -> pd.DataFrame:
    """Return a non-mutating copy of an OHLCV frame with indicator columns."""
    if "Close" not in price_frame.columns:
        raise ValueError("The input frame must include a 'Close' column.")

    enriched = price_frame.copy()
    enriched["RSI_14"] = compute_rsi(enriched["Close"])

    macd_frame = compute_macd(enriched["Close"])
    for column in macd_frame.columns:
        enriched[column] = macd_frame[column]

    return enriched


def summarize_latest_indicators(price_frame: pd.DataFrame) -> dict[str, float | str]:
    """Build the shared latest-value contract consumed by the UI and prompt builder.

    The returned mapping contains raw values plus simple rule-based classifications.
    Those classifications describe momentum signals only; they are not predictions or
    automatic trading instructions.
    """
    if price_frame.empty:
        raise ValueError("Cannot summarize an empty frame.")

    # The previous row is needed only for the one-session percentage change.  A
    # single-row frame falls back to the latest row, producing a safe 0% change.
    latest = price_frame.iloc[-1]
    previous = price_frame.iloc[-2] if len(price_frame) > 1 else latest

    macd_value = _scalar_from_row(latest, "MACD", 0.0)
    signal_value = _scalar_from_row(latest, "MACD_Signal", 0.0)
    rsi_value = _scalar_from_row(latest, "RSI_14", 50.0)
    close_value = _scalar_from_row(latest, "Close", 0.0)
    previous_close = _scalar_from_row(previous, "Close", close_value)
    price_change_pct = (
        ((close_value - previous_close) / previous_close * 100)
        if previous_close
        else 0.0
    )

    # Trend is represented by MACD's position relative to its signal, not by whether
    # either number is positive or negative in isolation.
    if macd_value > signal_value:
        trend = "bullish"
    elif macd_value < signal_value:
        trend = "bearish"
    else:
        trend = "neutral"

    # These conventional thresholds are communication aids rather than guarantees that
    # a reversal will occur.
    if rsi_value >= 70:
        momentum = "overbought"
    elif rsi_value <= 30:
        momentum = "oversold"
    else:
        momentum = "balanced"

    return {
        "close": close_value,
        "rsi": rsi_value,
        "macd": macd_value,
        "macd_signal": signal_value,
        "macd_histogram": _scalar_from_row(latest, "MACD_Histogram", 0.0),
        "price_change_pct": price_change_pct,
        "trend": trend,
        "momentum": momentum,
    }
