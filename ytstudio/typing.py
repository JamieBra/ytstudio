from enum import StrEnum, auto
from typing import Any, Mapping


class Visibility(StrEnum):
    PRIVATE = auto()
    UNLISTED = auto()
    PUBLIC = auto()


ANY_TUPLE = tuple[Any]
JSON = Mapping[str, Any]
MASK = bool | dict[str, bool]
OPT_BOOL = bool | None
OPT_LIST_STR = list[str] | None
OPT_STR = str | None
OPT_VISIBILITY = str | Visibility | None
