"""Tests for building the structured advisory prompt text."""

from src.llm.prompt_builder import (
    SYSTEM_PROMPT,
    _describe_momentum,
    _describe_trend,
    build_advisory_prompt,
)


def test_describe_trend_variants():
    assert _describe_trend("bullish") == "recent momentum is leaning upward"
    assert _describe_trend("bearish") == "recent momentum is leaning downward"
    assert _describe_trend("neutral") == "recent momentum looks mixed or steady"


def test_describe_momentum_variants():
    assert _describe_momentum("overbought") == (
        "the price may have risen quickly and could be due for a pause"
    )
    assert _describe_momentum("oversold") == (
        "the price has been weak and may be stretched to the downside"
    )
    assert _describe_momentum("balanced") == "the price action looks fairly balanced"


def test_build_advisory_prompt_contains_expected_fields_and_text():
    summary = {
        "close": 152.34,
        "price_change_pct": 1.23,
        "rsi": 58.9,
        "macd": 0.4567,
        "macd_signal": 0.321,
        "macd_histogram": 0.1357,
        "trend": "bullish",
        "momentum": "balanced",
    }

    prompt = build_advisory_prompt(
        ticker="Apple (AAPL)",
        indicator_summary=summary,
        risk_profile="medium",
        source_tickers=["AAPL"],
        start_date="2024-01-01",
        end_date="2024-02-01",
        sample_size=22,
    )

    assert prompt["system"] == SYSTEM_PROMPT
    assert "Ticker: Apple (AAPL)" in prompt["user"]
    assert "Risk profile: medium" in prompt["user"]
    assert "Trend in plain English: recent momentum is leaning upward" in prompt["user"]
    assert (
        "Momentum in plain English: the price action looks fairly balanced"
        in prompt["user"]
    )
    assert "Observe, Interpret, Infer, and Recommend" in prompt["prompt"]
