"""Offline test for the HTML dashboard builder."""

from pr_summarizer.dashboard import build_dashboard_html

RECORDS = [
    {
        "trial": 1,
        "prompt_id": "aaa111",
        "note": "seed",
        "metrics": {"composite": 0.30, "faithfulness": 0.5, "coverage": 0.8, "brevity": 1.0},
    },
    {
        "trial": 2,
        "prompt_id": "bbb222",
        "note": "ground the paths",
        "metrics": {"composite": 0.75, "faithfulness": 0.9, "coverage": 0.9, "brevity": 1.0},
    },
]


def test_build_dashboard_is_standalone_html_with_data():
    html = build_dashboard_html(RECORDS)
    assert html.lstrip().startswith("<!doctype html>")
    assert "<svg" in html  # inline chart, no external chart lib
    assert "http://" not in html and "https://" not in html  # fully offline, no CDN
    # best trial (composite 0.75) is surfaced
    assert "0.75" in html
    assert "bbb222" in html
    # both trials appear in the table
    assert "ground the paths" in html


def test_empty_log_renders_placeholder():
    html = build_dashboard_html([])
    assert "No trials logged yet" in html
    assert html.lstrip().startswith("<!doctype html>")
