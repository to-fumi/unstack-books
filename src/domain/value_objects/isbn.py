from dataclasses import dataclass

from domain.exceptions import DomainValidationError


@dataclass(frozen=True, slots=True)
class Isbn:
    """ISBN 値オブジェクト（ISBN-10 / ISBN-13）。ハイフンは取り除いて保持する。"""

    value: str

    def __post_init__(self) -> None:
        normalized = self.value.replace("-", "").replace(" ", "").upper()
        if not self._is_valid(normalized):
            raise DomainValidationError(f"Invalid ISBN: {self.value}")
        object.__setattr__(self, "value", normalized)

    @staticmethod
    def _is_valid(v: str) -> bool:
        if len(v) == 13 and v.isdigit():
            total = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(v))
            return total % 10 == 0
        if len(v) == 10 and v[:9].isdigit() and (v[9].isdigit() or v[9] == "X"):
            total = sum((10 - i) * (10 if c == "X" else int(c)) for i, c in enumerate(v))
            return total % 11 == 0
        return False

    def __str__(self) -> str:
        return self.value
