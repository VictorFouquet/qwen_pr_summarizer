"""Reference-based semantic scoring for PR summaries via local embeddings.

The summarizer's real job is to write a good *PR body* — high-level context for review —
not to echo filenames. So we score a summary by how close it is, in embedding space, to
the human-written PR body that is held out from the model (it only sees the diff through
tools). This is deterministic (a forward pass, no sampling), fully local, and reference-
based, which makes it a stable optimization target — unlike an LLM judge.

The raw cosine similarity of two related texts under nomic-embed-text sits well above 0
(≈0.6 for unrelated prose, ≈0.9 for a faithful summary), so we linearly rescale that band
to [0, 1] to give the optimizer usable dynamic range. Constants are FROZEN scoring params.
"""

from __future__ import annotations

import math
import os
from functools import lru_cache

# Frozen scoring parameters for the similarity rescale. Empirically, vague/unrelated prose
# lands ≈0.62 and a good summary ≈0.86–0.91 against these PR bodies (nomic-embed-text).
SIM_FLOOR = 0.60   # maps to body_similarity 0.0
SIM_CEIL = 0.90    # maps to body_similarity 1.0
EMBED_MODEL = os.environ.get("PR_SUMMARIZER_EMBED_MODEL", "nomic-embed-text")


def _client():
    import ollama

    # Same server the summarizer uses (OLLAMA_HOST), so one backend scores a whole run.
    host = os.environ.get("OLLAMA_HOST")
    if host and not host.startswith("http"):
        host = "http://" + host
    return ollama.Client(host=host) if host else ollama.Client()


@lru_cache(maxsize=256)
def _embed(text: str) -> tuple[float, ...]:
    # nomic-embed-text was trained with task prefixes; use the same one on both sides so
    # the comparison is symmetric document-to-document.
    resp = _client().embeddings(model=EMBED_MODEL, prompt="search_document: " + text)
    return tuple(resp["embedding"])


def cosine(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def raw_similarity(summary: str, reference_body: str) -> float:
    """Unscaled cosine similarity between a summary and the reference PR body."""
    if not summary.strip() or not reference_body.strip():
        return 0.0
    return cosine(_embed(summary), _embed(reference_body))


def body_similarity(summary: str, reference_body: str) -> float:
    """Cosine similarity rescaled to [0, 1]; the loop's semantic-coverage signal.

    Returns 1.0 when there is no reference body to score against (nothing to miss).
    """
    if not reference_body.strip():
        return 1.0
    raw = raw_similarity(summary, reference_body)
    scaled = (raw - SIM_FLOOR) / (SIM_CEIL - SIM_FLOOR)
    return max(0.0, min(1.0, scaled))
