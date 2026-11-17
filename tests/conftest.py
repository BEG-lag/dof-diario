from __future__ import annotations

import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"
ROOT = Path(__file__).resolve().parents[1]


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


@pytest.fixture
def friday() -> dict:
    """Raw SIDOF payload for 2026-11-13 (matutina + vespertina)."""
    return load_fixture("notas__13-11-2026.json")


@pytest.fixture
def holiday() -> dict:
    """Raw SIDOF payload for 2026-11-16 (no publication)."""
    return load_fixture("notas__16-11-2026.json")


@pytest.fixture
def schema() -> dict:
    return json.loads((ROOT / "schema" / "day.schema.json").read_text(encoding="utf-8"))
