"""Render the research log as a self-contained, offline HTML dashboard.

No server, no CDN: the trial data is embedded and the chart is drawn with inline
SVG, so ``progress.html`` opens straight in a browser. Shows the composite score
and its sub-metrics across trials, marks the best trial, and lists every trial with
its prompt id so you can see what the researcher tried and whether it is improving.
"""

from __future__ import annotations

import html
import json

_METRIC_COLORS = {
    "composite": "#2563eb",
    "faithfulness": "#16a34a",
    "coverage": "#d97706",
    "brevity": "#9333ea",
}


def _polyline(values: list[float], w: int, h: int, pad: int) -> str:
    n = len(values)
    if n == 0:
        return ""
    if n == 1:
        x = pad
        y = h - pad - values[0] * (h - 2 * pad)
        return f"{x},{y:.1f}"
    step = (w - 2 * pad) / (n - 1)
    pts = []
    for i, v in enumerate(values):
        x = pad + i * step
        y = h - pad - max(0.0, min(1.0, v)) * (h - 2 * pad)
        pts.append(f"{x:.1f},{y:.1f}")
    return " ".join(pts)


def _svg_chart(records: list[dict]) -> str:
    w, h, pad = 760, 320, 40
    series = {m: [r["metrics"].get(m, 0.0) for r in records] for m in _METRIC_COLORS}
    trials = [r.get("trial", i + 1) for i, r in enumerate(records)]

    # y gridlines at 0, .25, .5, .75, 1
    grid = []
    for frac in (0, 0.25, 0.5, 0.75, 1.0):
        y = h - pad - frac * (h - 2 * pad)
        grid.append(
            f'<line x1="{pad}" y1="{y:.1f}" x2="{w - pad}" y2="{y:.1f}" '
            f'stroke="#e5e7eb" stroke-width="1"/>'
            f'<text x="{pad - 8}" y="{y + 4:.1f}" text-anchor="end" '
            f'font-size="11" fill="#6b7280">{frac:.2f}</text>'
        )

    lines = []
    for metric, color in _METRIC_COLORS.items():
        pts = _polyline(series[metric], w, h, pad)
        if pts:
            lines.append(
                f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2"/>'
            )

    # mark the best composite trial
    best_mark = ""
    if records:
        best_i = max(range(len(records)), key=lambda i: records[i]["metrics"].get("composite", 0.0))
        n = len(records)
        step = (w - 2 * pad) / max(1, n - 1)
        bx = pad + best_i * step if n > 1 else pad
        bv = records[best_i]["metrics"].get("composite", 0.0)
        by = h - pad - bv * (h - 2 * pad)
        best_mark = (
            f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="5" fill="none" '
            f'stroke="#2563eb" stroke-width="2"/>'
            f'<text x="{bx:.1f}" y="{by - 10:.1f}" text-anchor="middle" '
            f'font-size="11" fill="#2563eb">best {bv:.2f}</text>'
        )

    # x labels (trial numbers)
    xlabels = []
    n = len(records)
    if n:
        step = (w - 2 * pad) / max(1, n - 1)
        for i, t in enumerate(trials):
            x = pad + i * step if n > 1 else pad
            xlabels.append(
                f'<text x="{x:.1f}" y="{h - pad + 16}" text-anchor="middle" '
                f'font-size="11" fill="#6b7280">{t}</text>'
            )

    legend = []
    lx = pad
    for metric, color in _METRIC_COLORS.items():
        legend.append(
            f'<rect x="{lx}" y="10" width="12" height="12" fill="{color}"/>'
            f'<text x="{lx + 16}" y="20" font-size="12" fill="#374151">{metric}</text>'
        )
        lx += 110

    return (
        f'<svg viewBox="0 0 {w} {h}" width="100%" style="max-width:{w}px">'
        + "".join(grid)
        + "".join(lines)
        + best_mark
        + "".join(xlabels)
        + "".join(legend)
        + "</svg>"
    )


def _rows(records: list[dict]) -> str:
    out = []
    best_i = (
        max(range(len(records)), key=lambda i: records[i]["metrics"].get("composite", 0.0))
        if records
        else -1
    )
    for i, r in enumerate(records):
        m = r["metrics"]
        star = " ★" if i == best_i else ""
        out.append(
            "<tr>"
            f"<td>{r.get('trial', i + 1)}{star}</td>"
            f"<td><code>{html.escape(str(r.get('prompt_id', '')))}</code></td>"
            f"<td>{m.get('composite', 0):.3f}</td>"
            f"<td>{m.get('faithfulness', 0):.3f}</td>"
            f"<td>{m.get('coverage', 0):.3f}</td>"
            f"<td>{m.get('brevity', 0):.3f}</td>"
            f"<td>{html.escape(str(r.get('note', '')))}</td>"
            "</tr>"
        )
    return "\n".join(out)


def build_dashboard_html(records: list[dict]) -> str:
    """Return a complete, standalone HTML document for the given trial records."""
    chart = _svg_chart(records) if records else "<p>No trials logged yet.</p>"
    rows = _rows(records)
    data_json = html.escape(json.dumps(records))
    best = (
        max(records, key=lambda r: r["metrics"].get("composite", 0.0)) if records else None
    )
    best_line = (
        f"Best composite: <b>{best['metrics']['composite']:.3f}</b> "
        f"(trial {best.get('trial')}, prompt <code>{best.get('prompt_id')}</code>)"
        if best
        else "No trials yet."
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PR Summarizer — prompt optimization</title>
<style>
  body {{ font-family: system-ui, -apple-system, sans-serif; margin: 2rem; color: #111827; }}
  h1 {{ font-size: 1.25rem; }}
  table {{ border-collapse: collapse; margin-top: 1rem; font-size: 0.9rem; }}
  th, td {{ border-bottom: 1px solid #e5e7eb; padding: 6px 12px; text-align: left; }}
  th {{ color: #6b7280; font-weight: 600; }}
  code {{ background: #f3f4f6; padding: 1px 4px; border-radius: 3px; }}
  .card {{ border: 1px solid #e5e7eb; border-radius: 8px; padding: 1rem 1.25rem; max-width: 820px; }}
</style></head>
<body>
  <h1>Prompt optimization progress</h1>
  <p>Only the system prompt varies; model, tools, and metric are frozen.</p>
  <div class="card">{chart}</div>
  <p style="margin-top:1rem">{best_line}</p>
  <table>
    <thead><tr>
      <th>trial</th><th>prompt</th><th>composite</th>
      <th>faithful</th><th>coverage</th><th>brevity</th><th>note</th>
    </tr></thead>
    <tbody>{rows}</tbody>
  </table>
  <script type="application/json" id="trials">{data_json}</script>
</body></html>
"""
