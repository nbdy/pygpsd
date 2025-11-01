from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime

from pygpsd.type.validation import safe_datetime, safe_int


@dataclass
class Time:
    time: datetime
    leap_seconds: int

    @staticmethod
    def from_json(data: dict) -> Time:
        return Time(
            time=safe_datetime(data.get("time")),
            leap_seconds=safe_int(data.get("leap_seconds"), 0),
        )
