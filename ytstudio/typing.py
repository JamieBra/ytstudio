from enum import StrEnum, auto
from typing import Any, Mapping

ANY_TUPLE = tuple[Any]
JSON = Mapping[str, Any]
MASK = bool | dict[str, bool]


class AllowCommentsMode(StrEnum):
    APPROVED_COMMENTS = auto()


class DefaultSortOrder(StrEnum):
    MDE_COMMENT_SORT_ORDER_LATEST = auto()


class Privacy(StrEnum):
    PRIVATE = auto()
    PUBLIC = auto()
    UNLISTED = auto()
