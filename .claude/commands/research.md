Act as the prompt researcher for this repo. Read `RESEARCH.md` and follow it exactly.

Run one full research iteration (unless I gave a number of iterations in the arguments below):

1. `python evaluate.py --status` and read the most recent trial's per-PR `unsupported`
   claims in `research/log.jsonl`.
2. Form ONE hypothesis about why the current `prompts/system_prompt.txt` loses composite.
3. Make a small, targeted edit to `prompts/system_prompt.txt` ONLY.
4. `python evaluate.py --note "<your hypothesis>"`.
5. Report whether composite improved vs. the best, and regenerate the graph with
   `python visualize.py`.

Hard rules: edit only `prompts/system_prompt.txt`; never read/print/hard-code
`GITHUB_TOKEN`; change one thing per trial.

Iterations / focus (optional): $ARGUMENTS
