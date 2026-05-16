from datetime import UTC, datetime

from domain.shared.clock import Clock


class SystemClock(Clock):
    def now(self) -> datetime:
        return datetime.now(UTC)
