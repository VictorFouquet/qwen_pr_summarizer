# Researcher protocol — prompt optimization

You are a **prompt researcher**. Your goal is to raise the **composite** score of the
PR-summarizer on the frozen eval set by improving the system prompt — and nothing else.

The summarizer is a local Qwen model that reads a PR through tools and writes a summary.
It hallucinates (invents files, endpoints, fields). Your job is to find the prompt that
makes it stay grounded and cover the real changes, concisely.

## The one rule that must never break

**Edit ONLY `prompts/system_prompt.txt`.** That file is the single independent variable.

Do **not** touch `main.py`, `pr_summarizer/**`, `research/eval_set.json`, the model, or
the temperature. Everything except the prompt is frozen so a score change is caused by
the prompt alone. Each trial records a `config_fp`; if it changes, you altered something
frozen and the trials are no longer comparable — stop and undo it.

## Never touch the token

The summarizer reads `GITHUB_TOKEN` from the environment. Ensure it is exported before
running. **Never print it, log it, echo it, or write it into any file.** No `echo
$GITHUB_TOKEN`, no hard-coding.

## The metric

`composite = faithfulness × coverage × (0.7 + 0.3·brevity)`, averaged over the eval-set PRs.

- **faithfulness** — fraction of the summary's checkable claims (paths, endpoints,
  identifiers) actually present in the tool output. Hallucination drives this down. Gate.
- **coverage** — fraction of the PR's changed files the summary references. An empty or
  vague summary drives this to 0. Gate.
- **brevity** — soft modifier; within ~200 words is best, decaying to a 500-word cap.

Faithfulness and coverage are multiplicative gates: you cannot win by being only faithful
(say nothing) or only thorough (invent detail). You need both, stated briefly.

## The loop

1. `python evaluate.py --status` — see the current best and recent trials.
2. Read the **last trial's per-PR `unsupported` claims** in `research/log.jsonl`. These
   are the exact hallucinations to eliminate. Low `coverage` means the summary omitted
   real changed files; low `brevity` means it ran long.
3. Form **one** hypothesis about the prompt (e.g. "it invents file paths → tell it to
   name only paths that appear verbatim in tool output"). Make a **small, targeted** edit
   to `prompts/system_prompt.txt`.
4. `python evaluate.py --note "<your hypothesis>"` — this scores the new prompt over the
   eval set and appends a trial (your note is the record of what you tried and why).
5. Compare the new composite to the best. If worse, revert the change (git) or try a
   different edit. If better, keep it — the file is now the champion.
6. `python visualize.py` — regenerate `research/progress.html` for the human to watch.

Repeat. One variable, one hypothesis, one trial at a time — that is what makes the graph
readable.

## Stopping

Stop when composite plateaus (no improvement over ~5 trials) or hits your target. Then:
- leave the best prompt in `prompts/system_prompt.txt`,
- report the best composite, the trial number, and what changed between the seed prompt
  and the champion.

## Discipline

- Change one thing per trial. Batches make the graph uninterpretable.
- Write honest notes — future-you (and the human) read them to see the reasoning.
- Determinism is on (`temperature=0`): if a score moves without a prompt change,
  something in the frozen config drifted. Investigate before continuing.
