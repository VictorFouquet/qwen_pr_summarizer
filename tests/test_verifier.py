"""Tests for the reference-free faithfulness verifier.

These are pure and offline — no network, no model, no GitHub. They pin the
behaviour that makes the verifier trustworthy: real claims pass, invented claims
are flagged, and ordinary prose does not generate false positives.
"""

from pr_summarizer.verifier import (
    Claim,
    ClaimKind,
    extract_claims,
    verify,
)

# A small slice of a realistic diff/grounding text (App Router, PATCH routes, etc.).
REAL_SOURCE = """
diff --git a/apps/web/src/app/(auth)/login/login-form.tsx b/apps/web/src/app/(auth)/login/login-form.tsx
+        orgSlug: form.get('orgSlug'),
diff --git a/apps/web/src/app/api/tickets/[id]/status/route.ts b/apps/web/src/app/api/tickets/[id]/status/route.ts
+export async function PATCH(
+  const { status } = (await req.json()) as { status: TicketStatus };
diff --git a/apps/web/src/components/tickets/comment-form.tsx b/apps/web/src/components/tickets/comment-form.tsx
+  const [isInternal, setIsInternal] = useState(false);
+      body,
+      isInternal,
const STATUSES: TicketStatus[] = ['OPEN', 'PENDING', 'RESOLVED', 'CLOSED'];
"""


def kinds(claims):
    return {(c.text, c.kind) for c in claims}


def test_grounded_summary_scores_perfect():
    summary = (
        "Adds `apps/web/src/app/api/tickets/[id]/status/route.ts` with a PATCH "
        "handler. The comment form posts `body` and `isInternal`. Statuses are "
        "OPEN, PENDING, RESOLVED, CLOSED."
    )
    result = verify(summary, REAL_SOURCE)
    assert result.unsupported == []
    assert result.score == 1.0
    assert result.ok


def test_flags_the_qwen_hallucinations():
    # The exact fabrications the local model produced against this PR.
    summary = (
        "The app uses `pages/index.tsx` (Pages Router). Login posts to "
        "`/api/auth/login`. Status values are open, `in_progress`, and closed. "
        "The comment form sends a `content` field. Components live in "
        "`components/tickets/status-control.js`."
    )
    result = verify(summary, REAL_SOURCE)
    texts = {c.text for c in result.unsupported}
    assert "pages/index.tsx" in texts
    assert any("/api/auth/login" in t for t in texts)
    assert "components/tickets/status-control.js" in texts
    assert "in_progress" in texts  # backticked, snake_case -> checkable identifier
    assert result.score < 0.5
    assert not result.ok


def test_endpoint_path_is_grounded_even_with_wrong_method():
    # The route path is real; we ground the path (method mismatch is out of scope
    # for the deterministic pass). A real path should not be flagged.
    summary = "There is a POST `/api/tickets/[id]/status` endpoint."
    result = verify(summary, REAL_SOURCE)
    assert all("api/tickets" not in c.text for c in result.unsupported)


def test_invented_endpoint_path_is_flagged():
    summary = "Login goes through `/api/auth/login`."
    result = verify(summary, REAL_SOURCE)
    assert any("auth/login" in c.text for c in result.unsupported)


def test_plain_prose_does_not_create_false_claims():
    summary = (
        "This pull request adds a web client so that agents can manage tickets "
        "from the browser. The session is kept on the server and the browser "
        "never holds the token."
    )
    result = verify(summary, REAL_SOURCE)
    # Ordinary English + stopworded domain nouns -> nothing checkable, nothing wrong.
    assert result.unsupported == []
    assert result.ok


def test_extract_claims_types():
    claims = extract_claims(
        "See `apps/web/src/lib/mutate.ts`; it exports `mutate`. PATCH /api/x/y."
    )
    assert Claim("apps/web/src/lib/mutate.ts", ClaimKind.PATH) in claims
    assert Claim("mutate", ClaimKind.IDENTIFIER) in claims
    assert any(c.kind is ClaimKind.ENDPOINT for c in claims)


def test_empty_summary_is_vacuously_ok():
    result = verify("", REAL_SOURCE)
    assert result.score == 1.0
    assert result.total == 0
    assert result.ok
