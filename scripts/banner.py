"""Generate assets/banner.svg from the dataset (docs/data/summary.json).

    uv run python scripts/banner.py

The bar chart is the real number of titled notes per month; the footer states the
date and totals the banner was generated from, so it never claims more than it knows.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "docs" / "data" / "summary.json"
OUT = ROOT / "assets" / "banner.svg"

MONTHS_ES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]


def month_label(month: str) -> str:
    year, number = month.split("-")
    return f"{MONTHS_ES[int(number) - 1]} {year}"


def main() -> None:
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    months = summary["by_month"]
    as_of = date.fromisoformat(summary["last_publication"])

    chart_x, chart_y, chart_w, chart_h = 660, 96, 476, 196
    peak = max(m["notes"] for m in months)
    slot = chart_w / len(months)
    bar_w = slot * 0.62
    bars = []
    for i, m in enumerate(months):
        h = max(2.0, m["notes"] / peak * chart_h)
        x = chart_x + i * slot + (slot - bar_w) / 2
        y = chart_y + chart_h - h
        partial = i == len(months) - 1 and m["month"] == as_of.strftime("%Y-%m")
        opacity = ' opacity="0.45"' if partial else ""
        bars.append(
            f'<rect class="bar" style="animation-delay:{0.15 + i * 0.04:.2f}s" x="{x:.1f}" '
            f'y="{y:.1f}" width="{bar_w:.1f}" height="{h:.1f}" rx="2" fill="#cfff45"{opacity}>'
            f"<title>{month_label(m['month'])}: {m['notes']} notas</title></rect>"
        )
    first, last = month_label(months[0]["month"]), month_label(months[-1]["month"])
    notes = f"{summary['notes']:,}"
    days = f"{summary['days_with_publications']:,}"

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 400" width="1200" height="400" role="img" aria-labelledby="title desc">
  <title id="title">dof-diario</title>
  <desc id="desc">A living open dataset of the Diario Oficial de la Federación table of contents, updated daily by GitHub Actions. The chart shows titled notes per month from {first} to {last}. As of {as_of.isoformat()} the dataset holds {notes} notes from {days} days with an edition.</desc>
  <defs>
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M40 0H0V40" fill="none" stroke="#191d27" stroke-width="1"/>
    </pattern>
    <radialGradient id="glow" cx="0.8" cy="0.15" r="0.75">
      <stop offset="0" stop-color="#cfff45" stop-opacity="0.12"/>
      <stop offset="0.55" stop-color="#cfff45" stop-opacity="0"/>
    </radialGradient>
    <style>
      .mono {{ font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace; }}
      .serif {{ font-family: 'Cormorant Garamond', 'Iowan Old Style', Georgia, 'Times New Roman', serif; font-style: italic; }}
      .sans {{ font-family: Inter, ui-sans-serif, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }}
      .bar {{ transform-box: fill-box; transform-origin: 50% 100%; animation: grow 0.7s cubic-bezier(.2,.8,.2,1) both; }}
      .dot {{ animation: pulse 2.4s ease-in-out infinite; }}
      @keyframes grow {{ from {{ transform: scaleY(0); }} to {{ transform: scaleY(1); }} }}
      @keyframes pulse {{ 50% {{ opacity: 0.25; }} }}
      @media (prefers-reduced-motion: reduce) {{ .bar, .dot {{ animation: none; }} }}
    </style>
  </defs>

  <rect width="1200" height="400" fill="#0a0c10"/>
  <rect width="1200" height="400" fill="url(#grid)" opacity="0.7"/>
  <rect width="1200" height="400" fill="url(#glow)"/>

  <g>
    <circle class="dot" cx="69" cy="75" r="5" fill="#cfff45"/>
    <text x="86" y="80" class="mono" font-size="13" letter-spacing="3" fill="#969dab">OPEN DATASET · GITHUB ACTIONS · DAILY</text>
    <text x="60" y="170" class="mono" font-size="76" font-weight="700" fill="#eceee6" letter-spacing="-1">dof<tspan fill="#cfff45">-diario</tspan></text>
    <text x="64" y="228" class="serif" font-size="32" fill="#eceee6">el sumario del Diario Oficial,</text>
    <text x="64" y="264" class="serif" font-size="32" fill="#eceee6">archivado cada día.</text>
    <text x="64" y="318" class="sans" font-size="15" fill="#969dab">Every DOF note since January 2025 · JSON + JSON Schema · static search site</text>
    <text x="64" y="344" class="mono" font-size="13" fill="#ffb648">beg-lag.github.io/dof-diario</text>
  </g>

  <g>
    <text x="{chart_x}" y="74" class="mono" font-size="12" fill="#969dab">notas por mes · {first} a {last}</text>
    <line x1="{chart_x}" x2="{chart_x + chart_w}" y1="{chart_y + chart_h + 0.5}" y2="{chart_y + chart_h + 0.5}" stroke="#232838"/>
    {chr(10).join("    " + b for b in bars).strip()}
    <text x="{chart_x}" y="{chart_y + chart_h + 26}" class="mono" font-size="12" fill="#eceee6">{notes} <tspan fill="#969dab">notes</tspan>  {days} <tspan fill="#969dab">days</tspan></text>
  </g>

  <text x="1140" y="376" text-anchor="end" class="mono" font-size="11" fill="#969dab" opacity="0.8">data as of {as_of.isoformat()} · unofficial, not legal advice</text>
</svg>
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(svg, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(months)} months, peak {peak})")


if __name__ == "__main__":
    main()
