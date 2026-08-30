"""Evaluate one prompt over a fixed set of PRs → one aggregate trial score.

The eval set is frozen alongside the rest of the config; only the prompt varies.
``run_fn`` is injected (defaults to the real agent) so the aggregation logic is
testable without a model or network.
"""

from __future__ import annotations

from statistics import mean
from typing import Callable

_AGG_KEYS = ["faithfulness", "body_similarity", "coverage", "brevity", "composite"]


def evaluate_prompt(prompt: str, eval_set: list[dict], run_fn: Callable) -> dict:
    """Run ``run_fn(repo, pr_number, prompt=...)`` for each PR and aggregate metrics.

    Returns ``{"metrics": <aggregate>, "per_pr": [<per-pr metrics>...]}``.
    """
    per_pr: list[dict] = []
    for item in eval_set:
        repo, number = item["repo"], item["pr_number"]
        result = run_fn(repo, number, prompt=prompt, reference_body=item.get("reference_body", ""))
        row = result.metrics.as_dict()
        row["repo"] = repo
        row["pr_number"] = number
        # The gradient the researcher reasons from: exactly which claims were not
        # grounded in tool output, plus the summary text that produced them.
        row["unsupported"] = [str(c) for c in result.verification.unsupported]
        row["summary"] = result.summary
        # How the agent spent its budget (which files it opened / skipped) — surfaced so the
        # researcher can tune the reading policy through the prompt.
        row["tool_calls"] = getattr(result, "tool_calls", [])
        row["steps"] = getattr(result, "steps", None)
        per_pr.append(row)

    if per_pr:
        aggregate = {k: round(mean(p[k] for p in per_pr), 4) for k in _AGG_KEYS}
    else:
        aggregate = {k: 0.0 for k in _AGG_KEYS}
    aggregate["n"] = len(per_pr)
    return {"metrics": aggregate, "per_pr": per_pr}
