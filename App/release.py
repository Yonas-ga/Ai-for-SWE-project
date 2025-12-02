from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Release:
    """
    Represents a single release window.
    """
    start_day: datetime
    end_date: datetime
    working_days: int
