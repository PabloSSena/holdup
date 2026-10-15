from datetime import datetime, timedelta


class FakeClock:
    """A clock the test moves by hand. Call it to read the time, like datetime.now."""

    def __init__(self, start: datetime = datetime(2026, 1, 5, 9, 0, 0)):
        self.now = start

    def __call__(self) -> datetime:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += timedelta(seconds=seconds)
