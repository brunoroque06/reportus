import csv
import dataclasses
import typing
from typing import Any, Callable, ClassVar, Protocol


class DataclassInstance(Protocol):
    __dataclass_fields__: ClassVar[dict[str, Any]]


@dataclasses.dataclass(frozen=True)
class Table[T: DataclassInstance]:
    rows: list[T]

    def concat(self, other: "Table[T]") -> "Table[T]":
        return Table(self.rows + other.rows)

    def filter(self, **kwargs: Any) -> "Table[T]":
        def match(row: T) -> bool:
            for k, v in kwargs.items():
                val = getattr(row, k)
                if callable(v):
                    if not v(val):
                        return False
                elif val != v:
                    return False
            return True

        return Table([r for r in self.rows if match(r)])

    def is_empty(self) -> bool:
        return len(self.rows) == 0

    def item(self) -> T:
        return self.rows[0]

    def map[V: DataclassInstance](self, func: Callable[[T], V]) -> "Table[V]":
        return Table([func(r) for r in self.rows])

    def sort(self, key: Callable[[T], str | int]) -> "Table[T]":
        return Table(sorted(self.rows, key=key))

    def to_dicts(self) -> list[dict[str, Any]]:
        fields = dataclasses.fields(self.rows[0])
        return [{f.name: getattr(r, f.name) for f in fields} for r in self.rows]


def read_csv[T: DataclassInstance](path: str, cls: type[T]) -> Table[T]:
    fields = dataclasses.fields(cls)
    type_hints = typing.get_type_hints(cls)
    with open(path) as f:
        reader = csv.DictReader(f)
        rows: list[T] = []
        for raw in reader:
            values = {}
            for field in fields:
                if field.name in raw:
                    values[field.name] = type_hints[field.name](raw[field.name])
            rows.append(cls(**values))

    return Table(rows)


def from_list[T: DataclassInstance](rows: list[T]) -> Table[T]:
    return Table(rows)
