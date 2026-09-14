"""Generate and automatically check the planned 20-output OIIR evaluation set.

Prerequisites: a local Ollama server with the `llama3` model. Run from the repository
root. Responses and a blank manual-rubric sheet are written under
`documentation/evaluation/results/`.
"""

from __future__ import annotations

import csv
import json
import re
from datetime import date, timedelta
from pathlib import Path

from src.engine.data_loader import download_stock_data
from src.engine.indicator_engine import (
    enrich_with_indicators,
    summarize_latest_indicators,
)
from src.llm.ollama_client import OllamaClient
from src.llm.prompt_builder import build_advisory_prompt


OUTPUT_DIR = Path("documentation/evaluation/results")
END_DATE = date(2026, 7, 20)
START_DATE = END_DATE - timedelta(days=365)
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
RISK_PROFILES = ("low", "high")
HEADINGS = ("Observe", "Interpret", "Infer", "Recommend")


def _mentions_value(text: str, label: str, expected: float, decimals: int) -> bool:
    """Check for a labelled value rounded as it appears in the source prompt."""
    expected_text = f"{expected:.{decimals}f}"
    pattern = rf"{re.escape(label)}[^.\n]{{0,80}}{re.escape(expected_text)}"
    return re.search(pattern, text, flags=re.IGNORECASE) is not None


def _has_unnegated_term(text: str, term: str) -> bool:
    """Find a threshold term that is not locally negated or presented as an alternative."""
    lower = text.lower()
    for match in re.finditer(term, lower):
        prefix = lower[max(0, match.start() - 60) : match.start()]
        if any(
            negation in prefix
            for negation in ("not ", "no ", "neither ", "nor ", "without ")
        ):
            continue
        return True
    return False


def automatic_checks(response: str, summary: dict[str, float | str]) -> dict[str, bool]:
    lower = response.lower()
    momentum = str(summary["momentum"])
    contradictory_momentum = (
        momentum == "balanced"
        and (
            _has_unnegated_term(lower, "oversold")
            or _has_unnegated_term(lower, "overbought")
        )
    ) or (
        momentum == "oversold" and _has_unnegated_term(lower, "overbought")
    ) or (
        momentum == "overbought" and _has_unnegated_term(lower, "oversold")
    )
    return {
        "all_oiir_headings_present": all(heading.lower() in lower for heading in HEADINGS),
        "rsi_value_mentioned_exactly": _mentions_value(
            response, "RSI", float(summary["rsi"]), 2
        ),
        "macd_value_mentioned_exactly": _mentions_value(
            response, "MACD", float(summary["macd"]), 4
        ),
        "no_obvious_momentum_contradiction": not contradictory_momentum,
    }


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    client = OllamaClient(model="llama3")
    if not client.is_available():
        raise SystemExit(
            "Ollama is unavailable at localhost:11434. Start it and pull `llama3`, "
            "then rerun this script."
        )

    records = []
    rubric_rows = []
    sample_number = 0
    for label, ticker in TICKERS.items():
        source_tickers = ticker if isinstance(ticker, list) else [ticker]
        frame = download_stock_data(
            ticker, START_DATE.isoformat(), END_DATE.isoformat(), save=False
        )
        if frame is None or frame.empty:
            raise RuntimeError(f"No market data returned for {label}.")
        summary = summarize_latest_indicators(enrich_with_indicators(frame))

        for risk_profile in RISK_PROFILES:
            sample_number += 1
            sample_id = f"O{sample_number:02d}"
            prompt = build_advisory_prompt(
                ticker=label,
                indicator_summary=summary,
                risk_profile=risk_profile,
                source_tickers=source_tickers,
                start_date=START_DATE.isoformat(),
                end_date=END_DATE.isoformat(),
                sample_size=len(frame),
            )
            response = client.generate(prompt["user"], system_prompt=prompt["system"])
            checks = automatic_checks(response, summary)
            records.append(
                {
                    "sample_id": sample_id,
                    "ticker": label,
                    "risk_profile": risk_profile,
                    "indicator_summary": summary,
                    "prompt": prompt,
                    "response": response,
                    "automatic_checks": checks,
                }
            )
            rubric_rows.append(
                {
                    "sample_id": sample_id,
                    "ticker": label,
                    "risk_profile": risk_profile,
                    "factual_accuracy_0_to_2": "",
                    "logical_coherence_0_to_2": "",
                    "completeness_0_to_2": "",
                    "transparency_0_to_2": "",
                    "total_0_to_8": "",
                    "scorer_code": "",
                    "notes": "",
                }
            )

    responses_path = OUTPUT_DIR / "oiir-responses.json"
    responses_path.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    rubric_path = OUTPUT_DIR / "oiir-manual-rubric.csv"
    with rubric_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rubric_rows[0]))
        writer.writeheader()
        writer.writerows(rubric_rows)

    checks = [
        record["automatic_checks"] for record in records
    ]
    check_summary = {
        key: sum(int(check[key]) for check in checks)
        for key in checks[0]
    }
    summary_path = OUTPUT_DIR / "oiir-automatic-summary.json"
    summary_path.write_text(
        json.dumps(
            {
                "samples": len(records),
                "model": "llama3 via local Ollama",
                "fixed_period": f"{START_DATE.isoformat()} to {END_DATE.isoformat()}",
                "passes_by_check": check_summary,
                "warning": (
                    "String/rule checks supplement but do not replace manual rubric "
                    "scoring. Review every flagged response in context."
                ),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {responses_path}, {rubric_path}, and {summary_path}")


if __name__ == "__main__":
    main()
