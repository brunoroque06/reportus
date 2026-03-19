class StrBuilder:
    def __init__(self):
        self._lines: list[str] = []

    def add(self, s: str = "") -> None:
        self._lines.append(s)

    def build(self, sep: str = "\n") -> str:
        return sep.join(self._lines)
