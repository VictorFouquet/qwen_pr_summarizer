# PR summarizer (local Qwen) + prompt-optimization harness

A grounded PR summarizer built on a **local Qwen** model (via Ollama), with a
**reference-free faithfulness guard** and a harness for optimizing **one thing — the
system prompt** — while everything else stays frozen, so progress is measurable.

## Why

A small local model asked to "summarize PR #N" will happily invent files, endpoints,
and fields it never saw. This project makes the summary **grounded in tool output** and
**scores how grounded it is**, then lets a researcher (a Claude Code session) tune the
prompt against that score and watch it improve.

## The pieces

| File | Role | Frozen? |
|---|---|---|
| `main.py` | Exportable agent: `summarize_pr(repo, pr)` → summary + metrics | ✅ frozen |
| `prompts/system_prompt.txt` | The system prompt | ⬅ **the only variable** |
| `pr_summarizer/verifier.py` | Reference-free faithfulness check (the gate) | ✅ |
| `pr_summarizer/metrics.py` | `composite = faithfulness × coverage × (0.7 + 0.3·brevity)` | ✅ |
| `pr_summarizer/evaluate.py` + `evaluate.py` | Score a prompt over the eval set, log a trial | ✅ |
| `pr_summarizer/dashboard.py` + `visualize.py` | Offline HTML progress graph | ✅ |
| `research/eval_set.json` | The PRs scored against | ✅ frozen |
| `research/log.jsonl` | Append-only trial history | — |

The **researcher** is a Claude Code session that follows [`RESEARCH.md`](./RESEARCH.md)
and edits only `prompts/system_prompt.txt`.

## Setup

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt

# Local model
ollama pull qwen3:8b            # or set PR_SUMMARIZER_MODEL to another local model

# GitHub auth — via a git-ignored .env, so you set it once (never hard-coded or committed)
cp .env.example .env           # then edit .env and set GITHUB_TOKEN=...
```

`main.py` loads `.env` automatically (an exported `GITHUB_TOKEN` still takes precedence).
`.env` is git-ignored; only `.env.example` is tracked.

## Use

Summarize one PR:

```bash
python main.py VictorFouquet/supportops 11
python main.py VictorFouquet/supportops 11 --json
```

Run one optimization trial (tests the current prompt, logs it, shows the signal):

```bash
python evaluate.py --note "seed prompt"
python evaluate.py --status
python visualize.py --open
```

Drive the optimization with a Claude Code session:

```
/research            # follows RESEARCH.md: one hypothesis → edit prompt → evaluate → log
```

## Metric

- **faithfulness** — grounded claims ÷ checkable claims in the summary (paths, endpoints,
  identifiers). Multiplicative gate.
- **coverage** — changed files the summary references ÷ changed files. Multiplicative gate.
- **brevity** — soft modifier, best within ~200 words.

Faithfulness and coverage are gates: you can't win by saying nothing (coverage 0) or by
inventing detail (faithfulness down). Only a faithful, complete, concise summary scores high.

## Token safety

The GitHub token is read from `$GITHUB_TOKEN` (or a git-ignored `.env`) at runtime by
`main.py` only. It is never stored in source, printed, logged, or committed. Do not
hard-code it. Only `.env.example` (a placeholder) is tracked.

## Tests

```bash
python -m pytest -q      # offline: verifier, metrics, log, evaluator, dashboard
```
