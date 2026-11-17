"""Command line entry point: ``dof-diario update | backfill | build-site | stats``."""

from __future__ import annotations

import argparse
import sys
import time
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from .normalize import normalize_day
from .sidof import Sidof, SidofError
from .site import DOCS_DATA, build_site
from .store import DATA_DIR, day_path, load_days, read_meta, write_day, write_meta

MX_TZ = ZoneInfo("America/Mexico_City")
COVERAGE_FROM = date(2025, 1, 1)


def today_mx() -> date:
    return datetime.now(MX_TZ).date()


def _parse_day(text: str) -> date:
    if text in {"today", "hoy"}:
        return today_mx()
    return date.fromisoformat(text)


def archive(
    start: date,
    end: date,
    *,
    delay: float,
    skip_existing: bool = False,
    data_dir: Path = DATA_DIR,
    client: Sidof | None = None,
) -> Counter[str]:
    """Fetch every day in ``[start, end]`` and store the ones with publications."""
    counts: Counter[str] = Counter()
    total = (end - start).days + 1
    began = time.monotonic()
    owned = client is None
    sidof = client or Sidof(delay=delay)
    try:
        for i in range(total):
            day = start + timedelta(days=i)
            if skip_existing and day_path(day, data_dir).exists():
                counts["skipped"] += 1
                continue
            try:
                record = normalize_day(sidof.day(day), day)
            except SidofError as exc:
                counts["failed"] += 1
                print(f"  ! {day}: {exc}", file=sys.stderr)
                continue
            status = write_day(record, data_dir)
            counts[status] += 1
            counts["notes"] += record["total_notes"]
            if status in {"created", "updated"}:
                print(f"  {status:>8} {day} ({record['total_notes']} notes)")
            if (i + 1) % 50 == 0:
                elapsed = time.monotonic() - began
                print(f"  ... {i + 1}/{total} days in {elapsed:.0f}s", flush=True)
    finally:
        if owned:
            sidof.close()
    counts["requests"] = sidof.requests
    return counts


def refresh_meta(data_dir: Path = DATA_DIR) -> dict:
    days = load_days(data_dir)
    meta = {
        "schema_version": 1,
        "coverage_from": COVERAGE_FROM.isoformat(),
        "first_publication": days[0]["date"] if days else None,
        "last_publication": days[-1]["date"] if days else None,
        "days_with_publications": len(days),
        "notes": sum(d["total_notes"] for d in days),
        "avisos": sum(d["total_avisos"] for d in days),
    }
    previous = read_meta(data_dir)
    write_meta(meta, data_dir)
    if previous != meta:
        print(f"meta: {meta['days_with_publications']} days, {meta['notes']} notes")
    return meta


def _summary(label: str, counts: Counter[str], seconds: float) -> None:
    keys = ("created", "updated", "unchanged", "empty", "skipped", "failed", "requests", "notes")
    parts = ", ".join(f"{k}={counts[k]}" for k in keys if counts[k])
    print(f"{label}: {parts} in {seconds:.1f}s")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="dof-diario", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    update = sub.add_parser("update", help="re-fetch the last N days (default 4), then rebuild")
    update.add_argument("--days", type=int, default=4)
    update.add_argument("--delay", type=float, default=1.0)

    backfill = sub.add_parser("backfill", help="fetch a historical range")
    backfill.add_argument("--start", type=_parse_day, default=COVERAGE_FROM)
    backfill.add_argument("--end", type=_parse_day, default=None)
    backfill.add_argument("--delay", type=float, default=0.5)
    backfill.add_argument("--skip-existing", action="store_true")

    sub.add_parser("build-site", help="rebuild docs/data indexes from data/")
    sub.add_parser("stats", help="print dataset statistics")

    args = parser.parse_args(argv)
    began = time.monotonic()

    if args.command == "update":
        end = today_mx()
        start = end - timedelta(days=args.days - 1)
        print(f"Updating {start} to {end} (Mexico City date)")
        counts = archive(start, end, delay=args.delay)
        _summary("update", counts, time.monotonic() - began)
        refresh_meta()
        build_site()
        return 1 if counts["failed"] and not (counts["created"] or counts["unchanged"]) else 0

    if args.command == "backfill":
        end = args.end or today_mx()
        print(f"Backfilling {args.start} to {end}")
        counts = archive(args.start, end, delay=args.delay, skip_existing=args.skip_existing)
        _summary("backfill", counts, time.monotonic() - began)
        refresh_meta()
        return 1 if counts["failed"] else 0

    if args.command == "build-site":
        meta = refresh_meta()
        written = build_site()
        print(f"Wrote {len(written)} files to {DOCS_DATA} ({meta['notes']} notes)")
        return 0

    if args.command == "stats":
        meta = refresh_meta()
        for key, value in meta.items():
            print(f"{key:>24}: {value}")
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
