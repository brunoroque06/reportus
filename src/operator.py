from collections.abc import Callable


def ge(c: int) -> Callable[[int], bool]:
    return lambda v: v >= c


def gt(c: int) -> Callable[[int], bool]:
    return lambda v: v > c


def le(c: int) -> Callable[[int], bool]:
    return lambda v: v <= c
