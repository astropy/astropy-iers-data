from dataclasses import KW_ONLY, dataclass
from datetime import datetime
from typing import Generic, TypeVar

T = TypeVar("T", int, float)


@dataclass(kw_only=True, frozen=True, slots=True)
class Bounds(Generic[T]):
    lo: T | None = None
    hi: T | None = None


@dataclass(frozen=True, slots=True)
class ColumnMetadata(Generic[T]):
    name: str
    _: KW_ONLY
    type: type[T]
    bounds: Bounds[T] = Bounds()


JAN_1_1962_DT = datetime(1962, 1, 1)
JAN_1_1962_MJD = 37665.0
NOW_DT = datetime.now()
NOW_MJD = JAN_1_1962_MJD + (NOW_DT - JAN_1_1962_DT).days
