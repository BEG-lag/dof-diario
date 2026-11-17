import json
from datetime import date

from dof_diario.normalize import normalize_day
from dof_diario.store import day_path, dumps_day, iter_day_files, write_day

FRIDAY = date(2026, 11, 13)


def test_day_path_layout(tmp_path) -> None:
    assert day_path(FRIDAY, tmp_path) == tmp_path / "2026" / "11" / "2026-11-13.json"


def test_dumps_day_round_trips_with_one_note_per_line(friday) -> None:
    record = normalize_day(friday, FRIDAY)
    text = dumps_day(record)
    assert json.loads(text) == record
    note_lines = [line for line in text.splitlines() if line.startswith('    {"id"')]
    assert len(note_lines) == record["total_notes"]


def test_write_day_reports_changes(friday, holiday, tmp_path) -> None:
    record = normalize_day(friday, FRIDAY)
    assert write_day(record, tmp_path) == "created"
    assert write_day(record, tmp_path) == "unchanged"
    record["notes"][0]["title"] += " (fe de erratas)"
    assert write_day(record, tmp_path) == "updated"
    assert write_day(normalize_day(holiday, date(2026, 11, 16)), tmp_path) == "empty"
    assert [p.name for p in iter_day_files(tmp_path)] == ["2026-11-13.json"]


def test_empty_answer_never_deletes_a_stored_day(friday, holiday, tmp_path) -> None:
    write_day(normalize_day(friday, FRIDAY), tmp_path)
    empty = normalize_day(holiday, FRIDAY)  # SIDOF glitch: an empty payload for a past day
    assert write_day(empty, tmp_path) == "empty"
    assert day_path(FRIDAY, tmp_path).exists()
