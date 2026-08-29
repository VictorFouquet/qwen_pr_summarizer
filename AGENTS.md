# Agent instructions

This repo is a **prompt-optimization harness** for a local-Qwen PR summarizer.

If you are acting as the **prompt researcher**, read and follow [`RESEARCH.md`](./RESEARCH.md)
exactly. The prime directive: **edit only `prompts/system_prompt.txt`**; everything else is
frozen, and changing it invalidates the experiment.

**Never read, print, or hard-code `GITHUB_TOKEN`.** It is supplied via the environment and
consumed only by `main.py` at runtime.

## Map

- `main.py` — the exportable summarizer agent (`summarize_pr`); FROZEN.
- `prompts/system_prompt.txt` — the ONLY optimization variable.
- `pr_summarizer/verifier.py` — reference-free faithfulness check (the gate); FROZEN.
- `pr_summarizer/metrics.py` — scoring; FROZEN.
- `pr_summarizer/evaluate.py` / `evaluate.py` — run a prompt over the eval set, log a trial.
- `pr_summarizer/dashboard.py` / `visualize.py` — offline HTML progress graph.
- `research/eval_set.json` — FROZEN set of PRs to score against.
- `research/log.jsonl` — append-only trial history (the track record).

## Commands

```bash
python evaluate.py --status                 # progress, no run
python evaluate.py --note "<hypothesis>"    # score current prompt, log a trial
python visualize.py --open                  # regenerate + open the graph
python -m pytest -q                         # offline unit tests
```
