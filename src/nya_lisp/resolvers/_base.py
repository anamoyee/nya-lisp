import abc
import dataclasses as dc
from typing import Any


@dc.dataclass
class ResolverContext[T]:
	resolvers: tuple[type[ResolverT[T]], ...]
	concat_resolver_ty: type[ResolverT[T]]
	dct: dict[str, Any] = dc.field(default_factory=dict)


@dc.dataclass
class ResolverT[T = str](abc.ABC):
	args: tuple[ResolverT[T], ...]
	ctx: ResolverContext[T]

	@classmethod
	@abc.abstractmethod
	def accept(cls, name: T) -> bool: ...

	@abc.abstractmethod
	def resolve(self) -> T: ...


@dc.dataclass
class Literal[T = str](ResolverT[T]):
	value: T

	def __init__(self, value: T, ctx: ResolverContext[T], args: tuple[ResolverT[T], ...] = ()):
		super().__init__(args=args, ctx=ctx)
		self.value = value

	@classmethod
	def accept(cls, name: T) -> bool:
		return False

	def resolve(self) -> T:
		return self.value


@dc.dataclass
class ExprResolver[T = str](ResolverT[T]):
	name_resolver: ResolverT[T]

	def __init__(
		self,
		name_resolver: ResolverT[T],
		ctx: ResolverContext[T],
		args: tuple[ResolverT[T], ...] = (),
	):
		super().__init__(args=args, ctx=ctx)
		self.name_resolver = name_resolver

	@classmethod
	def accept(cls, name: T) -> bool:
		return False

	def resolve(self) -> T:
		resolved_name = self.name_resolver.resolve()
		resolver_cls = find_resolver_type(resolved_name, self.ctx)
		target_resolver = resolver_cls(args=self.args, ctx=self.ctx)
		return target_resolver.resolve()


def find_resolver_type[T](name: T, ctx: ResolverContext[T]) -> type[ResolverT[T]]:
	for ty in ctx.resolvers:
		if ty.accept(name):
			return ty
	raise ValueError(f"No registered resolver found for name {name!r}")


