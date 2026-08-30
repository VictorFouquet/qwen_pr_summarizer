"""Scalar metrics for one PR summary — the single source of truth for "the score".

Kept deterministic and dependency-free so a trial's numbers depend only on the two
things that vary in an optimization run: the prompt and the model's output. The
weights here are FROZEN infrastructure, not a knob — changing them invalidates
cross-trial comparison, so they live in one place and are captured in the config
fingerprint (see ``research_config``).
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass

from .embedding import body_similarity as _body_similarity
from .verifier import ClaimKind, Verification, verify

# Faithfulness must be EARNED, not granted for silence. The old score was pure precision
# (supported / total), so a summary that reads nothing and commits to nothing scored 1.0 —
# the "trader who never trades" degeneracy, which pushes the optimizer toward vagueness.
# Instead we reward grounded *specifics* and penalize hallucinations:
#     faithfulness = grounded_substance / (grounded_substance + hallucinations + ALPHA)
# An empty/vague summary → ~0; a summary that surfaces real, grounded identifiers and
# endpoints → high; any invented claim drags it down. Identifiers and endpoints (which
# only appear in the DIFFS, so they require actually reading files) are weighted fully;
# paths are cheap (they show up in the file list) so they earn little — you can't pad
# faithfulness by echoing filenames you never opened.
FAITH_ALPHA = 2.0
_CLAIM_WEIGHT = {ClaimKind.IDENTIFIER: 1.0, ClaimKind.ENDPOINT: 1.0, ClaimKind.PATH: 0.3}


def faithfulness_score(verification: Verification) -> float:
    grounded = sum(_CLAIM_WEIGHT.get(c.kind, 1.0) for c in verification.supported)
    hallucinations = len(verification.unsupported)
    return grounded / (grounded + hallucinations + FAITH_ALPHA)

# Frozen scoring parameters. Changing any of these changes what "score" means.
BREVITY_TARGET_WORDS = 200
BREVITY_HARD_CAP_WORDS = 500
# Brevity is a soft modifier in [BREVITY_FLOOR, 1.0], never a gate: a concise summary
# is nudged up, a bloated one down, but brevity alone can never rescue an empty or
# hallucinated summary (faithfulness and coverage are the multiplicative gates).
BREVITY_FLOOR = 0.7
BREVITY_RANGE = 1.0 - BREVITY_FLOOR

_FILE_LINE_RE = re.compile(r"^FILE:\s*(.+)$", re.MULTILINE)
_DIFF_GIT_RE = re.compile(r"^diff --git a/\S+ b/(\S+)$", re.MULTILINE)
_PLUSFILE_RE = re.compile(r"^\+\+\+ b/(\S+)$", re.MULTILINE)


@dataclass
class Metrics:
    faithfulness: float
    body_similarity: float
    coverage: float
    brevity: float
    composite: float
    word_count: int
    changed_files: int
    files_referenced: int
    unsupported_claims: int

    def as_dict(self) -> dict:
        return asdict(self)


def changed_files_from_grounding(grounding: str) -> list[str]:
    """Recover the changed-file paths from whatever the tools returned.

    Supports the agent's ``FILE: <path>`` tool format and raw unified diffs, so the
    metric works regardless of how grounding was assembled.
    """
    files: list[str] = []
    seen: set[str] = set()
    for regex in (_FILE_LINE_RE, _DIFF_GIT_RE, _PLUSFILE_RE):
        for m in regex.finditer(grounding):
            path = m.group(1).strip()
            if path and path != "/dev/null" and path not in seen:
                seen.add(path)
                files.append(path)
    return files


def coverage_score(summary: str, changed_files: list[str]) -> tuple[float, int]:
    """Fraction of changed files the summary actually references (path or basename)."""
    if not changed_files:
        return (1.0, 0)  # nothing to cover; don't penalize
    low = summary.lower()
    referenced = 0
    for path in changed_files:
        base = path.rsplit("/", 1)[-1]
        if path.lower() in low or base.lower() in low:
            referenced += 1
    return (referenced / len(changed_files), referenced)


def brevity_score(summary: str) -> tuple[float, int]:
    """1.0 up to the target word count, decaying linearly to 0 at the hard cap."""
    words = len(summary.split())
    if words <= BREVITY_TARGET_WORDS:
        return (1.0, words)
    if words >= BREVITY_HARD_CAP_WORDS:
        return (0.0, words)
    span = BREVITY_HARD_CAP_WORDS - BREVITY_TARGET_WORDS
    return (1.0 - (words - BREVITY_TARGET_WORDS) / span, words)


def compute_metrics(
    summary: str,
    grounding: str,
    verification: Verification | None = None,
    reference_body: str | None = None,
) -> Metrics:
    if verification is None:
        verification = verify(summary, grounding)
    files = changed_files_from_grounding(grounding)
    cov, referenced = coverage_score(summary, files)
    brev, words = brevity_score(summary)
    faith = faithfulness_score(verification)
    # The summarizer's job is a high-level PR body, so the semantic signal is how close
    # the summary is to the human PR body (reference), not how many filenames it echoes.
    # Faithfulness and body_similarity are the multiplicative gates; brevity only
    # modulates. Coverage is still computed, but as a diagnostic — it no longer scores.
    bsim = _body_similarity(summary, reference_body or "")
    composite = faith * bsim * (BREVITY_FLOOR + BREVITY_RANGE * brev)
    return Metrics(
        faithfulness=round(faith, 4),
        body_similarity=round(bsim, 4),
        coverage=round(cov, 4),
        brevity=round(brev, 4),
        composite=round(composite, 4),
        word_count=words,
        changed_files=len(files),
        files_referenced=referenced,
        unsupported_claims=len(verification.unsupported),
    )
