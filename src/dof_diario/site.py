"""Build the static indexes the GitHub Pages site loads (``docs/data``).

Everything here is derived from ``data/`` only, with no timestamps, so the
files change only when the dataset changes.

* ``summary.json``: totals, notes per month, top issuing agencies.
* ``index-YYYY.json``: a compact search index per year. Avisos judiciales y
  generales are left out: SIDOF titles them with reference codes only.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .store import DATA_DIR, ROOT, load_days

DOCS_DATA = ROOT / "docs" / "data"
EDITION_CODES = {"matutina": 0, "vespertina": 1, "extraordinaria": 2}


def issuer(note: dict[str, Any]) -> str:
    return note.get("agency") or note.get("branch") or "SIN DEPENDENCIA"


def _dumps(data: Any) -> str:
    """Compact JSON, but with one row per line for ``notes`` so git can delta it."""
    if isinstance(data, dict) and isinstance(data.get("notes"), list):
        head = {k: v for k, v in data.items() if k != "notes"}
        rows = ",\n".join(
            json.dumps(r, ensure_ascii=False, separators=(",", ":")) for r in data["notes"]
        )
        prefix = json.dumps(head, ensure_ascii=False, separators=(",", ":"))[:-1]
        return f'{prefix},"notes":[\n{rows}\n]}}\n'
    return json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n"


def _write(path: Path, data: Any) -> bool:
    text = _dumps(data)
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return True


def build_summary(days: list[dict[str, Any]]) -> dict[str, Any]:
    by_month: dict[str, Counter[str]] = defaultdict(Counter)
    agencies: Counter[str] = Counter()
    branches: dict[str, str] = {}
    edition_days: Counter[str] = Counter()
    for day in days:
        month = day["date"][:7]
        for edition in day["editions"]:
            edition_days[edition["edition"]] += 1
        for note in day["notes"]:
            if note["aviso"]:
                by_month[month]["avisos"] += 1
                continue
            by_month[month]["notes"] += 1
            by_month[month][note["edition"]] += 1
            name = issuer(note)
            agencies[name] += 1
            branches.setdefault(name, note.get("branch") or "")
    notes = sum(d["total_notes"] for d in days)
    avisos = sum(d["total_avisos"] for d in days)
    return {
        "first_publication": days[0]["date"] if days else None,
        "last_publication": days[-1]["date"] if days else None,
        "days_with_publications": len(days),
        "notes": notes,
        "avisos": avisos,
        "indexed_notes": notes - avisos,
        "agencies_count": len(agencies),
        "edition_days": dict(edition_days),
        "by_month": [
            {
                "month": month,
                "notes": counts["notes"],
                "avisos": counts["avisos"],
                "matutina": counts["matutina"],
                "vespertina": counts["vespertina"],
                "extraordinaria": counts["extraordinaria"],
            }
            for month, counts in sorted(by_month.items())
        ],
        "top_agencies": [
            {"name": name, "branch": branches[name], "notes": count}
            for name, count in agencies.most_common(15)
        ],
        "years": sorted({d["date"][:4] for d in days}),
    }


def build_year_index(year: str, days: list[dict[str, Any]]) -> dict[str, Any]:
    agencies: list[str] = []
    position: dict[str, int] = {}
    rows: list[list[Any]] = []
    for day in days:
        if not day["date"].startswith(year):
            continue
        for note in day["notes"]:
            if note["aviso"]:
                continue
            name = issuer(note)
            if name not in position:
                position[name] = len(agencies)
                agencies.append(name)
            rows.append(
                [
                    note["id"],
                    day["date"],
                    EDITION_CODES[note["edition"]],
                    position[name],
                    note["page"],
                    note["title"],
                ]
            )
    return {
        "year": year,
        "columns": ["id", "date", "edition", "agency", "page", "title"],
        "editions": list(EDITION_CODES),
        "agencies": agencies,
        "notes": rows,
    }


def build_site(data_dir: Path = DATA_DIR, out_dir: Path = DOCS_DATA) -> list[Path]:
    days = load_days(data_dir)
    summary = build_summary(days)
    written: list[Path] = []
    target = out_dir / "summary.json"
    _write(target, summary)
    written.append(target)
    for year in summary["years"]:
        target = out_dir / f"index-{year}.json"
        _write(target, build_year_index(year, days))
        written.append(target)
    return written
