Act as the prompt researcher for this repo. Read `RESEARCH.md` and follow it exactly.

Run one full research iteration (unless I gave a number of iterations in the arguments below):

0. If you have not already this session, read the eval-set PRs for ground truth — start
   with `gh pr view VictorFouquet/supportops 11` and `gh pr diff VictorFouquet/supportops 11`
   (then #8, #10) — so you can judge whether a higher composite is a genuinely better
   summary and not a gamed metric. Never print or hard-code the token.
1. `python evaluate.py --status` and read the most recent trial's per-PR `unsupported`
   claims in `research/log.jsonl`.
2. Form ONE hypothesis about why the current `prompts/system_prompt.txt` loses composite.
3. Make a small, targeted edit to `prompts/system_prompt.txt` ONLY.
4. `python evaluate.py --note "<your hypothesis>"`.
5. Report whether composite improved vs. the best, and regenerate the graph with
   `python visualize.py`.
6. Commit this iteration (per RESEARCH.md): ALWAYS commit `research/log.jsonl` +
   `research/progress.html` with the hypothesis and result; ALSO commit
   `prompts/system_prompt.txt` only if it improved (revert it first if it regressed).
   Commit every trial — successes and failures both. A failed idea is data.

Hard rules: edit only `prompts/system_prompt.txt`; never read/print/hard-code
`GITHUB_TOKEN`; change one thing per trial; commit every iteration.

Iterations / focus (optional): $ARGUMENTS
