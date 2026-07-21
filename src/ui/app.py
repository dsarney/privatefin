"""Streamlit presentation and orchestration for the PrivateFin analysis pipeline.

The UI intentionally contains no indicator mathematics or prompt policy.  It validates
inputs, calls each application layer in sequence, and renders either the local-model
response or a clearly labelled fallback.
"""

from __future__ import annotations

from datetime import date, timedelta

import streamlit as st

from src.engine.data_loader import download_stock_data
from src.engine.indicator_engine import (
    enrich_with_indicators,
    summarize_latest_indicators,
)
from src.llm.ollama_client import OllamaClient
from src.llm.prompt_builder import build_advisory_prompt

st.set_page_config(page_title="PrivateFin", page_icon="📈", layout="wide")


# Keeping the allow-list in application code gives users readable company names while
# ensuring every choice maps to known Yahoo Finance symbols.  A list (rather than a
# mapping) preserves the deliberate display order.  Alphabet demonstrates the supported
# multi-symbol company blend.
COMPANY_OPTIONS = [
    {"label": "3M", "tickers": ["MMM"]},
    {"label": "Abbott Laboratories", "tickers": ["ABT"]},
    {"label": "AbbVie", "tickers": ["ABBV"]},
    {"label": "Accenture", "tickers": ["ACN"]},
    {"label": "Adobe", "tickers": ["ADBE"]},
    {"label": "Advanced Micro Devices", "tickers": ["AMD"]},
    {"label": "Aflac", "tickers": ["AFL"]},
    {"label": "Air Products", "tickers": ["APD"]},
    {"label": "Alphabet (Google)", "tickers": ["GOOG", "GOOGL"]},
    {"label": "Amazon", "tickers": ["AMZN"]},
    {"label": "American Express", "tickers": ["AXP"]},
    {"label": "American Tower", "tickers": ["AMT"]},
    {"label": "Amgen", "tickers": ["AMGN"]},
    {"label": "Analog Devices", "tickers": ["ADI"]},
    {"label": "Apple", "tickers": ["AAPL"]},
    {"label": "Applied Materials", "tickers": ["AMAT"]},
    {"label": "Archer-Daniels-Midland", "tickers": ["ADM"]},
    {"label": "AT&T", "tickers": ["T"]},
    {"label": "Bank of America", "tickers": ["BAC"]},
    {"label": "Best Buy", "tickers": ["BBY"]},
    {"label": "Boeing", "tickers": ["BA"]},
    {"label": "Booking Holdings", "tickers": ["BKNG"]},
    {"label": "Bristol Myers Squibb", "tickers": ["BMY"]},
    {"label": "Broadcom", "tickers": ["AVGO"]},
    {"label": "Caterpillar", "tickers": ["CAT"]},
    {"label": "Charles Schwab", "tickers": ["SCHW"]},
    {"label": "Chevron", "tickers": ["CVX"]},
    {"label": "Chubb", "tickers": ["CB"]},
    {"label": "Cisco", "tickers": ["CSCO"]},
    {"label": "Citigroup", "tickers": ["C"]},
    {"label": "Coca-Cola", "tickers": ["KO"]},
    {"label": "Comcast", "tickers": ["CMCSA"]},
    {"label": "ConocoPhillips", "tickers": ["COP"]},
    {"label": "Costco", "tickers": ["COST"]},
    {"label": "CVS Health", "tickers": ["CVS"]},
    {"label": "Danaher", "tickers": ["DHR"]},
    {"label": "Deere & Company", "tickers": ["DE"]},
    {"label": "Delta Air Lines", "tickers": ["DAL"]},
    {"label": "Duke Energy", "tickers": ["DUK"]},
    {"label": "Eaton", "tickers": ["ETN"]},
    {"label": "Eli Lilly", "tickers": ["LLY"]},
    {"label": "Emerson Electric", "tickers": ["EMR"]},
    {"label": "Exelon", "tickers": ["EXC"]},
    {"label": "Exxon Mobil", "tickers": ["XOM"]},
    {"label": "Ford", "tickers": ["F"]},
    {"label": "General Dynamics", "tickers": ["GD"]},
    {"label": "General Electric", "tickers": ["GE"]},
    {"label": "General Motors", "tickers": ["GM"]},
    {"label": "Gilead Sciences", "tickers": ["GILD"]},
    {"label": "Goldman Sachs", "tickers": ["GS"]},
    {"label": "Halliburton", "tickers": ["HAL"]},
    {"label": "Home Depot", "tickers": ["HD"]},
    {"label": "Honeywell", "tickers": ["HON"]},
    {"label": "IBM", "tickers": ["IBM"]},
    {"label": "Intel", "tickers": ["INTC"]},
    {"label": "Intuit", "tickers": ["INTU"]},
    {"label": "Johnson & Johnson", "tickers": ["JNJ"]},
    {"label": "JPMorgan Chase", "tickers": ["JPM"]},
    {"label": "Kraft Heinz", "tickers": ["KHC"]},
    {"label": "Lockheed Martin", "tickers": ["LMT"]},
    {"label": "Lowe's", "tickers": ["LOW"]},
    {"label": "Marathon Petroleum", "tickers": ["MPC"]},
    {"label": "Mastercard", "tickers": ["MA"]},
    {"label": "McDonald's", "tickers": ["MCD"]},
    {"label": "Medtronic", "tickers": ["MDT"]},
    {"label": "Merck", "tickers": ["MRK"]},
    {"label": "Meta Platforms", "tickers": ["META"]},
    {"label": "Micron Technology", "tickers": ["MU"]},
    {"label": "Microsoft", "tickers": ["MSFT"]},
    {"label": "Mondelez", "tickers": ["MDLZ"]},
    {"label": "Morgan Stanley", "tickers": ["MS"]},
    {"label": "Netflix", "tickers": ["NFLX"]},
    {"label": "Nike", "tickers": ["NKE"]},
    {"label": "NVIDIA", "tickers": ["NVDA"]},
    {"label": "Oracle", "tickers": ["ORCL"]},
    {"label": "PepsiCo", "tickers": ["PEP"]},
    {"label": "Pfizer", "tickers": ["PFE"]},
    {"label": "Philip Morris International", "tickers": ["PM"]},
    {"label": "Procter & Gamble", "tickers": ["PG"]},
    {"label": "Qualcomm", "tickers": ["QCOM"]},
    {"label": "RTX", "tickers": ["RTX"]},
    {"label": "Salesforce", "tickers": ["CRM"]},
    {"label": "ServiceNow", "tickers": ["NOW"]},
    {"label": "Starbucks", "tickers": ["SBUX"]},
    {"label": "Stryker", "tickers": ["SYK"]},
    {"label": "T-Mobile", "tickers": ["TMUS"]},
    {"label": "Target", "tickers": ["TGT"]},
    {"label": "Tesla", "tickers": ["TSLA"]},
    {"label": "Texas Instruments", "tickers": ["TXN"]},
    {"label": "The Cigna Group", "tickers": ["CI"]},
    {"label": "Thermo Fisher Scientific", "tickers": ["TMO"]},
    {"label": "Travelers", "tickers": ["TRV"]},
    {"label": "Truist Financial", "tickers": ["TFC"]},
    {"label": "Uber", "tickers": ["UBER"]},
    {"label": "Union Pacific", "tickers": ["UNP"]},
    {"label": "United Airlines", "tickers": ["UAL"]},
    {"label": "United Parcel Service", "tickers": ["UPS"]},
    {"label": "UnitedHealth Group", "tickers": ["UNH"]},
    {"label": "Valero", "tickers": ["VLO"]},
    {"label": "Verizon", "tickers": ["VZ"]},
    {"label": "Vertex Pharmaceuticals", "tickers": ["VRTX"]},
    {"label": "Visa", "tickers": ["V"]},
    {"label": "Walmart", "tickers": ["WMT"]},
    {"label": "Walt Disney", "tickers": ["DIS"]},
    {"label": "Wells Fargo", "tickers": ["WFC"]},
    {"label": "Workday", "tickers": ["WDAY"]},
    {"label": "Zoetis", "tickers": ["ZTS"]},
]

