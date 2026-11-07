from enum import StrEnum


class ReadingStatus(StrEnum):
    """読書ステータス。"""

    UNREAD = "unread"  # 積読
    READING = "reading"  # 読書中
    COMPLETED = "completed"  # 読了
