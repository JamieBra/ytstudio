from enum import StrEnum, auto
from typing import Any, Iterable


class Visibility(StrEnum):
    PRIVATE = auto()
    UNLISTED = auto()
    PUBLIC = auto()


ANY_TUPLE = tuple[Any]
MASK = bool | dict[str, bool]
OPT_BOOL = bool | None
OPT_STR_ITER = Iterable[str] | None
OPT_VISIBILITY = str | Visibility | None
