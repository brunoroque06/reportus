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
    res = t1.concat(t2)
    assert len(res.rows) == 3
    assert res.rows[2] == Row("c", 3)


def test_filter_by_value():
    t = init_table(("a", 1), ("b", 2), ("c", 1))
    res = t.filter(value=1)
    assert len(res.rows) == 2
    assert [r.name for r in res.rows] == ["a", "c"]


def test_filter_by_callable():
    t = init_table(("a", 1), ("b", 5), ("c", 3))
    res = t.filter(value=lambda v: v > 2)
    assert [r.name for r in res.rows] == ["b", "c"]


def test_filter_multiple_kwargs():
    t = init_table(("a", 1), ("a", 2), ("b", 1))
    res = t.filter(name="a", value=1)
    assert len(res.rows) == 1
    assert res.rows[0] == Row("a", 1)


def test_filter_no_match():
    t = init_table(("a", 1))
    res = t.filter(name="z")
    assert res.is_empty()


def test_is_empty():
    assert from_list([]).is_empty()
    assert not init_table(("a", 1)).is_empty()


def test_item():
    t = init_table(("a", 1), ("b", 2))
    assert t.item() == Row("a", 1)


def test_sort():
    t = init_table(("a", 1), ("b", 2), ("b1", 0))
    res = t.sort(key=lambda r: r.name if len(r.name) == 2 else r.name + "z")
    assert res.rows[0] == Row("a", 1)
    assert res.rows[1] == Row("b1", 0)
    assert res.rows[2] == Row("b", 2)


def test_map():
    t = init_table(("a", 1), ("b", 2))
    res = t.map(lambda r: Row(r.name * 2, r.value * 2))
    assert res.rows[0] == Row("aa", 2)
    assert res.rows[1] == Row("bb", 4)


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