RISK_PROFILE_OPTIONS = [
    {"label": "Low", "value": "low"},
    {"label": "Medium", "value": "medium"},
    {"label": "High", "value": "high"},
]

# This warning is shown before every analysis.  The generated text is educational
# indicator commentary and must not be presented as regulated or personalised advice.
OUTPUT_DISCLAIMER = (
    "Disclaimer: This analysis is generated by AI for educational and informational "
    "purposes only. It does not constitute professional financial advice, investment "
    "recommendations, or an endorsement of any security."
)


def _company_display(option: dict[str, list[str] | str]) -> str:
    """Format a company option with all source tickers visible to the user."""
    tickers = option["tickers"]
    if isinstance(tickers, str):
        tickers = [tickers]
    return f"{option['label']} ({' + '.join(tickers)})"


def _risk_profile_display(option: dict[str, str]) -> str:
    """Show the readable label while retaining a prompt-friendly internal value."""
    return option["label"]


def render_metrics(summary: dict[str, float | str]) -> None:
    """Render the key deterministic values above the generated explanation."""
    # A fixed four-column layout makes the evidence easy to compare with the OIIR text.
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Latest Close", f"{summary['close']:.2f}")
    col2.metric("RSI(14)", f"{summary['rsi']:.2f}")
    col3.metric("MACD", f"{summary['macd']:.4f}")
    col4.metric("Price Change", f"{summary['price_change_pct']:.2f}%")


