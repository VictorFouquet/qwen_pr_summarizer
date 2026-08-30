"""Reference-free faithfulness verification for PR summaries.

The core idea: a faithful summary only asserts things that actually appear in the
source it was given (the diff / assembled context). We extract *checkable claims*
from the summary — file paths, code identifiers, and HTTP endpoints — and check
each one is grounded in the source text. Anything not grounded is a candidate
hallucination.

This is deterministic, cheap, and needs no reference summary. It is the load-bearing
guard: use it to score a summary in a prompt-optimization loop, or as a runtime gate
that rejects ungrounded output. It cannot catch every semantic error (that needs an
LLM judge — see ``llm_judge``), but it reliably catches invented paths, endpoints,
and identifiers, which is the most damaging and most common failure mode.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum


class ClaimKind(str, Enum):
    PATH = "path"
    ENDPOINT = "endpoint"
    IDENTIFIER = "identifier"


@dataclass(frozen=True)
class Claim:
    """A concrete, checkable assertion extracted from a summary."""

    text: str
    kind: ClaimKind

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"[{self.kind.value}] {self.text}"


@dataclass
class Verification:
    """Result of grounding a summary against its source."""

    score: float
    supported: list[Claim] = field(default_factory=list)
    unsupported: list[Claim] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.supported) + len(self.unsupported)

    @property
    def ok(self) -> bool:
        return not self.unsupported

    def summary_line(self) -> str:
        return (
            f"faithfulness={self.score:.2f} "
            f"({len(self.supported)}/{self.total} claims grounded, "
            f"{len(self.unsupported)} unsupported)"
        )


# --- extraction --------------------------------------------------------------

# A path-like token: at least one "dir/" segment followed by a final segment.
# Matches apps/web/src/app/page.tsx, docs/adr/0016-...md, packages/queue, etc.
_PATH_RE = re.compile(r"(?:[\w.@-]+/)+[\w.\[\]()@-]+")

# METHOD /route  (POST /api/tickets/1/status)
_ENDPOINT_RE = re.compile(
    r"\b(GET|POST|PUT|PATCH|DELETE)\b\s+(`?)(/[\w/\[\]:.-]+)\2",
    re.IGNORECASE,
)

# A bare route path even without a method: /api/session/expire
_ROUTE_RE = re.compile(r"/(?:api|auth|tickets|users|customers|teams|login)(?:/[\w\[\]:.-]+)+")

# Backtick-quoted spans — the summary's own "I am quoting the code" marker.
_BACKTICK_RE = re.compile(r"`([^`\n]+)`")

# An identifier worth checking: camelCase / PascalCase / snake_case / SCREAMING,
# length >= 3, must contain a lowercase+uppercase mix, an underscore, or be all-caps —
# i.e. it "looks like code", not an English word.
_IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]{2,}")

# A single, clean identifier occupying a whole backtick span (e.g. `mutate`, `body`).
_SINGLE_IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]{2,}")

# English/common words and generic tech nouns we never treat as checkable claims,
# so ordinary prose doesn't generate false "hallucinations".
_STOPWORDS = {
    "the", "and", "for", "with", "this", "that", "from", "into", "when", "then",
    "server", "client", "browser", "token", "cookie", "session", "request",
    "response", "component", "components", "route", "routes", "handler", "handlers",
    "page", "pages", "login", "logout", "status", "assignment", "comment", "comments",
    "ticket", "tickets", "user", "users", "agent", "agents", "customer", "customers",
    "api", "app", "web", "test", "tests", "error", "errors", "http", "https", "json",
    "get", "post", "put", "patch", "delete", "true", "false", "null", "none",
    "summary", "purpose", "changes", "context", "middleware", "cookies",
}


def _looks_like_code_identifier(tok: str) -> bool:
    if tok.lower() in _STOPWORDS:
        return False
    has_lower = any(c.islower() for c in tok)
    has_upper = any(c.isupper() for c in tok)
    has_underscore = "_" in tok
    is_screaming = tok.isupper() and len(tok) >= 3
    # camelCase / PascalCase (mixed case), snake_case, or SCREAMING_SNAKE.
    return (has_lower and has_upper) or has_underscore or is_screaming


def _looks_like_path(tok: str) -> bool:
    if "/" not in tok:
        return False
    # Avoid grabbing URLs like https://... (host claims aren't diff-checkable here).
    if tok.startswith(("http://", "https://")):
        return False
    # A real path has a file extension in its last segment, or several segments. A bare
    # two-word pair joined by a slash ("BullMQ/Redis", "console/email", "queue/worker") is
    # ordinary prose, not a file path — treating it as a path claim is a false positive.
    last = tok.rsplit("/", 1)[-1]
    return "." in last or tok.count("/") >= 2


def extract_claims(summary: str) -> list[Claim]:
    """Pull the concrete, source-checkable assertions out of a summary."""
    seen: set[tuple[str, ClaimKind]] = set()
    claims: list[Claim] = []

    def add(text: str, kind: ClaimKind) -> None:
        text = text.strip().strip("`.,;:()[]")
        if not text:
            return
        key = (text.lower(), kind)
        if key in seen:
            return
        seen.add(key)
        claims.append(Claim(text=text, kind=kind))

    # Endpoints first (most specific).
    for m in _ENDPOINT_RE.finditer(summary):
        method, _, path = m.group(1).upper(), m.group(2), m.group(3)
        add(f"{method} {path}", ClaimKind.ENDPOINT)
    for m in _ROUTE_RE.finditer(summary):
        add(m.group(0), ClaimKind.ENDPOINT)

    # Paths anywhere in the prose or code blocks.
    for m in _PATH_RE.finditer(summary):
        tok = m.group(0)
        if _looks_like_path(tok):
            add(tok, ClaimKind.PATH)

    # Identifiers inside backticks — the summary explicitly claims these are code.
    for m in _BACKTICK_RE.finditer(summary):
        inner = m.group(1).strip()
        if _looks_like_path(inner):
            add(inner, ClaimKind.PATH)
            continue
        # A backtick wrapping a single clean identifier is an explicit code claim;
        # accept it regardless of case (catches `mutate`, `body`, `isInternal`),
        # unless it is a stopworded common noun.
        if _SINGLE_IDENT_RE.fullmatch(inner) and inner.lower() not in _STOPWORDS:
            add(inner, ClaimKind.IDENTIFIER)
            continue
        # Otherwise, a multi-token span (e.g. `{ status: TicketStatus }`): only pull
        # tokens that independently look like code, to avoid flagging prose words.
        for tok in _IDENT_RE.findall(inner):
            if _looks_like_code_identifier(tok):
                add(tok, ClaimKind.IDENTIFIER)

    return claims


# --- grounding ---------------------------------------------------------------


def _normalize(text: str) -> str:
    return text.lower()


def _endpoint_path(claim_text: str) -> str:
    # "PATCH /api/x" -> "/api/x"; "/api/x" -> "/api/x"
    parts = claim_text.split(None, 1)
    return parts[1] if len(parts) == 2 else parts[0]


def is_grounded(claim: Claim, source_norm: str) -> bool:
    """Is this claim's text present in the (normalized) source?"""
    if claim.kind is ClaimKind.ENDPOINT:
        # Ground the route path (methods are hard to verify by substring alone).
        return _endpoint_path(claim.text).lower() in source_norm
    return claim.text.lower() in source_norm


