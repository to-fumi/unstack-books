"""ドメイン層の例外。HTTP などの外部の関心事には依存しない。"""


class DomainError(Exception):
    """ドメイン例外の基底クラス。"""


class DomainValidationError(DomainError):
    """ドメインルール違反（不正な値など）。"""


class BookNotFoundError(DomainError):
    def __init__(self, book_id: object) -> None:
        super().__init__(f"Book not found: {book_id}")
        self.book_id = book_id
