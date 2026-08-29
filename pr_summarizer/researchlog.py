"""Append-only JSONL log of optimization trials.

Every trial the researcher runs is one line: the prompt it tried, the metrics it
scored, and the frozen-config fingerprint it ran under. Append-only so the history
is the record; the visualizer reads it back. One trial per line keeps it greppable
and crash-safe (a partial run loses at most the last line).
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path


def prompt_id(prompt: str) -> str:
    """Short stable id for a prompt variant, so repeats are visible in the log."""
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:12]


def config_fingerprint(config: dict) -> str:
    """Hash of the FROZEN settings. If this changes, trials are not comparable."""
    blob = json.dumps(config, sort_keys=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()[:12]


@dataclass
class Trial:
    trial: int
    prompt: str
    metrics: dict  # aggregate metrics across the eval set
    per_pr: list[dict] = field(default_factory=list)
    config_fp: str = ""
    note: str = ""
    ts: float = field(default_factory=time.time)

    def to_record(self) -> dict:
        rec = {
            "trial": self.trial,
            "ts": self.ts,
            "prompt_id": prompt_id(self.prompt),
            "prompt": self.prompt,
            "config_fp": self.config_fp,
            "note": self.note,
            "metrics": self.metrics,
            "per_pr": self.per_pr,
        }
        return rec


class ResearchLog:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, trial: Trial) -> None:
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(trial.to_record()) + "\n")

    def read(self) -> list[dict]:
        if not self.path.exists():
            return []
        records = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                records.append(json.loads(line))
        return records

    def best(self, metric: str = "composite") -> dict | None:
        records = self.read()
        if not records:
            return None
        return max(records, key=lambda r: r["metrics"].get(metric, float("-inf")))

    def next_trial_number(self) -> int:
        records = self.read()
        return (max((r["trial"] for r in records), default=0)) + 1
