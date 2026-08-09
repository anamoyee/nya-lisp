import abc
import dataclasses as dc
import typing as t

from nya_scope import Scope

from nya_lisp.resolvers._base import ExprResolver, Literal, ResolverContext, ResolverT

# ==============================================================================
# Exception Hierarchy
# ==============================================================================


class _ParseError(SyntaxError):
	"""Base exception for all parsing errors."""


@dc.dataclass
class UnexpectedClosingBraceError(_ParseError):
	char: str
	pos: int

	def __post_init__(self):
		super().__init__(f"Unexpected character {self.char!r} at position {self.pos:d} without matching opening brace")


@dc.dataclass
class UnexpectedPipeError(_ParseError):
	char: str
	pos: int

	def __post_init__(self):
		super().__init__(f"Unexpected character {self.char!r} at position {self.pos:d} outside enclosing scope")


@dc.dataclass
class UnknownResolverError(_ParseError):
	name: t.Any

	def __post_init__(self):
		super().__init__(f"No registered resolver found for name {self.name!r}")


# ==============================================================================
# AST & Scoping
# ==============================================================================


def lower_field_to_resolver[T](nodes: tuple[AST__.NodeType[T], ...], ctx: ResolverContext[T]) -> ResolverT[T]:
	if len(nodes) == 1:
		return nodes[0].into_resolver(ctx)
	child_resolvers = tuple(node.into_resolver(ctx) for node in nodes)
	return ctx.concat_resolver_ty(args=child_resolvers, ctx=ctx)


class AST__(Scope):
	class _BaseNode[T](abc.ABC):
		@abc.abstractmethod
		def into_resolver(self, ctx: ResolverContext[T]) -> ResolverT[T]: ...

	@t.final
	@dc.dataclass
	class Constant[T](_BaseNode[T]):
		value: T

		def into_resolver(self, ctx: ResolverContext[T]) -> ResolverT[T]:
			return Literal(value=self.value, ctx=ctx)

	@t.final
	@dc.dataclass
	class Expr[T](_BaseNode[T]):
		name: tuple[AST__.NodeType[T], ...]
		children: tuple[tuple[AST__.NodeType[T], ...], ...]

		def into_resolver(self, ctx: ResolverContext[T]) -> ResolverT[T]:
			name_resolver = lower_field_to_resolver(self.name, ctx)
			child_resolvers = tuple(lower_field_to_resolver(child, ctx) for child in self.children)
			return ExprResolver(name_resolver=name_resolver, args=child_resolvers, ctx=ctx)

	type NodeType[T] = AST__.Constant[T] | AST__.Expr[T]


### Parser


def parse[T: t.Sequence[t.Any]](__s: T, /) -> list[AST__.NodeType[T]]:
	pos = 0
	length = len(__s)
	empty_val: T = __s[0:0]

	def parse_node() -> AST__.Expr[T]:
		nonlocal pos
		fields: list[list[AST__.NodeType[T]]] = [[]]
		start_pos = pos

		def flush_text():
			nonlocal start_pos
			if pos > start_pos:
				slice_val: T = __s[start_pos:pos]
				fields[-1].append(AST__.Constant(slice_val))
			start_pos = pos

		while pos < length:
			c = __s[pos]
			if c == "{":
				flush_text()
				pos += 1
				start_pos = pos
				nested_expr = parse_node()
				fields[-1].append(nested_expr)
				start_pos = pos
			elif c == "|":
				flush_text()
				pos += 1
				start_pos = pos
				if not fields[-1]:
					fields[-1].append(AST__.Constant(empty_val))
				fields.append([])
			elif c == "}":
				flush_text()
				pos += 1
				start_pos = pos
				if not fields[-1]:
					fields[-1].append(AST__.Constant(empty_val))
				name_field = tuple(fields[0])
				children_fields = tuple(tuple(f) for f in fields[1:])
				return AST__.Expr(name=name_field, children=children_fields)
			else:
				pos += 1

		raise UnexpectedClosingBraceError(char="}", pos=pos)

	nodes: list[AST__.NodeType[T]] = []
	start_pos = 0

	def flush_top_text():
		nonlocal start_pos
		if pos > start_pos:
			slice_val: T = __s[start_pos:pos]
			nodes.append(AST__.Constant(slice_val))
		start_pos = pos

	while pos < length:
		c = __s[pos]
		current_pos = pos

		if c == "{":
			flush_top_text()
			pos += 1
			start_pos = pos
			nodes.append(parse_node())
			start_pos = pos
		elif c == "}":
			raise UnexpectedClosingBraceError(char=c, pos=current_pos)
		elif c == "|":
			raise UnexpectedPipeError(char=c, pos=current_pos)
		else:
			pos += 1

	flush_top_text()
	return nodes


