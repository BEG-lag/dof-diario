"""The static site must only reference files that exist (no build step to catch it)."""

import json
import re
from pathlib import Path

DOCS = Path(__file__).resolve().parents[1] / "docs"


def test_local_references_in_index_html_exist() -> None:
    html = (DOCS / "index.html").read_text(encoding="utf-8")
    refs = re.findall(r'(?:href|src)="([^"#:]+)"', html)
    local = [r for r in refs if not r.startswith(("//", "./")) and r != "./"]
    assert local, "expected local references such as styles.css and app.js"
    for ref in local:
        assert (DOCS / ref).exists(), f"index.html references missing file {ref}"


def test_site_data_files_exist_for_every_year() -> None:
    summary = json.loads((DOCS / "data" / "summary.json").read_text(encoding="utf-8"))
    for year in summary["years"]:
        index = json.loads((DOCS / "data" / f"index-{year}.json").read_text(encoding="utf-8"))
        assert index["columns"] == ["id", "date", "edition", "agency", "page", "title"]
        assert all(row[1].startswith(year) for row in index["notes"])
    total = sum(
        len(json.loads((DOCS / "data" / f"index-{y}.json").read_text())["notes"])
        for y in summary["years"]
    )
    assert total == summary["indexed_notes"]


def test_site_has_disclaimer_and_no_external_scripts() -> None:
    html = (DOCS / "index.html").read_text(encoding="utf-8")
    assert "solo el DOF impreso/oficial es fuente auténtica" in html
    assert not re.search(r'<script[^>]+src="https?://', html)
