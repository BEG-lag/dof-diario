"""Integrity checks over the committed dataset. They run in CI after every update."""

import json
from datetime import date

import jsonschema
import pytest

from dof_diario.site import build_summary
from dof_diario.store import DATA_DIR, iter_day_files, load_days, read_meta

FILES = list(iter_day_files(DATA_DIR))
pytestmark = pytest.mark.skipif(not FILES, reason="no data committed yet")


def test_every_day_file_matches_the_schema(schema) -> None:
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    for path in FILES:
        record = json.loads(path.read_text(encoding="utf-8"))
        errors = sorted(validator.iter_errors(record), key=lambda e: e.path)
        assert not errors, f"{path.name}: {errors[0].message}"


def test_file_names_match_their_dates_and_totals() -> None:
    for path in FILES:
        record = json.loads(path.read_text(encoding="utf-8"))
        day = date.fromisoformat(record["date"])
        assert path.name == f"{day.isoformat()}.json"
        assert path.parent.name == f"{day:%m}"
        assert path.parent.parent.name == f"{day:%Y}"
        assert record["total_notes"] == len(record["notes"])
        assert record["total_avisos"] == sum(n["aviso"] for n in record["notes"])


def test_note_ids_are_unique_across_the_dataset() -> None:
    seen: dict[int, str] = {}
    for record in load_days():
        for note in record["notes"]:
            assert note["id"] not in seen, (
                f"{note['id']} in {seen.get(note['id'])} and {record['date']}"
            )
            seen[note["id"]] = record["date"]


def test_meta_and_site_summary_agree_with_the_files() -> None:
    days = load_days()
    meta = read_meta()
    assert meta["days_with_publications"] == len(days)
    assert meta["notes"] == sum(d["total_notes"] for d in days)
    published = json.loads((DATA_DIR.parent / "docs" / "data" / "summary.json").read_text())
    assert published == build_summary(days)
