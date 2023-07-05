from enum import StrEnum, auto
from typing import Any


class Visibility(StrEnum):
    PRIVATE = auto()
    UNLISTED = auto()
    PUBLIC = auto()


ANY_TUPLE = tuple[Any]
MASK = bool | dict[str, bool]
OPT_BOOL = bool | None
OPT_LIST_STR = list[str] | None
OPT_VISIBILITY = str | Visibility | None
