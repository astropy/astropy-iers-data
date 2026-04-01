import csv
import re
from dataclasses import KW_ONLY, dataclass
from datetime import datetime
from itertools import takewhile
from pathlib import Path
from typing import Generic, TypeVar

import pytest

DATA_DIR = Path(__file__).parents[1] / "astropy_iers_data" / "data"
DATA_FILE = DATA_DIR / "eopc04.1962-now"

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


EXPECTED_COLUMN_META = [
    ColumnMetadata("YR", type=int, bounds=Bounds(lo=1962, hi=NOW_DT.year)),
    ColumnMetadata("MM", type=int, bounds=Bounds(lo=1, hi=12)),
    ColumnMetadata("DD", type=int, bounds=Bounds(lo=1, hi=31)),
    ColumnMetadata("HH", type=int, bounds=Bounds(lo=0, hi=23)),
    ColumnMetadata("MJD", type=float, bounds=Bounds(lo=JAN_1_1962_MJD, hi=NOW_MJD)),
    ColumnMetadata('x(")', type=float),
    ColumnMetadata('y(")', type=float),
    ColumnMetadata("UT1-UTC(s)", type=float),
    ColumnMetadata('dX(")', type=float),
    ColumnMetadata('dY(")', type=float),
    ColumnMetadata('xrt("/day)', type=float),
    ColumnMetadata('yrt("/day)', type=float),
    ColumnMetadata("LOD(s)", type=float),
    ColumnMetadata("x Er", type=float),
    ColumnMetadata("y Er", type=float),
    ColumnMetadata("UT1-UTC Er", type=float),
    ColumnMetadata("dX Er", type=float),
    ColumnMetadata("dY Er", type=float),
    ColumnMetadata("xrt Er", type=float),
    ColumnMetadata("yrt Er", type=float),
    ColumnMetadata("LOD Er", type=float),
]

SIMPLE_FMT_REGEXP = r"(?P<type>i(4|8)|f\d+\.\d+)"
REPEATED_FMT_REGEXP = rf"(?P<count>\d+)\({SIMPLE_FMT_REGEXP}\)"


@dataclass(kw_only=True, frozen=True, slots=True)
class CSV_Data:
    header: list[str]
    rows: list[list[str]]

    def __post_init__(self):
        ncols = self.ncols
        assert all(len(r) == ncols for r in self.rows[1:])

    @property
    def ncols(self) -> int:
        return len(self.rows[0])

    @property
    def nrows(self) -> int:
        return len(self.rows)

    @property
    def formats(self) -> list[str]:
        formats_line = self.header[4]
        raw_formats = formats_line.removeprefix("format(").removesuffix(")").split(",")
        expanded_formats: list[str] = []
        for fmt in raw_formats:
            if (match := re.fullmatch(SIMPLE_FMT_REGEXP, fmt)) is not None:
                count = 1
                tp = match.group("type")
            elif (match := re.fullmatch(REPEATED_FMT_REGEXP, fmt)) is not None:
                count = int(match.group("count"))
                tp = match.group("type")
            else:
                # should be unreacheable, only useful when test code itself is broken
                raise RuntimeError(f"failed to parse {fmt!r}")

            expanded_formats.extend([tp] * count)
        return expanded_formats

    @property
    def compatible_py_types(self) -> list[type]:
        types: list[type] = []
        for fmt in self.formats:
            if fmt.startswith("i"):
                tp = int
            elif fmt.startswith("f"):
                tp = float
            else:
                # should be unreacheable, only useful when test code itself is broken
                raise RuntimeError
            types.append(tp)
        return types

    @property
    def names(self) -> list[str]:
        return re.split(r"\s\s+", self.header[5].removeprefix("#").strip())

    def get_columns(self, *, max_rows: int | None = None) -> list[list[float] | list[int]]:
        # last nrows of each column, cast to infered Python types
        nrows = min(max_rows or self.nrows, self.nrows)
        tail_rows = self.rows[self.nrows - nrows :]
        assert len(tail_rows) == nrows
        tail_cols = [[r[i] for r in tail_rows] for i in range(self.ncols)]
        return [
            [tp(c[i]) for i in range(nrows)]
            for c, tp in zip(
                tail_cols,
                self.compatible_py_types,
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

    return CSV_Data(header=header, rows=rows)


def test_header(csv_data):
    assert len(csv_data.header) == 6


def test_columns_meta(csv_data):
    assert csv_data.names == [c.name for c in EXPECTED_COLUMN_META]
    assert csv_data.compatible_py_types == [c.type for c in EXPECTED_COLUMN_META]


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
