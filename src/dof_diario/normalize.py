"""Turn a raw SIDOF ``/notas/{fecha}`` payload into the dataset's day record.

The output is deliberately stable: no fetch timestamps and a deterministic
order, so re-running the archiver only produces a git diff when the DOF really
changed.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date, datetime
from typing import Any

from .sidof import BASE_URL, sidof_date

SCHEMA_VERSION = 1

EDITIONS: tuple[tuple[str, str], ...] = (
    ("NotasMatutinas", "matutina"),
    ("NotasVespertinas", "vespertina"),
    ("NotasExtraordinarias", "extraordinaria"),
)
EDITION_ORDER = {name: i for i, (_, name) in enumerate(EDITIONS)}


def _clean(value: Any) -> Any:
    if isinstance(value, str):
        value = value.strip()
        return None if value in {"", "null", "None"} else value
    return value


def _flag(value: Any) -> bool:
    return _clean(value) == "S"


def _int(value: Any) -> int | None:
    value = _clean(value)
    if value is None:
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def official_url(note_id: int, day: date) -> str:
    return f"https://dof.gob.mx/nota_detalle.php?codigo={note_id}&fecha={day.strftime('%d/%m/%Y')}"


def edition_pdf_url(diario_id: int) -> str:
    return f"{BASE_URL}/documentos/pdf/{diario_id}"


def normalize_note(raw: Mapping[str, Any], edition: str, day: date) -> dict[str, Any] | None:
    title = _clean(raw.get("titulo"))
    note_id = _int(raw.get("codNota"))
    if not title or note_id is None:
        return None  # untitled rows are agency headers inside the table of contents
    raw_day = _clean(raw.get("fecha"))
    note_day = datetime.strptime(raw_day, "%d-%m-%Y").date() if raw_day else day
    branch_code = _clean(raw.get("codOrgaUno"))
    kind = _clean(raw.get("tipoNota"))
    order = float(_clean(raw.get("orden")) or 0)
    return {
        "id": note_id,
        "edition": edition,
        "order": int(order) if order.is_integer() else order,
        "section": _clean(raw.get("codSeccion")),
        "diario_id": _int(raw.get("codDiario")),
        "page": _int(raw.get("pagina")),
        "branch": _clean(raw.get("nombreCodOrgaUno")),
        "branch_code": branch_code,
        "agency": _clean(raw.get("codOrgaDos")),
        "title": " ".join(title.split()),
        "aviso": kind == "AVISO" or branch_code == "AV",
        "has_doc": _flag(raw.get("existeDoc")),
        "has_pdf": _flag(raw.get("existePdf")),
        "url": official_url(note_id, note_day),
    }


def normalize_day(payload: Mapping[str, Any], day: date) -> dict[str, Any]:
    """Return the normalized record for ``day`` (it may contain zero notes)."""
    notes: list[dict[str, Any]] = []
    editions: list[dict[str, Any]] = []
    for key, edition in EDITIONS:
        parsed = [
            note
            for raw in payload.get(key) or []
            if (note := normalize_note(raw, edition, day)) is not None
        ]
        if not parsed:
            continue
        parsed.sort(key=lambda n: (n["order"], n["id"]))
        diario_ids = sorted({n["diario_id"] for n in parsed if n["diario_id"]})
        editions.append(
            {
                "edition": edition,
                "notes": len(parsed),
                "avisos": sum(n["aviso"] for n in parsed),
                "diario_ids": diario_ids,
                "pdf_urls": [edition_pdf_url(d) for d in diario_ids],
            }
        )
        notes.extend(parsed)
    return {
        "schema_version": SCHEMA_VERSION,
        "date": day.isoformat(),
        "source": f"{BASE_URL}/notas/{sidof_date(day)}",
        "total_notes": len(notes),
        "total_avisos": sum(n["aviso"] for n in notes),
        "editions": editions,
        "notes": notes,
    }
