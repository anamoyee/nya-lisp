import dataclasses
from collections.abc import Callable

from .types._base import LispSerde


@dataclasses.dataclass
class Separators:
	argument: str = "|"
	kwarg_key_value: str = "="
	type_deserialize: str = ","


@dataclasses.dataclass
class Brackets:
	open: str = "{"
	close: str = "}"


@dataclasses.dataclass
class Parser:
	separator: Separators = dataclasses.field(default_factory=Separators)
	bracket: Brackets = dataclasses.field(default_factory=Brackets)

	type LispTy = type[LispSerde]
	tys: dict[str, LispTy] = dataclasses.field(default_factory=dict)

	type LispFn = Callable[..., str]
	fns: dict[str, LispFn] = dataclasses.field(default_factory=dict)
