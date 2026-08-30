#!/usr/bin/env python3
"""Experiment primitive for the prompt-optimization loop.

Runs the CURRENT champion prompt (``prompts/system_prompt.txt``) over the frozen
eval set, scores each PR, appends one trial to the research log, and prints the
aggregate metrics plus every unsupported claim per PR — the signal the researcher
uses to revise the prompt. This command TESTS a prompt; it never edits one.

    python evaluate.py --note "why I changed the prompt"   # run + log a trial
    python evaluate.py --status                            # show progress, no run

Requires GITHUB_TOKEN in the environment and a running Ollama with the model.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from pr_summarizer.evaluate import evaluate_prompt
from pr_summarizer.researchlog import ResearchLog, Trial, config_fingerprint

ROOT = Path(__file__).resolve().parent
DEFAULT_EVAL = ROOT / "research" / "eval_set.json"
DEFAULT_LOG = ROOT / "research" / "log.jsonl"


def load_eval_set(path: str) -> list[dict]:
    return json.loads(Path(path).read_text(encoding="utf-8"))["prs"]


def _print_status(log: ResearchLog) -> None:
    records = log.read()
    if not records:
        print("No trials yet. Run: python evaluate.py --note '<hypothesis>'")
        return
    best = log.best()
    print(
        f"Trials: {len(records)}   "
        f"Best composite: {best['metrics']['composite']:.3f} "
        f"(trial {best['trial']}, prompt {best['prompt_id']})"
    )
    print("\nRecent trials:")
    for r in records[-6:]:
        m = r["metrics"]
        print(
            f"  #{r['trial']:>3}  comp={m['composite']:.3f}  faith={m['faithfulness']:.3f}  "
            f"bsim={m.get('body_similarity', 0):.3f}  brev={m['brevity']:.3f}   {r.get('note', '')}"
        )


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--note", default="", help="the hypothesis behind the current prompt (logged with the trial)")
    ap.add_argument("--eval-set", default=str(DEFAULT_EVAL))
    ap.add_argument("--log", default=str(DEFAULT_LOG))
    ap.add_argument("--status", action="store_true", help="print progress and exit (no run)")
    args = ap.parse_args()

    log = ResearchLog(args.log)
    if args.status:
        _print_status(log)
        return

    # Imported lazily so --status works without the model/GitHub deps installed.
    import main as agent

    eval_set = load_eval_set(args.eval_set)
    prompt = agent.load_prompt()
    result = evaluate_prompt(prompt, eval_set, run_fn=agent.summarize_pr)

    fingerprint = config_fingerprint(
        {**agent.frozen_config(), "eval_set": [(p["repo"], p["pr_number"]) for p in eval_set]}
    )
    trial = Trial(
        trial=log.next_trial_number(),
        prompt=prompt,
        metrics=result["metrics"],
        per_pr=result["per_pr"],
        config_fp=fingerprint,
        note=args.note,
    )
    log.append(trial)

    agg = result["metrics"]
    print(
        f"trial {trial.trial}  composite={agg['composite']}  faithfulness={agg['faithfulness']}  "
        f"body_similarity={agg['body_similarity']}  brevity={agg['brevity']}  "
        f"(coverage={agg['coverage']}, n={agg['n']}, config {fingerprint})"
    )
    for p in result["per_pr"]:
        print(
            f"\nPR {p['repo']}#{p['pr_number']}: "
            f"composite={p['composite']} faith={p['faithfulness']} bsim={p['body_similarity']} "
            f"(cov={p['coverage']}, {p['files_referenced']}/{p['changed_files']} files, {p['word_count']} words)"
        )
        if p["unsupported"]:
            print("  unsupported claims (fix these in the prompt):")
            for claim in p["unsupported"]:
                print(f"    - {claim}")
    best = log.best()
    print(
        f"\nbest so far: composite={best['metrics']['composite']:.3f} "
        f"(trial {best['trial']}). Run `python visualize.py --open` to see the graph."
    )


if __name__ == "__main__":
    main()
