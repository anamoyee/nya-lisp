import dataclasses
from collections.abc import Callable


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
	fns: dict[str, Callable[..., str]] = dataclasses.field(default_factory=dict)

