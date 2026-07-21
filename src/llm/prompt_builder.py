"""Construct the auditable prompt passed to PrivateFin's local language model.

Prompt construction is kept separate from generation so it can be unit tested and
inspected without running Ollama.  The indicator summary is produced by deterministic
code; the model's role is limited to explaining that supplied evidence.
"""

from __future__ import annotations

# A single module-level instruction keeps behavioural constraints consistent between
# runs and prevents UI code from quietly changing the explanation contract.
SYSTEM_PROMPT = (
    "You are a local financial analysis assistant. "
    "Provide a concise, structured response using the headings Observe, Interpret, Infer, and Recommend. "
    "Base every statement on the supplied market data. "
    "Do not mention hidden reasoning or internal chain-of-thought. "
    "Keep the response practical, cautious, and grounded in the indicators provided. "
    "Use plain English that a non-specialist can understand. "
    "Avoid stock-market jargon such as bullish, bearish, overbought, oversold, or MACD unless you explain it in simple words."
)


def _describe_trend(trend: str) -> str:
    """Translate the engine's MACD classification into novice-friendly wording."""
    if trend == "bullish":
        return "recent momentum is leaning upward"
    if trend == "bearish":
        return "recent momentum is leaning downward"
    return "recent momentum looks mixed or steady"


def _describe_momentum(momentum: str) -> str:
    """Translate the engine's RSI bucket without relying on unexplained jargon."""
    if momentum == "overbought":
        return "the price may have risen quickly and could be due for a pause"
    if momentum == "oversold":
        return "the price has been weak and may be stretched to the downside"
    return "the price action looks fairly balanced"


def build_advisory_prompt(
    ticker: str,
    indicator_summary: dict[str, float | str],
    risk_profile: str = "balanced",
    source_tickers: list[str] | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    sample_size: int | None = None,
) -> dict[str, str]:
    """Build system, user, and combined prompts for one advisory request.

    Args:
        ticker: Human-readable company/ticker label displayed by the UI.
        indicator_summary: Latest deterministic values from the indicator engine.
        risk_profile: User-selected context passed to the model; it does not alter the
            underlying calculations.
        source_tickers: Actual market symbols used to create the price series.
        start_date: Inclusive beginning of the requested analysis period.
        end_date: Exclusive end supplied to the data provider.
        sample_size: Number of price observations used.

    Returns:
        Separate ``system`` and ``user`` messages plus a combined inspection string.
    """
    # Explicit "n/a" markers are preferable to silently omitting provenance fields:
    # every prompt retains the same shape and is easier to audit.
    source_tickers_text = ", ".join(source_tickers) if source_tickers else "n/a"
    period_text = (
        f"{start_date} to {end_date}"
        if start_date is not None and end_date is not None
        else "n/a"
    )
    sample_size_text = str(sample_size) if sample_size is not None else "n/a"

    # Raw values and deterministic plain-English classifications are both included.
    # This gives the model precise evidence while reducing its need to infer technical
    # thresholds from memory.
    user_prompt = (
        f"Ticker: {ticker}\n"
        f"Underlying symbols used: {source_tickers_text}\n"
        f"Analysis date range: {period_text}\n"
        f"Data points: {sample_size_text}\n"
        f"Risk profile: {risk_profile}\n"
        f"Latest close: {indicator_summary['close']:.2f}\n"
        f"Price change vs previous session: {indicator_summary['price_change_pct']:.2f}%\n"
        f"RSI(14): {indicator_summary['rsi']:.2f}\n"
        f"MACD: {indicator_summary['macd']:.4f}\n"
        f"MACD signal: {indicator_summary['macd_signal']:.4f}\n"
        f"MACD histogram: {indicator_summary['macd_histogram']:.4f}\n"
        f"Trend in plain English: {_describe_trend(str(indicator_summary['trend']))}\n"
        f"Momentum in plain English: {_describe_momentum(str(indicator_summary['momentum']))}\n\n"
        "Produce a short analysis with the headings Observe, Interpret, Infer, and Recommend. "
        "Make the recommendation proportional to the indicator evidence and include a brief caution where appropriate. "
        "If you use any technical term, immediately explain it in everyday language."
    )

    return {
        "system": SYSTEM_PROMPT,
        "user": user_prompt,
        # This value is not sent as an additional message; it is for inspection/debugging.
        "prompt": f"{SYSTEM_PROMPT}\n\n{user_prompt}",
    }