def verify(summary: str, source: str) -> Verification:
    """Ground every checkable claim in ``summary`` against ``source``.

    ``source`` is the text the summary must be faithful to — the raw diff, or the
    assembled grounding context (stat + commit messages + file bodies). The stat
    section matters: it lists every changed path, so path claims stay checkable
    even when the diff is truncated for a large PR.
    """
    source_norm = _normalize(source)
    claims = extract_claims(summary)
    supported: list[Claim] = []
    unsupported: list[Claim] = []
    for claim in claims:
        (supported if is_grounded(claim, source_norm) else unsupported).append(claim)

    total = len(claims)
    score = 1.0 if total == 0 else len(supported) / total
    return Verification(score=score, supported=supported, unsupported=unsupported)


# --- optional semantic pass --------------------------------------------------


def llm_judge(summary: str, source: str, complete_fn) -> str:
    """Optional second opinion for *semantic* faithfulness the grounder can't see.

    ``complete_fn(system, user) -> str`` is any chat-completion callable (e.g. a
    local model). Kept separate and optional so the deterministic grounder above
    stays the trustworthy gate; an LLM judge is advisory, never the sole authority.
    """
    system = (
        "You check whether a PR summary is faithful to a diff. Reply with a short "
        "list of any statement in the summary that is NOT supported by the diff, or "
        "the single word FAITHFUL if every statement is supported. Judge only "
        "against the diff; do not add opinions."
    )
    user = f"## Diff\n{source}\n\n## Summary\n{summary}"
    return complete_fn(system, user)
