import csv
import re
from dataclasses import KW_ONLY, dataclass
from datetime import datetime
from itertools import takewhile
from pathlib import Path
from typing import Generic, Mapping, NewType, TypeVar

import pytest

from . import JAN_1_1962_MJD, NOW_DT, NOW_MJD, Bounds, ColumnMetadata

DATA_DIR = Path(__file__).parents[1] / "astropy_iers_data" / "data"
DATA_FILE = DATA_DIR / "Leap_Second.dat"

T = TypeVar("T", int, float)

EXPECTED_COLUMN_META = [
    ColumnMetadata("MJD", type=float, bounds=Bounds(lo=JAN_1_1962_MJD, hi=NOW_MJD)),
    ColumnMetadata("day", type=int, bounds=Bounds(lo=1, hi=12)),
    ColumnMetadata("month", type=int, bounds=Bounds(lo=1, hi=31)),
    ColumnMetadata("year", type=int, bounds=Bounds(lo=1972, hi=NOW_DT.year)),
    ColumnMetadata(
        "tai-utc",
        type=int,
        bounds=Bounds(
            lo=0,
            # there is no theoritical upper bound here,
            # however a value much larger than 100 is definitely suspicious
            # as of 2026, when the maximum (then current) value was 37
            hi=100,
        ),
    ),
]


@dataclass(kw_only=True, frozen=True, slots=True)
class CSV_Data:
    header: list[str]
    rows: list[list[str]]
    names: list[str]
    types: list[type]

    def __post_init__(self):
        ncols = len(self.names)
        assert len(self.types) == ncols
        assert all(len(r) == ncols for r in self.rows)

    @property
    def ncols(self) -> int:
        return len(self.types)

    @property
    def nrows(self) -> int:
        return len(self.rows)

    def get_columns(
        self, *, max_rows: int | None = None
    ) -> list[list[float] | list[int]]:
        # last nrows of each column, cast to infered Python types
        nrows = min(max_rows or self.nrows, self.nrows)
        tail_rows = self.rows[self.nrows - nrows :]
        assert len(tail_rows) == nrows
        tail_cols = [[r[i] for r in tail_rows] for i in range(self.ncols)]
        return [
            [tp(c[i]) for i in range(nrows)]
            for c, tp in zip(
                tail_cols,
                self.types,
                strict=True,
            )
        ]


@pytest.fixture(scope="module")
def csv_data():
    with DATA_FILE.open() as fh:
        header = [
            L.removeprefix("#").strip()
            for L in takewhile(lambda L: L.startswith("#"), fh)
        ]
        rows = list(csv.reader(fh, delimiter=" ", skipinitialspace=True))

    return CSV_Data(
        header=header,
        rows=rows,
        names=["MJD", "day", "month", "year", "TAI-UTC"],
        types=[float, int, int, int, int],
    )


def test_header(csv_data):
    assert "File expires on" in "\n".join(csv_data.header)


def test_data(csv_data, subtests):
    cols = csv_data.get_columns()
    for c, meta in zip(cols, EXPECTED_COLUMN_META, strict=True):
        tp = meta.type
        with subtests.test(f"{meta.name} (types)"):
            assert all(type(e) == tp for e in c)

        if (lo := meta.bounds.lo) is not None:
            with subtests.test(f"{meta.name} (min)"):
                assert min(c) >= lo

        if (hi := meta.bounds.hi) is not None:
            with subtests.test(f"{meta.name} (max)"):
                assert max(c) <= hi