def render_output_disclaimer() -> None:
    """Render the persistent educational-use notice in a visually distinct panel."""
    # The content is a constant controlled by this application, so rendering the small
    # HTML wrapper is safe; no user or model text is interpolated into it.
    st.markdown(
        f"""
        <div style="
            margin: 0.35rem 0 0.9rem 0;
            padding: 0.6rem 0.85rem;
            border-radius: 0.5rem;
            background: rgba(59, 130, 246, 0.12);
            border: 1px solid rgba(59, 130, 246, 0.25);
            color: inherit;
            font-size: 0.9rem;
            line-height: 1.45;
        ">
            <strong>Disclaimer:</strong> {OUTPUT_DISCLAIMER.removeprefix('Disclaimer: ')}
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    """Run one reactive Streamlit page and orchestrate analysis on button clicks."""
    st.title("PrivateFin")
    st.caption(
        "Local, explainable financial analysis with market data, indicators, and Ollama."
    )
    render_output_disclaimer()

    with st.sidebar:
        # Streamlit reruns this function whenever a widget changes.  The button below
        # acts as an explicit gate so network and model calls occur only on request.
        st.header("Analysis Inputs")
        selected_company = st.selectbox(
            "Company",
            COMPANY_OPTIONS,
            format_func=_company_display,
        )
        start_date = st.date_input(
            "Start date", value=date.today() - timedelta(days=365)
        )
        end_date = st.date_input("End date", value=date.today())
        selected_risk_profile = st.selectbox(
            "Risk profile",
            RISK_PROFILE_OPTIONS,
            index=1,
            format_func=_risk_profile_display,
        )
        generate_button = st.button("Generate analysis", use_container_width=True)

    if not generate_button:
        return

    # Reject invalid periods before making a Yahoo Finance request.
    if start_date >= end_date:
        st.error("Start date must be earlier than end date.")
        return

    tickers = selected_company["tickers"]
    if isinstance(tickers, str):
        tickers = [tickers]
    company_name = _company_display(selected_company)

    # Stage 1: retrieve and normalise the market data.  Data-provider failures remain
    # recoverable and are presented as UI feedback rather than an application crash.
    with st.spinner("Downloading market data..."):
        # Normalize dates to ISO so the data layer receives a stable string format.
        data_frame = download_stock_data(
            tickers, start_date.isoformat(), end_date.isoformat()
        )

    if data_frame is None or data_frame.empty:
        st.error("No market data was returned for that ticker and date range.")
        return

    # Stage 2: compute the quantitative source of truth once.  The same summary is used
    # for both visible metric cards and the LLM prompt.
    enriched_frame = enrich_with_indicators(data_frame)
    summary = summarize_latest_indicators(enriched_frame)
    render_metrics(summary)

    st.subheader("Price History")
    st.line_chart(enriched_frame[["Close"]])

    # Stage 3: preserve provenance and context in a stable, inspectable prompt.
    prompt = build_advisory_prompt(
        ticker=company_name,
        indicator_summary=summary,
        risk_profile=selected_risk_profile["value"],
        source_tickers=tickers,
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat(),
        sample_size=len(enriched_frame),
    )

    # Stage 4: generate through the loopback Ollama service.  A missing local model does
    # not hide the deterministic results already produced above.
    client = OllamaClient(model="llama3")
    if client.is_available():
        with st.spinner("Generating local analysis with Ollama..."):
            response_text = client.generate(
                prompt["user"], system_prompt=prompt["system"]
            )
        st.subheader("Model Response")
        st.write(response_text)
    else:
        st.warning(
            "Ollama is not available on this machine. The prompt is ready, but the local model could not be reached."
        )
        st.subheader("Suggested Analysis Template")
        st.write(
            "Observe: the latest price, recent change, and momentum signals are loaded.\n\n"
            "Interpret: explain what the numbers suggest in simple everyday language.\n\n"
            "Infer: say whether the stock seems to be moving up, down, or staying fairly steady.\n\n"
            "Recommend: give a cautious, evidence-based action with a short risk note."
        )


if __name__ == "__main__":
    main()
