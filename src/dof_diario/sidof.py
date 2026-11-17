"""Minimal, polite client for the public SIDOF API (synchronous on purpose).

The archiver runs unattended in GitHub Actions, so it favours simplicity: one
request at a time, a fixed pause between requests, retries with exponential
backoff on network errors, 429 and 5xx, and a descriptive User-Agent.
"""

from __future__ import annotations

import random
import time
from datetime import date
from typing import Any

import httpx

from . import __version__

BASE_URL = "https://sidof.segob.gob.mx/dof/sidof"
USER_AGENT = f"dof-diario/{__version__} (+https://github.com/BEG-lag/dof-diario)"
RETRY_STATUS = {429, 500, 502, 503, 504}


class SidofError(RuntimeError):
    pass


def sidof_date(day: date) -> str:
    return day.strftime("%d-%m-%Y")


class Sidof:
    def __init__(
        self,
        *,
        base_url: str = BASE_URL,
        delay: float = 0.5,
        timeout: float = 30.0,
        max_retries: int = 4,
        backoff: float = 2.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.delay = delay
        self.max_retries = max_retries
        self.backoff = backoff
        self.requests = 0
        self.seconds_waiting = 0.0
        self._last = 0.0
        self._http = httpx.Client(
            timeout=httpx.Timeout(timeout, connect=10.0),
            # SIDOF answers 406 to a bare "Accept: application/json".
            headers={"User-Agent": USER_AGENT, "Accept": "application/json, */*;q=0.8"},
            transport=transport,
            follow_redirects=True,
        )

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> Sidof:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def _pause(self) -> None:
        wait = self._last + self.delay - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        self._last = time.monotonic()

    def get_json(self, path: str) -> dict[str, Any]:
        url = f"{self.base_url}/{path.lstrip('/')}"
        error = "unknown error"
        for attempt in range(self.max_retries + 1):
            if attempt:
                sleep = self.backoff * 2 ** (attempt - 1) + random.uniform(0, self.backoff)
                self.seconds_waiting += sleep
                time.sleep(sleep)
            self._pause()
            try:
                response = self._http.get(url)
                self.requests += 1
            except httpx.TransportError as exc:
                error = f"{type(exc).__name__}: {exc}"
                continue
            if response.status_code in RETRY_STATUS:
                error = f"HTTP {response.status_code}"
                continue
            if response.status_code >= 400:
                raise SidofError(f"HTTP {response.status_code} for {url}")
            try:
                payload = response.json()
            except ValueError as exc:
                raise SidofError(f"Invalid JSON for {url}") from exc
            if not isinstance(payload, dict):
                raise SidofError(f"Unexpected payload for {url}")
            return payload
        raise SidofError(f"Giving up on {url} after {self.max_retries + 1} attempts ({error})")

    def day(self, day: date) -> dict[str, Any]:
        """Raw ``/notas/{DD-MM-YYYY}`` payload for one date."""
        return self.get_json(f"notas/{sidof_date(day)}")
