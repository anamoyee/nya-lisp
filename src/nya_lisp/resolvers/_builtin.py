import dataclasses as dc
import typing as t
from typing import Any

from ._base import ResolverT

if True:  # RL_MATH

	@dc.dataclass
	class Add(ResolverT[str]):
		@classmethod
		def accept(cls, name: str) -> bool:
			return name in {
				cls.__name__.lower(),
				"+",
			}

		def resolve(self) -> str:
			return str(sum(int(arg.resolve()) for arg in self.args))

	@dc.dataclass
	class Sub(ResolverT[str]):
		@classmethod
		def accept(cls, name: str) -> bool:
			return name in {
				cls.__name__.lower(),
				"-",
			}

		def resolve(self) -> str:
			if not self.args:
				return "0"
			arg0, *args = self.args
			if not args:
				return str(-int(arg0.resolve()))
			return str(int(arg0.resolve()) - sum(int(arg.resolve()) for arg in args))

	RL_MATH = [
		Add,
		Sub,
	]

if True:  # RL_STR

	@dc.dataclass
	class Concat[T: Any = str](ResolverT[T]):
		@classmethod
		def accept(cls, name: T) -> bool:
			return name in {
				cls.__name__.lower(),
				"cat",
				"concat",
			}

		def resolve(self) -> T:
			if not self.args:
				raise ValueError("Concat resolver called with no arguments")
			result: Any = self.args[0].resolve()
			for arg in self.args[1:]:
				result = result + arg.resolve()
			return t.cast(T, result)



	# resolver lists
	RL_STR = [
		Concat,
	]


if True:  # RL_MISC

	@dc.dataclass
	class Comment(ResolverT[str]):
		@classmethod
		def accept(cls, name: str) -> bool:
			return name in {
				cls.__name__.lower(),
				"//",
				"#",
			}

		def resolve(self) -> str:
			# Decides to NOT resolve any of self.args
			return ""

	RL_MISC = [
		Comment,
	]


RL_ALL: list[type[ResolverT[str]]] = [
	*RL_STR,
	*RL_MATH,
	*RL_MISC,
]

