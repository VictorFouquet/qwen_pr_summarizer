"""Offline test for the evaluator aggregation — no model, no network.

Uses a fake ``run_fn`` shaped like ``main.summarize_pr`` (returns an object with
``.metrics``, ``.verification``, ``.summary``).
"""

from types import SimpleNamespace

from pr_summarizer.evaluate import evaluate_prompt
from pr_summarizer.metrics import Metrics
from pr_summarizer.verifier import Claim, ClaimKind


def _fake_result(composite, unsupported=()):
    metrics = Metrics(
        faithfulness=composite,
        coverage=1.0,
        brevity=1.0,
        composite=composite,
        word_count=50,
        changed_files=2,
        files_referenced=2,
        unsupported_claims=len(unsupported),
    )
    verification = SimpleNamespace(
        unsupported=[Claim(t, ClaimKind.PATH) for t in unsupported]
    )
    return SimpleNamespace(metrics=metrics, verification=verification, summary="a summary")


def test_evaluate_aggregates_and_surfaces_unsupported():
    eval_set = [
        {"repo": "o/r", "pr_number": 1},
        {"repo": "o/r", "pr_number": 2},
    ]
    scores = iter([_fake_result(0.6, unsupported=["pages/x.tsx"]), _fake_result(0.8)])

    def fake_run(repo, number, prompt=None):
        return next(scores)

    out = evaluate_prompt("some prompt", eval_set, run_fn=fake_run)

    assert out["metrics"]["composite"] == 0.7  # mean(0.6, 0.8)
    assert out["metrics"]["n"] == 2
    assert out["per_pr"][0]["unsupported"] == ["[path] pages/x.tsx"]
    assert out["per_pr"][0]["summary"] == "a summary"
    assert out["per_pr"][1]["pr_number"] == 2


def test_evaluate_empty_set_is_zero():
    out = evaluate_prompt("p", [], run_fn=lambda *a, **k: None)
    assert out["metrics"]["composite"] == 0.0
    assert out["metrics"]["n"] == 0
