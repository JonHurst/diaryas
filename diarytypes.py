from typing import NamedTuple, Optional, Tuple
import datetime


class Entry(NamedTuple):
    timestr: Optional[str]
    text: str


class DayRecord(NamedTuple):
    date: datetime.date
    holidays: Tuple[str, ...]
    tags: Tuple[str, ...]
    entries: Tuple[Entry, ...]
