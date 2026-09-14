"""Recalculate automatic checks and summarise the completed author-scored rubric."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from documentation.evaluation.evaluate_oiir import automatic_checks


RESULTS = Path("documentation/evaluation/results")
RESPONSES = RESULTS / "oiir-responses.json"
RUBRIC = RESULTS / "oiir-manual-rubric.csv"
OUTPUT = RESULTS / "oiir-evaluation-summary.json"


def main() -> None:
    records = json.loads(RESPONSES.read_text(encoding="utf-8"))
    for record in records:
        record["automatic_checks"] = automatic_checks(
            record["response"], record["indicator_summary"]
        )
    RESPONSES.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")

    checks = [record["automatic_checks"] for record in records]
    pass_counts = {
        key: sum(int(check[key]) for check in checks)
        for key in checks[0]
    }

    rubric = pd.read_csv(RUBRIC)
    dimensions = [
        "factual_accuracy_0_to_2",
        "logical_coherence_0_to_2",
        "completeness_0_to_2",
        "transparency_0_to_2",
    ]
    calculated_total = rubric[dimensions].sum(axis=1)
    if not calculated_total.equals(rubric["total_0_to_8"]):
        raise ValueError("One or more rubric totals do not match their dimensions.")

    summary = {
        "samples": int(len(records)),
        "model": "llama3:latest, 8.0B, Q4_0 via local Ollama",
        "model_digest": "365c0bd3c000a25d28ddbf732fe1c6add414de7275464c4e4d1c3b5fcb5d8ad1",
        "fixed_period": "2025-07-20 to 2026-07-20",
        "conditions": "10 ticker groups, low and high risk profile for each",
        "automatic_passes": pass_counts,
        "manual_rubric": {
            "scoring": "Single author scorer; no inter-rater reliability claim.",
            "mean_total_out_of_8": float(rubric["total_0_to_8"].mean()),
            "median_total_out_of_8": float(rubric["total_0_to_8"].median()),
            "minimum_total_out_of_8": int(rubric["total_0_to_8"].min()),
            "maximum_total_out_of_8": int(rubric["total_0_to_8"].max()),
            "samples_at_or_above_6": int((rubric["total_0_to_8"] >= 6).sum()),
            "dimension_means_out_of_2": {
                dimension: float(rubric[dimension].mean())
                for dimension in dimensions
            },
            "predeclared_mean_threshold_6_met": bool(
                rubric["total_0_to_8"].mean() >= 6
            ),
        },
        "interpretation_notes": [
            "Heading and value-string checks measure observable format/faithfulness only.",
            "A missing exact MACD string is not automatically a factual failure if the relation is described correctly.",
            "The momentum check ignores locally negated threshold terms such as 'not overbought'.",
            "Manual author scoring found important MACD sign/order errors and unsupported price or portfolio targets.",
        ],
    }
    OUTPUT.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (RESULTS / "oiir-automatic-summary.json").write_text(
        json.dumps(
            {
                "samples": len(records),
                "model": summary["model"],
                "fixed_period": summary["fixed_period"],
                "passes_by_check": pass_counts,
                "warning": (
                    "Rule checks supplement but do not replace manual scoring. "
                    "Review every response in context."
                ),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
