from datetime import date

import httpx

from dof_diario.cli import archive
from dof_diario.sidof import USER_AGENT, Sidof


def make_sidof(friday, holiday, calls):
    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        if request.url.path.endswith("/notas/13-11-2026"):
            return httpx.Response(200, json=friday)
        if request.url.path.endswith("/notas/12-11-2026"):
            return httpx.Response(503)
        return httpx.Response(200, json=holiday)

    return Sidof(transport=httpx.MockTransport(handler), delay=0, backoff=0, max_retries=1)


def test_archive_writes_only_days_with_notes(friday, holiday, tmp_path) -> None:
    calls: list[httpx.Request] = []
    with make_sidof(friday, holiday, calls) as sidof:
        counts = archive(
            date(2026, 11, 12), date(2026, 11, 16), delay=0, data_dir=tmp_path, client=sidof
        )
    assert counts["created"] == 1
    assert counts["empty"] == 3
    assert counts["failed"] == 1  # 12-11 kept failing with 503 after one retry
    assert counts["notes"] == 66
    assert (tmp_path / "2026" / "11" / "2026-11-13.json").exists()
    assert calls[0].headers["User-Agent"] == USER_AGENT
    assert "*/*" in calls[0].headers["Accept"]


def test_archive_can_skip_existing_days(friday, holiday, tmp_path) -> None:
    calls: list[httpx.Request] = []
    with make_sidof(friday, holiday, calls) as sidof:
        archive(date(2026, 11, 13), date(2026, 11, 13), delay=0, data_dir=tmp_path, client=sidof)
        counts = archive(
            date(2026, 11, 13),
            date(2026, 11, 13),
            delay=0,
            data_dir=tmp_path,
            client=sidof,
            skip_existing=True,
        )
    assert counts["skipped"] == 1
    assert len(calls) == 1
