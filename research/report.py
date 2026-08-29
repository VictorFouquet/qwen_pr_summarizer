#!/usr/bin/env python3
"""Render the research log into a human-readable Markdown progress report.

READ-ONLY over ``research/log.jsonl`` — this is a reporting artifact, not part of the
frozen scoring harness. It changes no scored behavior and no ``config_fp``; it exists so
a human can read every trial's hypothesis, metrics, AND the actual summary the agent
produced for each PR (which otherwise only lives as JSON in the log).

    python research/report.py            # writes research/summaries.md
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG = ROOT / "research" / "log.jsonl"
OUT = ROOT / "research" / "summaries.md"


def _read_trials() -> list[dict]:
    if not LOG.exists():
        return []
    return [json.loads(line) for line in LOG.read_text(encoding="utf-8").splitlines() if line.strip()]


def _fmt_metrics(m: dict) -> str:
    return (
        f"composite **{m['composite']:.4f}** · "
        f"faith {m['faithfulness']:.3f} · cov {m['coverage']:.3f} · brev {m['brevity']:.3f}"
    )


def render(trials: list[dict]) -> str:
    lines: list[str] = []
    lines.append("# PR-summarizer research — trial-by-trial progress\n")
    lines.append(
        "Human-readable companion to `research/log.jsonl`. For each trial: the hypothesis "
        "(note), the aggregate score, and the **actual summary the agent produced** for "
        "each eval PR. Regenerate with `python research/report.py`.\n"
    )

    if trials:
        best = max(trials, key=lambda t: t["metrics"]["composite"])
        lines.append("## Scoreboard\n")
        lines.append(f"Best so far: **{best['metrics']['composite']:.4f}** (trial {best['trial']}).\n")
        lines.append("| Trial | Composite | Faith | Cov | Brev | Note |")
        lines.append("|------:|----------:|------:|----:|-----:|------|")
        for t in trials:
            m = t["metrics"]
            star = " ⭐" if t["trial"] == best["trial"] else ""
            note = (t.get("note") or "").replace("|", "\\|").replace("\n", " ")
            lines.append(
                f"| {t['trial']}{star} | {m['composite']:.4f} | {m['faithfulness']:.3f} | "
                f"{m['coverage']:.3f} | {m['brevity']:.3f} | {note} |"
            )
        lines.append("")

    for t in trials:
        m = t["metrics"]
        lines.append(f"\n---\n\n## Trial {t['trial']} — {_fmt_metrics(m)}\n")
        lines.append(f"- **Prompt id:** `{t.get('prompt_id', '?')}` · **config_fp:** `{t.get('config_fp', '?')}`")
        lines.append(f"- **Hypothesis / note:** {t.get('note') or '_(none)_'}\n")
        for p in t["per_pr"]:
            lines.append(
                f"### {p['repo']}#{p['pr_number']} — {_fmt_metrics(p)} "
                f"({p['files_referenced']}/{p['changed_files']} files, {p['word_count']} words)\n"
            )
            summary = (p.get("summary") or "").strip() or "_(empty summary)_"
            lines.append("> " + summary.replace("\n", "\n> ") + "\n")
            if p.get("unsupported"):
                lines.append("<details><summary>Unsupported claims (hallucinations)</summary>\n")
                for claim in p["unsupported"]:
                    lines.append(f"- `{claim}`")
                lines.append("\n</details>\n")
    return "\n".join(lines) + "\n"


def main() -> None:
    trials = _read_trials()
    OUT.write_text(render(trials), encoding="utf-8")
    print(f"wrote {OUT} ({len(trials)} trials)")


if __name__ == "__main__":
    main()
