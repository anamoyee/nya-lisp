import typing as t
from collections.abc import Iterable, Sequence
from typing import Any

from .parse.parser import AST__, parse
from .resolvers._base import ResolverContext, ResolverT
from .resolvers._builtin import RL_ALL, Concat


class Client[T: Sequence[Any] = str]:
	def __init__(
		self,
		*resolvers: type[ResolverT[T]],
		resolvers_list: Iterable[type[ResolverT[T]]] | None = None,
		concat_resolver: type[ResolverT[T]] | None = None,
		dct: dict[str, Any] | None = None,
	):
		if resolvers_list is not None:
			self.resolvers: tuple[type[ResolverT[T]], ...] = tuple(resolvers_list)
		elif resolvers:
			self.resolvers = tuple(resolvers)
		else:
			self.resolvers = tuple(t.cast(tuple[type[ResolverT[T]], ...], RL_ALL))

		self.concat_resolver: type[ResolverT[T]] = (
			concat_resolver if concat_resolver is not None else t.cast(type[ResolverT[T]], Concat)
		)
		self.dct: dict[str, Any] = dct if dct is not None else {}

	def get_context(self) -> ResolverContext[T]:
		return ResolverContext(
			dct=self.dct,
			resolvers=self.resolvers,
			concat_resolver_ty=self.concat_resolver,
		)

	def resolve_nodes(self, nodes: list[AST__.NodeType[T]]) -> T:
		ctx = self.get_context()
		resolvers = [node.into_resolver(ctx) for node in nodes]
		top_resolver = ctx.concat_resolver_ty(args=tuple(resolvers), ctx=ctx)
		return top_resolver.resolve()

	def __call__(self, __input: T, /) -> T:
		nodes = parse(__input)
		return self.resolve_nodes(nodes)


