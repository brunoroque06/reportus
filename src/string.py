class StrBuilder:
    def __init__(self):
        self._lines: list[str] = []

    def add_line(self, s: str = "") -> None:
        self._lines.append(s)

    def __str__(self) -> str:
        return "\n".join(self._lines)
