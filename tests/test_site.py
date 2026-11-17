from datetime import date

from dof_diario.normalize import normalize_day
from dof_diario.site import build_site, build_summary, build_year_index
from dof_diario.store import write_day


def test_summary_counts(friday) -> None:
    day = normalize_day(friday, date(2026, 11, 13))
    summary = build_summary([day])
    assert summary["notes"] == 66
    assert summary["avisos"] == 44
    assert summary["indexed_notes"] == 22
    assert summary["by_month"] == [
        {
            "month": "2026-11",
            "notes": 22,
            "avisos": 44,
            "matutina": 17,
            "vespertina": 5,
            "extraordinaria": 0,
        }
    ]
    top = summary["top_agencies"][0]
    assert top == {"name": "PRESIDENCIA DE LA REPUBLICA", "branch": "PODER EJECUTIVO", "notes": 7}


def test_year_index_excludes_avisos_and_uses_lookup_tables(friday) -> None:
    day = normalize_day(friday, date(2026, 11, 13))
    index = build_year_index("2026", [day])
    assert index["columns"] == ["id", "date", "edition", "agency", "page", "title"]
    assert len(index["notes"]) == 22
    note_id, when, edition, agency, page, title = index["notes"][0]
    assert (note_id, when, edition, page) == (5803757, "2026-11-13", 0, 4)
    assert index["agencies"][agency] == "PRESIDENCIA DE LA REPUBLICA"
    assert title.startswith("Decreto por el que se expide la Ley de Ingresos")
    assert build_year_index("2025", [day])["notes"] == []


def test_build_site_is_idempotent(friday, tmp_path) -> None:
    data, out = tmp_path / "data", tmp_path / "out"
    write_day(normalize_day(friday, date(2026, 11, 13)), data)
    first = {p.name: p.read_text() for p in build_site(data, out)}
    second = {p.name: p.read_text() for p in build_site(data, out)}
    assert first == second
    assert set(first) == {"summary.json", "index-2026.json"}
