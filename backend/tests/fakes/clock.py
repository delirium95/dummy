from datetime import UTC, datetime, timedelta

from domain.shared.clock import Clock


class FakeClock(Clock):
    def __init__(self, fixed: datetime | None = None) -> None:
        self._now = fixed if fixed is not None else datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)

    def set(self, value: datetime) -> None:
        self._now = value

    def advance_seconds(self, seconds: float) -> None:
        self._now = self._now + timedelta(seconds=seconds)

    def now(self) -> datetime:
        return self._now
