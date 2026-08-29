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

## Know the ground truth first

Before you optimize anything, **read the eval-set PRs yourself so you know what a correct
summary should say** — start with `VictorFouquet/supportops` PR #11, then #8 and #10:

```bash
gh pr view VictorFouquet/supportops 11
gh pr diff VictorFouquet/supportops 11
```

(`gh` handles auth — never print or hard-code the token.)

Why this matters: the metrics are mechanical and reference-free. They catch hallucination
(faithfulness) and omission (coverage), but they **cannot tell whether a grounded,
file-covering summary is actually accurate or useful**. You are the semantic check. Read
the summaries a run produced (`per_pr[].summary` in `research/log.jsonl`) against the real
PR and confirm a rising composite means genuinely better summaries — not a gamed metric.
If composite goes up but the summary got worse, the metric is being gamed; note it and
change tack.

**Do not overfit.** You are tuning a *general* prompt that must work on any PR. Never
encode facts specific to the eval-set PRs into `prompts/system_prompt.txt` — no "this repo
uses the App Router", no hard-coded paths or endpoints. If an edit only helps because it
bakes in #11's specifics, it is cheating the metric, not improving the summarizer.

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
5. Compare the new composite to the best so far.
   - **Improved** → keep the edited prompt; it is the new champion.
   - **Regressed or unchanged** → revert the prompt to the previous champion
     (`git checkout -- prompts/system_prompt.txt`). You still keep the trial: the failed
     idea stays in the log.
6. `python visualize.py` — regenerate `research/progress.html`.
7. **Commit every iteration — successes and failures alike.** This is the whole point:
   git history plus the log are the record of every idea, why you tried it, and what
   happened. Two rules:
   - **Always** commit the log and dashboard (the trial, your hypothesis, the result) —
     even when the idea failed.
   - Commit the changed `prompts/system_prompt.txt` **only when the trial improved** (a
     champion advance). On a regression the prompt is already reverted, so the commit
     records the failed idea without moving the champion.

   Improvement (champion advances):
   ```bash
   git add prompts/system_prompt.txt research/log.jsonl research/progress.html
   git commit -m "trial N ✓ <hypothesis> -> composite X.XX (was Y.YY)"
   ```
   Regression (prompt reverted, finding kept):
   ```bash
   git add research/log.jsonl research/progress.html
   git commit -m "trial N ✗ <hypothesis> -> composite X.XX (best Y.YY), reverted"
   ```

   Never squash or drop trials. A failed idea is data — it stops you and the next
   researcher from re-trying a dead end.

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
