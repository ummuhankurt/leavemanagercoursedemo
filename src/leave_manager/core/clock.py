"""The only place that reads the wall clock (docs/conventions.md, Data rules)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Protocol


class Clock(Protocol):
    def now(self) -> datetime:
        """Current moment, timezone-aware UTC."""
        ...


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(UTC)


class FixedClock:
    """Deterministic clock for tests (docs/testing.md, Determinism)."""

    def __init__(self, moment: datetime) -> None:
        if moment.tzinfo is None:
            raise ValueError("FixedClock needs a timezone-aware moment")
        self.moment = moment

    def now(self) -> datetime:
        return self.moment
