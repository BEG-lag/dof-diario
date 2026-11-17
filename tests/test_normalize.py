from datetime import date

import jsonschema

from dof_diario.normalize import normalize_day

FRIDAY = date(2026, 11, 13)


def test_normalized_day_totals(friday) -> None:
    record = normalize_day(friday, FRIDAY)
    assert record["date"] == "2026-11-13"
    assert record["total_notes"] == len(record["notes"]) == 66
    assert record["total_avisos"] == 44
    assert [e["edition"] for e in record["editions"]] == ["matutina", "vespertina"]
    assert record["editions"][0]["pdf_urls"] == [
        "https://sidof.segob.gob.mx/dof/sidof/documentos/pdf/330805"
    ]


def test_separator_rows_are_dropped_and_order_is_stable(friday) -> None:
    record = normalize_day(friday, FRIDAY)
    assert all(note["title"] for note in record["notes"])
    matutina = [n for n in record["notes"] if n["edition"] == "matutina"]
    assert [n["order"] for n in matutina] == sorted(n["order"] for n in matutina)
    assert matutina[0]["id"] == 5803757


def test_note_fields(friday) -> None:
    record = normalize_day(friday, FRIDAY)
    note = next(n for n in record["notes"] if n["id"] == 5803775)
    assert note["agency"] == "BANCO DE MEXICO"
    assert note["branch_code"] == "OA"
    assert note["page"] == 178
    assert note["aviso"] is False
    assert note["url"] == "https://dof.gob.mx/nota_detalle.php?codigo=5803775&fecha=13/11/2026"


def test_normalization_is_deterministic(friday) -> None:
    assert normalize_day(friday, FRIDAY) == normalize_day(friday, FRIDAY)


def test_normalized_day_matches_the_schema(friday, schema) -> None:
    jsonschema.validate(
        normalize_day(friday, FRIDAY), schema, format_checker=jsonschema.FormatChecker()
    )


def test_holiday_has_no_notes(holiday) -> None:
    record = normalize_day(holiday, date(2026, 11, 16))
    assert record["notes"] == []
    assert record["editions"] == []
