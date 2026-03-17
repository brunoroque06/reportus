import dataclasses

from src.report.mabc import TRow
from src.table import Table, from_list, read_csv


@dataclasses.dataclass(frozen=True)
class Row:
    name: str
    value: int


def init_table(*rows: tuple[str, int]) -> Table[Row]:
    return from_list([Row(n, v) for n, v in rows])


def test_concat():
    t1 = init_table(("a", 1), ("b", 2))
    t2 = init_table(("c", 3))
    result = t1.concat(t2)
    assert len(result.rows) == 3
    assert result.rows[2] == Row("c", 3)


def test_filter_by_value():
    t = init_table(("a", 1), ("b", 2), ("c", 1))
    result = t.filter(value=1)
    assert len(result.rows) == 2
    assert [r.name for r in result.rows] == ["a", "c"]


def test_filter_by_callable():
    t = init_table(("a", 1), ("b", 5), ("c", 3))
    result = t.filter(value=lambda v: v > 2)
    assert [r.name for r in result.rows] == ["b", "c"]


def test_filter_multiple_kwargs():
    t = init_table(("a", 1), ("a", 2), ("b", 1))
    result = t.filter(name="a", value=1)
    assert len(result.rows) == 1
    assert result.rows[0] == Row("a", 1)


def test_filter_no_match():
    t = init_table(("a", 1))
    result = t.filter(name="z")
    assert result.is_empty()


def test_is_empty():
    assert from_list([]).is_empty()
    assert not init_table(("a", 1)).is_empty()


def test_item():
    t = init_table(("a", 1), ("b", 2))
    assert t.item() == Row("a", 1)


def test_to_dicts():
    t = init_table(("a", 1), ("b", 2))
    assert t.to_dicts() == [
        {"name": "a", "value": 1},
        {"name": "b", "value": 2},
    ]


def test_from_list():
    rows = [Row("x", 10)]
    t = from_list(rows)
    assert t.rows == rows


def test_read_csv():
    t = read_csv("public/mabc-t.csv", TRow)
    assert len(t.rows) == 75
