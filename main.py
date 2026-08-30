"""Exportable PR-summarizer agent (local Qwen via Ollama) with a faithfulness gate.

Everything here is FROZEN for optimization purposes except the system prompt, which
lives in ``prompts/system_prompt.txt`` (the single file the auto-researcher edits).
Import ``summarize_pr`` in a pipeline, or run ``python main.py <repo> <pr>``.

GitHub auth: the token is read from ``$GITHUB_TOKEN`` at runtime and never stored in
source. Do not hard-code it.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

from github import Github
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama

from pr_summarizer.metrics import (
    BREVITY_FLOOR,
    BREVITY_HARD_CAP_WORDS,
    BREVITY_TARGET_WORDS,
    Metrics,
    compute_metrics,
)
from pr_summarizer.embedding import EMBED_MODEL
from pr_summarizer.researchlog import config_fingerprint
from pr_summarizer.verifier import Verification, verify

ROOT = Path(__file__).resolve().parent
PROMPT_FILE = ROOT / "prompts" / "system_prompt.txt"

# Load GITHUB_TOKEN (and optional overrides) from a git-ignored .env so it need not be
# exported every session. Real environment variables still take precedence, and a
# missing python-dotenv or .env is fine — it just falls back to the process environment.
try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except ModuleNotFoundError:
    pass

# ---- FROZEN configuration -------------------------------------------------
# The only thing an optimization run may change is the system prompt. Everything
# below is held constant so a score delta is attributable to the prompt alone.
# temperature=0 removes sampling noise; changing any of this breaks comparability
# and is reflected in the config fingerprint recorded with every trial.
MODEL = os.environ.get("PR_SUMMARIZER_MODEL", "qwen3:8b")
TEMPERATURE = 0.0
MAX_STEPS = 8
# Context window. Ollama's default num_ctx is only 2048 tokens; the eval-PR groundings
# are 24k-38k tokens, so at the default the tool output overflows the window and the
# SYSTEM PROMPT (at the head) is truncated away before generation — making prompt
# optimization inert (verified: identical output across different prompts). Sized to the
# model's maximum so the prompt + a full PR's grounding coexist. Requires adequate memory
# for the KV cache (~5-6GB at this size, on top of the ~6GB model).
NUM_CTX = int(os.environ.get("PR_SUMMARIZER_NUM_CTX", "40960"))
# A PR summary is high-level context, not a line-by-line review, and one giant file (a
# generated lockfile, a big design doc, vendored code) can be half the diff and crowd the
# real changes out of the context window. Cap each file's patch so no single file
# dominates the grounding, and omit lockfile bodies entirely — they carry no summary value.
PATCH_MAX_LINES = int(os.environ.get("PR_SUMMARIZER_PATCH_MAX_LINES", "120"))
LOCKFILES = {"pnpm-lock.yaml", "package-lock.json", "yarn.lock", "poetry.lock", "Cargo.lock"}


def _render_patch(filename: str, patch: str | None) -> str:
    """The patch text the model sees for one file — lockfiles omitted, long patches capped."""
    if filename.rsplit("/", 1)[-1] in LOCKFILES:
        return "(lock file — patch omitted)"
    text = patch or "(no patch available)"
    lines = text.split("\n")
    if len(lines) > PATCH_MAX_LINES:
        kept = "\n".join(lines[:PATCH_MAX_LINES])
        return f"{kept}\n... (patch truncated, {len(lines) - PATCH_MAX_LINES} more lines)"
    return text


def frozen_config() -> dict:
    return {
        "model": MODEL,
        "temperature": TEMPERATURE,
        "max_steps": MAX_STEPS,
        "num_ctx": NUM_CTX,
        "patch_max_lines": PATCH_MAX_LINES,
        "tools": ["get_pr_files", "read_file"],
        "metric": {
            "formula": "faithfulness * body_similarity * (0.7 + 0.3*brevity)",
            "body_similarity": "cosine(summary, reference_pr_body) rescaled [0.60,0.90]->[0,1]",
            "embed_model": EMBED_MODEL,
            "brevity_target": BREVITY_TARGET_WORDS,
            "brevity_cap": BREVITY_HARD_CAP_WORDS,
            "brevity_floor": BREVITY_FLOOR,
        },
    }


def frozen_fingerprint() -> str:
    return config_fingerprint(frozen_config())


def load_prompt() -> str:
    """The current champion system prompt — the sole optimization variable."""
    return PROMPT_FILE.read_text(encoding="utf-8").strip()


_THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)


def _clean(text: str | None) -> str:
    """Strip qwen3 reasoning traces so scoring sees only the delivered summary."""
    return _THINK_RE.sub("", text or "").strip()


def _github() -> Github:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError(
            "GITHUB_TOKEN is not set. Export it in the environment; never hard-code a token."
        )
    return Github(token)


def _build_tools(gh: Github, captured: list[str]):
    """The two frozen tools. Every tool result is captured as grounding for scoring."""

    @tool
    def get_pr_files(repo: str, pr_number: int) -> str:
        """Get the files changed by a pull request, including their patches."""
        pr = gh.get_repo(repo).get_pull(pr_number)
        blocks = []
        for f in pr.get_files():
            blocks.append(
                f"FILE: {f.filename}\n"
                f"STATUS: {f.status}\n"
                f"ADDITIONS: {f.additions}\n"
                f"DELETIONS: {f.deletions}\n"
                f"PATCH:\n{_render_patch(f.filename, f.patch)}"
            )
        out = "\n\n".join(blocks)
        captured.append(out)
        return out

    @tool
    def read_file(
        repo: str,
        pr_number: int,
        path: str,
        start_line: int | None = None,
        end_line: int | None = None,
    ) -> str:
        """Read a file from the PR head, optionally limited to a line range."""
        repository = gh.get_repo(repo)
        pr = repository.get_pull(pr_number)
        f = repository.get_contents(path, ref=pr.head.sha)
        content = f.decoded_content.decode("utf-8")
        lines = content.splitlines()
        start = (start_line or 1) - 1
        end = end_line or len(lines)
        out = "\n".join(f"{i + 1}: {lines[i]}" for i in range(start, min(end, len(lines))))
        captured.append(out)
        return out

    return [get_pr_files, read_file]


@dataclass
class SummaryResult:
    repo: str
    pr_number: int
    summary: str
    grounding: str
    verification: Verification
    metrics: Metrics
    steps: int


def summarize_pr(
    repo: str,
    pr_number: int,
    *,
    prompt: str | None = None,
    reference_body: str | None = None,
    model: str = MODEL,
    temperature: float = TEMPERATURE,
    max_steps: int = MAX_STEPS,
) -> SummaryResult:
    """Run the agent on one PR and score the result.

    ``prompt`` overrides the champion file (used by the evaluator to try a variant
    without touching the file). Everything else is frozen. The grounding used for
    scoring is exactly the concatenation of tool outputs the model actually saw.
    """
    gh = _github()
    captured: list[str] = []
    tools = _build_tools(gh, captured)
    tool_map = {t.name: t for t in tools}
    llm = ChatOllama(model=model, temperature=temperature, num_ctx=NUM_CTX).bind_tools(tools)

    system = prompt if prompt is not None else load_prompt()
    messages: list = [
        SystemMessage(content=system),
        HumanMessage(content=f"Summarize PR #{pr_number} in {repo}."),
    ]

    response = llm.invoke(messages)
    steps = 0
    while getattr(response, "tool_calls", None) and steps < max_steps:
        messages.append(response)
        for tc in response.tool_calls:
            result = tool_map[tc["name"]].invoke(tc["args"])
            messages.append(ToolMessage(content=result, tool_call_id=tc["id"]))
        response = llm.invoke(messages)
        steps += 1

    summary = _clean(response.content)
    grounding = "\n\n".join(captured)
    verification = verify(summary, grounding)
    metrics = compute_metrics(summary, grounding, verification, reference_body=reference_body)
    return SummaryResult(repo, pr_number, summary, grounding, verification, metrics, steps)


def _cli() -> None:
    import argparse
    import json

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("repo", help="owner/name, e.g. VictorFouquet/supportops")
    ap.add_argument("pr_number", type=int)
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    res = summarize_pr(args.repo, args.pr_number)
    if args.json:
        print(
            json.dumps(
                {
                    "summary": res.summary,
                    "metrics": res.metrics.as_dict(),
                    "unsupported": [str(c) for c in res.verification.unsupported],
                    "config_fp": frozen_fingerprint(),
                },
                indent=2,
            )
        )
        return
    print(res.summary)
    print("\n--- metrics ---")
    for k, v in res.metrics.as_dict().items():
        print(f"  {k}: {v}")
    if res.verification.unsupported:
        print("\nunsupported claims (not found in tool output):")
        for c in res.verification.unsupported:
            print(f"  - {c}")


if __name__ == "__main__":
    _cli()
