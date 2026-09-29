import abc
import dataclasses as dc
import functools
import typing as t
from collections.abc import Callable

from nya_scope import Scope


@dc.dataclass(kw_only=True)
class Context:
	nodes: tuple[type[_ExprNode], ...]
	custom: dict[str, str] = dc.field(default_factory=dict)

	@classmethod
	def null(cls) -> t.Self:
		"""Return a context with no custom values, no nodes registered, etc."""
		return cls(
			nodes=(),
			custom={},
		)

	@classmethod
	def default(cls, custom: dict[str, str] | None = None) -> t.Self:
		"""Return a context with default set of nodes.

		!!! Warning: This set may let users escape out of sandbox, start long single-threaded computations, etc. Use with caution.
		"""
		return cls(
			nodes=(
				BuiltinNodes__.Str__.Concat,
				BuiltinNodes__.Math__.Add,
			),
			custom=custom if custom is not None else {},
		)


@dc.dataclass(kw_only=False)
class _StaticNode:
	"""A node that always resolves to its static value."""

	value: str

	def resolve(self) -> str:
		return self.value


@dc.dataclass(kw_only=True)
class _ExprNode(abc.ABC):
	name: str
	"""The name due to which this node was instantiated, this was the `accept()`ed name, it's there if you accept multiple names for the same node class, but want to slightly tweak the behaviour for each of the names."""
	args: tuple[NodeT, ...]
	"""The arguments to this node, used in `resolve()`, this does not include the leading `.name`."""

	ctx: Context
	"""The context scoped to the entire execution of this node tree."""

	@classmethod
	@abc.abstractmethod
	def accept(cls, name: str, /) -> bool:
		"""Based on the name of the expr node candidate, is this node able to resolve with the given protocol?

		e.g. for node `{add|...|...}`, user is expected to provide only numbers in place of any ... given, there's also an implicit contract of *args (any number of arguments). This node declares that it supports the add protocol if it returns `True` on that name passed to `accept()`.
		"""  # ruff: ignore[missing-trailing-period]

	@abc.abstractmethod
	def resolve(self) -> str:
		"""Compute the value of this node, given the arguments in `self.args`, store or act upon any side effects stored in `self.ctx`.

		This node may choose to either eagerly resolve the underlying nodes, or do some lazy evaulation e.g. {add|1|2} requires the values of all the arguments (`("1", "2")` in this case)
		"""

	@classmethod
	def new_from_args(cls, name_node: NodeT, *args_rest: NodeT, ctx: Context) -> NodeT:
		"""Return an ExprNode matching args[0] from ctx.nodes, resolving the name node if required, fallback to Concat.

		Raises:
			KeyError: If no node class in ctx.nodes accepts the name of the node.
		"""
		name = name_node.resolve()

		for node_cls in ctx.nodes:
			if node_cls.accept(name):
				return node_cls(name=name, args=args_rest, ctx=ctx)

		raise KeyError(name)


type NodeT = _ExprNode | _StaticNode


class _IntoExprInputFnProtocol(t.Protocol):
	__name__: str

	@staticmethod
	def __call__(*args: NodeT, ctx: Context) -> str: ...


def into_expr(*extra_names: str) -> Callable[[_IntoExprInputFnProtocol], type[_ExprNode]]:
	"""Convert a function into a simple ExprNode subclass which accepts only a single expr name that being the function's `__name__`.

	Returns:
		A decorator that converts a subclass of `_ExprNode` which implements `accept()` and `resolve()` for the given function.
	"""

	def decorator(f: _IntoExprInputFnProtocol) -> type[_ExprNode]:

		return type(
			f"{f.__name__}__{into_expr.__name__}__ExprNode",
			(_ExprNode,),
			{
				"accept": classmethod(lambda _, name, /: (not f.__name__.startswith("_") and name == f.__name__.lower()) or name in extra_names),
				"resolve": lambda self: f(*self.args, ctx=self.ctx),
			},
		)

	return decorator


class BuiltinNodes__(Scope):
	class Str__(Scope):
		@dc.dataclass(kw_only=True)
		class Concat(_ExprNode):
			"""Eagerly resolve all the arguments and concatenate them into a single string."""

			name: str | None
			"""The name due to which this node was instantiated, this was the `accept()`ed name, it's there if you accept multiple names for the same node class, but want to slightly tweak the behaviour for each of the names.

			Special case when name is None - only ever for a Concat node, it means it was called without node resolution - hardcoded concatenation.
			"""

			@classmethod
			def accept(cls, name: str, /) -> bool:
				return name in {
					cls.__name__.lower(),
					"",
				}

			def resolve(self) -> str:
				return "".join(arg.resolve() for arg in self.args)

		@into_expr("uppercase")
		def Upper(*args: NodeT, ctx: Context) -> str:
			return "".join(arg.resolve() for arg in args).upper()

		@into_expr("lowercase")
		def Lower(*args: NodeT, ctx: Context) -> str:
			return "".join(arg.resolve() for arg in args).lower()

	class Math__(Scope):
		@into_expr("+")
		def Add(*args: NodeT, ctx: Context) -> str:
			return f"{
				functools.reduce(
					lambda x, y: x + y,
					(
						float(arg.resolve())  #
						for arg in args
					),
				):g}"

		@into_expr("-")
		def Sub(*args: NodeT, ctx: Context) -> str:
			return f"{
				functools.reduce(
					lambda x, y: x - y,
					(
						float(arg.resolve())  #
						for arg in args
					),
				):g}"

		@into_expr("*")
		def Mul(*args: NodeT, ctx: Context) -> str:
			return f"{
				functools.reduce(
					lambda x, y: x * y,
					(
						float(arg.resolve())  #
						for arg in args
					),
				):g}"

		@into_expr("/")
		def Div(*args: NodeT, ctx: Context) -> str:
			return f"{
				functools.reduce(
					lambda x, y: x / y,
					(
						float(arg.resolve())  #
						for arg in args
					),
				):g}"

		@into_expr("%")
		def Mod(*args: NodeT, ctx: Context) -> str:
			return f"{
				functools.reduce(
					lambda x, y: x % y,
					(
						float(arg.resolve())  #
						for arg in args
					),
				):g}"

		@into_expr()
		def Pow(*args: NodeT, ctx: Context) -> str:
			return f"{
				functools.reduce(
					lambda x, y: x**y,
					(
						float(arg.resolve())  #
						for arg in args
					),
				):g}"

		@into_expr()
		def Sqrt(*args: NodeT, ctx: Context) -> str:
			(arg,) = args

			return f"{float(arg.resolve()) ** 0.5:g}"
