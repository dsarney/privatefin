"""Observe process network endpoints during ten local Ollama inference requests.

This is an endpoint audit using repeated `lsof` snapshots, not packet-content capture.
It requires no elevated packet-capture permission and deliberately reuses frozen prompts,
so Yahoo Finance retrieval is excluded from the inference phase.
"""

from __future__ import annotations

import json
import os
import subprocess
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

import ollama


RESULTS = Path("documentation/evaluation/results")
RESPONSES = RESULTS / "oiir-responses.json"
OUTPUT = RESULTS / "network-endpoint-audit.json"
QUERY_COUNT = 10


def _ollama_pids() -> set[int]:
    result = subprocess.run(
        ["pgrep", "-x", "ollama"], capture_output=True, text=True, check=False
    )
    return {int(value) for value in result.stdout.split() if value.isdigit()}


def _snapshot(relevant_pids: set[int]) -> list[str]:
    result = subprocess.run(
        ["lsof", "-nP", "-i"],
        capture_output=True,
        text=True,
        check=False,
    )
    lines = []
    for line in result.stdout.splitlines()[1:]:
        columns = line.split()
        if len(columns) > 1 and columns[1].isdigit() and int(columns[1]) in relevant_pids:
            lines.append(line)
    return lines


def main() -> None:
    records = json.loads(RESPONSES.read_text(encoding="utf-8"))[:QUERY_COUNT]
    if len(records) < QUERY_COUNT:
        raise ValueError(f"Expected at least {QUERY_COUNT} frozen prompts.")

    current_pid = os.getpid()
    relevant_pids = {current_pid} | _ollama_pids()
    if len(relevant_pids) == 1:
        raise SystemExit("No Ollama server process was found.")

    stop_event = threading.Event()
    observed_lines: set[str] = set()
    snapshots = 0

    def monitor() -> None:
        nonlocal snapshots
        while not stop_event.is_set():
            observed_lines.update(_snapshot(relevant_pids))
            snapshots += 1
            time.sleep(0.15)

    monitor_thread = threading.Thread(target=monitor, daemon=True)
    client = ollama.Client(host="http://localhost:11434")
    started = datetime.now(timezone.utc)
    monitor_thread.start()
    query_results = []
    try:
        for record in records:
            query_started = time.monotonic()
            response = client.chat(
                model="llama3",
                messages=[
                    {"role": "system", "content": record["prompt"]["system"]},
                    {"role": "user", "content": record["prompt"]["user"]},
                ],
                options={"num_predict": 64},
            )
            content = getattr(getattr(response, "message", None), "content", "")
            query_results.append(
                {
                    "sample_id": record["sample_id"],
                    "elapsed_seconds": round(time.monotonic() - query_started, 3),
                    "response_received": bool(content),
                }
            )
    finally:
        stop_event.set()
        monitor_thread.join(timeout=3)
        observed_lines.update(_snapshot(relevant_pids))

    ended = datetime.now(timezone.utc)
    external_lines = [
        line
        for line in sorted(observed_lines)
        if "127.0.0.1" not in line and "[::1]" not in line and "localhost" not in line
    ]
    summary = {
        "method": "Repeated lsof -nP -i endpoint snapshots",
        "limitation": (
            "This records process sockets/endpoints, not packet payloads. It can miss "
            "very short-lived connections between snapshots and is not a substitute "
            "for a privileged tcpdump/Wireshark content audit."
        ),
        "started_utc": started.isoformat(),
        "ended_utc": ended.isoformat(),
        "python_pid": current_pid,
        "ollama_pids": sorted(relevant_pids - {current_pid}),
        "snapshots": snapshots,
        "queries_attempted": QUERY_COUNT,
        "queries_with_response": sum(
            int(result["response_received"]) for result in query_results
        ),
        "query_results": query_results,
        "all_observed_relevant_process_sockets": sorted(observed_lines),
        "observed_external_sockets": external_lines,
        "endpoint_audit_passed": len(external_lines) == 0,
    }
    OUTPUT.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
