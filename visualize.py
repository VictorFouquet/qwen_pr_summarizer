#!/usr/bin/env python3
"""Regenerate the offline HTML progress dashboard from the research log.

    python visualize.py            # write research/progress.html
    python visualize.py --open     # ...and open it in a browser
"""

from __future__ import annotations

import argparse
import webbrowser
from pathlib import Path

from pr_summarizer.dashboard import build_dashboard_html
from pr_summarizer.researchlog import ResearchLog

ROOT = Path(__file__).resolve().parent


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--log", default=str(ROOT / "research" / "log.jsonl"))
    ap.add_argument("--out", default=str(ROOT / "research" / "progress.html"))
    ap.add_argument("--open", action="store_true", help="open the dashboard after writing it")
    args = ap.parse_args()

    records = ResearchLog(args.log).read()
    Path(args.out).write_text(build_dashboard_html(records), encoding="utf-8")
    print(f"wrote {args.out} ({len(records)} trials)")
    if args.open:
        webbrowser.open(f"file://{Path(args.out).resolve()}")


if __name__ == "__main__":
    main()
