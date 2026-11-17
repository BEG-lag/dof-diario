"""Read and write the dataset on disk.

Layout: ``data/YYYY/MM/YYYY-MM-DD.json``, one file per day with at least one
publication, plus ``data/meta.json`` with the coverage window. Files are written
with one note per line: compact enough to keep the repository small and still
friendly to ``git diff``.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"


def day_path(day: date, data_dir: Path = DATA_DIR) -> Path:
    return data_dir / f"{day:%Y}" / f"{day:%m}" / f"{day.isoformat()}.json"


def dumps_day(record: dict[str, Any]) -> str:
    """Serialize a day record: pretty top level, one compact line per note."""
    head = {k: v for k, v in record.items() if k != "notes"}
    lines = ["{"]
    for key, value in head.items():
        lines.append(f"  {json.dumps(key)}: {json.dumps(value, ensure_ascii=False)},")
    notes = record.get("notes", [])
    if notes:
        lines.append('  "notes": [')
        rendered = [
            "    " + json.dumps(n, ensure_ascii=False, separators=(", ", ": ")) for n in notes
        ]
        lines.append(",\n".join(rendered))
        lines.append("  ]")
    else:
        lines.append('  "notes": []')
    lines.append("}")
    return "\n".join(lines) + "\n"


def write_day(record: dict[str, Any], data_dir: Path = DATA_DIR) -> str:
    """Write ``record`` if it changed. Returns 'created', 'updated', 'unchanged' or 'empty'.

    Days without notes are not stored; a previously stored file is kept, because an
    empty answer for a past day is far more likely a transient SIDOF problem than
    a retracted edition.
    """
    day = date.fromisoformat(record["date"])
    path = day_path(day, data_dir)
    if not record["notes"]:
        return "empty"
    text = dumps_day(record)
    if path.exists():
        if path.read_text(encoding="utf-8") == text:
            return "unchanged"
        status = "updated"
    else:
        status = "created"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return status


def iter_day_files(data_dir: Path = DATA_DIR) -> Iterator[Path]:
    yield from sorted(data_dir.glob("[0-9][0-9][0-9][0-9]/[0-9][0-9]/*.json"))


def load_days(data_dir: Path = DATA_DIR) -> list[dict[str, Any]]:
    return [json.loads(p.read_text(encoding="utf-8")) for p in iter_day_files(data_dir)]


def read_meta(data_dir: Path = DATA_DIR) -> dict[str, Any]:
    path = data_dir / "meta.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_meta(meta: dict[str, Any], data_dir: Path = DATA_DIR) -> bool:
    path = data_dir / "meta.json"
    text = json.dumps(meta, ensure_ascii=False, indent=2) + "\n"
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return True
