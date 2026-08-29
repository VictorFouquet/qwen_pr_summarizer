"""Offline tests for the scoring metrics."""

from pr_summarizer.metrics import (
    brevity_score,
    changed_files_from_grounding,
    compute_metrics,
    coverage_score,
)

GROUNDING = """
FILE: apps/web/src/app/api/tickets/[id]/status/route.ts
STATUS: added
PATCH:
+export async function PATCH(
FILE: apps/web/src/components/tickets/comment-form.tsx
STATUS: added
PATCH:
+  const [isInternal, setIsInternal] = useState(false);
"""


def test_changed_files_parsed_from_tool_format():
    files = changed_files_from_grounding(GROUNDING)
    assert "apps/web/src/app/api/tickets/[id]/status/route.ts" in files
    assert "apps/web/src/components/tickets/comment-form.tsx" in files
    assert len(files) == 2


def test_changed_files_parsed_from_raw_diff():
    diff = "diff --git a/pkg/x.ts b/pkg/x.ts\n+++ b/pkg/x.ts\n"
    assert "pkg/x.ts" in changed_files_from_grounding(diff)


def test_coverage_rewards_referencing_changed_files():
    files = changed_files_from_grounding(GROUNDING)
    summary_full = "Adds status/route.ts and comment-form.tsx."
    cov, n = coverage_score(summary_full, files)
    assert cov == 1.0 and n == 2

    cov_half, _ = coverage_score("Adds comment-form.tsx only.", files)
    assert cov_half == 0.5

    cov_none, _ = coverage_score("A vague summary mentioning nothing concrete.", files)
    assert cov_none == 0.0


def test_brevity_full_then_decays():
    assert brevity_score("word " * 100)[0] == 1.0
    assert brevity_score("word " * 200)[0] == 1.0
    assert brevity_score("word " * 1000)[0] == 0.0
    mid, _ = brevity_score("word " * 350)  # between target 200 and cap 500
    assert 0.0 < mid < 1.0


def test_composite_gates_on_faithfulness():
    files = "apps/web/src/lib/mutate.ts"
    grounding = f"FILE: {files}\nPATCH:\n+export function mutate() {{}}\n"

    # Faithful + covering + short -> high composite.
    good = "Adds `apps/web/src/lib/mutate.ts` exporting `mutate`."
    good_m = compute_metrics(good, grounding)
    assert good_m.faithfulness == 1.0
    assert good_m.coverage == 1.0
    assert good_m.composite > 0.9

    # Hallucinated path -> faithfulness collapses -> composite collapses.
    bad = "Adds `pages/index.tsx` and `/api/auth/login`."
    bad_m = compute_metrics(bad, grounding)
    assert bad_m.faithfulness < 0.5
    assert bad_m.composite < good_m.composite

    # Empty summary -> coverage 0 -> composite 0 even though nothing is "unfaithful".
    empty_m = compute_metrics("", grounding)
    assert empty_m.composite == 0.0
