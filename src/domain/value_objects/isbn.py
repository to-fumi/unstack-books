from dataclasses import dataclass

from domain.exceptions import DomainValidationError


@dataclass(frozen=True, slots=True)
class Isbn:
    # ISBN-10 と ISBN-13 を同一の本とみなせるよう、ISBN-13 に正規化して保持する
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.replace("-", "").replace(" ", "").upper()
        if self._is_valid_isbn13(normalized):
            pass
        elif self._is_valid_isbn10(normalized):
            normalized = self._to_isbn13(normalized)
        else:
            raise DomainValidationError(f"Invalid ISBN: {self.value}")
        object.__setattr__(self, "value", normalized)

    @staticmethod
    def _is_valid_isbn13(v: str) -> bool:
        if len(v) != 13 or not v.isdigit():
            return False
        total = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(v))
        return total % 10 == 0

    @staticmethod
    def _is_valid_isbn10(v: str) -> bool:
        if len(v) != 10 or not v[:9].isdigit() or not (v[9].isdigit() or v[9] == "X"):
            return False
        total = sum((10 - i) * (10 if c == "X" else int(c)) for i, c in enumerate(v))
        return total % 11 == 0

    @staticmethod
    def _to_isbn13(isbn10: str) -> str:
        body = "978" + isbn10[:9]
        total = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(body))
        return body + str((10 - total % 10) % 10)

    def __str__(self) -> str:
        return self.value
