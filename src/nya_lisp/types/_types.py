import dataclasses
from typing import Self

from ._base import LispSerde


@dataclasses.dataclass
class Result(LispSerde):
	inner: str
	is_err: bool

	def serialize(self) -> LispSerde.Serialized:
		return {"is_err": "1" if self.is_err else "", "inner": self.inner}

	@classmethod
	def deserialize(cls, *args: str, **kwargs: str) -> Self:
		match args, kwargs:
			case (), {"is_err": str(is_err), "inner": str(inner)}:
				pass
			case _:
				raise ValueError(f"Invalid args/kwargs for Result.deserialize: {args=}, {kwargs=}")

		return cls(inner=inner, is_err=bool(is_err))
