from __future__ import annotations

import typing as t
from collections.abc import Sequence
from typing import TYPE_CHECKING

from .parse_ import Node__Placeholder, Node__Text

if TYPE_CHECKING:
	from .abc import HandlerBFS, Matcher
	from .parse_ import Node

from .error import ExecutorHandlerRaisedError, ExecutorNoMatchingHandlerError


class Executor[ContextT]:
	def __init__(
		self,
		*matchers: Matcher[HandlerBFS[ContextT], ContextT],
	) -> None:
		self.matchers = matchers

	def __call__(self, source: Node | Sequence[Node], *, ctx: ContextT) -> str:
		return self.execute(source, ctx=ctx)

	def find_handler(self, name: str, *, ctx: ContextT) -> HandlerBFS[ContextT] | None:
		for matcher in self.matchers:
			handler = matcher.match(name, ctx=ctx)
			if handler is not None:
				return handler

		return None

	def construct(self, *arg_parts: Node, ctx: ContextT) -> str:
		"""Return a string constructed from the given Nodes, assuming a "".join() is required after executing each Node that needs executing (assume this set of nodes represents a single logical argument)."""

		return "".join(self.execute(arg_part_node, ctx=ctx) for arg_part_node in arg_parts)

	def _execute_placeholder(self, node: Node__Placeholder, *, ctx: ContextT) -> str:
		name_parts, *args_parts = node.args

		name = self.construct(*name_parts, ctx=ctx)

		handler = self.find_handler(name, ctx=ctx)

		if handler is None:
			raise ExecutorNoMatchingHandlerError(name, ctx=ctx)

		try:
			return handler.handle_bfs(name, *args_parts, ctx=ctx, executor=self)
		except Exception as e:
			raise ExecutorHandlerRaisedError(e) from e

	def execute(
		self,
		source: (
			Node  #
			| Sequence[Node,]  # shorthand for "".join(.execute(x) for x in sequence_of_nodes
		),
		*,
		ctx: ContextT,
	) -> str:
		"""Execute the given source and return the resulting string.

		Args:
			source: The source to execute, which can be a `Node` or a sequence of `Node` objects (a `Sequence[Node]` input is a shorthand for `"".join(.execute(x) for x in sequence_of_nodes)`).
			ctx: The context to pass to the handlers during execution. You may view the mutation of this context after execution if you assign it to a variable in your scope.

		Returns:
			The resulting string after executing the source with the given context.

		Raises:
			ExecutorNoMatchingHandlerError[ContextT]: If no matching handler is found for a placeholder during execution
			ExecutorHandlerRaisedError: If a matched handler's handle() method raised an exception
		"""  # ruff: ignore[docstring-extraneous-exception]

		if isinstance(source, Node__Text):
			return source.inner

		if isinstance(source, Node__Placeholder):
			return self._execute_placeholder(source, ctx=ctx)

		return "".join(self.execute(node, ctx=ctx) for node in source)


if True:  # type checking tests:
	if TYPE_CHECKING:  # type checking test 1 (empty TD)

		def __():
			from .abc import PlaceholderDFS
			from .parse_ import parse

			class EmptyTD(t.TypedDict):
				pass

			class ReturnHelloPlaceholder(PlaceholderDFS[EmptyTD]):
				def match(self, name: str, ctx: EmptyTD) -> t.Self | None:
					match name:
						case "hello":
							return self
						case _:
							return None

				def handle_dfs(self, name: str, *args: str, ctx: EmptyTD) -> str:
					return "hi!"

			class ReturnHelloAppContext(t.TypedDict):
				pass

			ctx = ReturnHelloAppContext()

			executor = Executor(
				ReturnHelloPlaceholder(),
			)

			executor.execute(
				parse("Meow meow {hello}"),
				ctx=ctx,
			)

	if TYPE_CHECKING:  # typing check 2 (non-empty TD)

		def __():
			from .abc import PlaceholderDFS
			from .parse_ import parse

			class EmbedContextTD(t.TypedDict):
				embed: dict[str, object]

			class DiscordEmbedPlaceholder(PlaceholderDFS[EmbedContextTD]):
				def match(self, name: str, *_, ctx: EmbedContextTD) -> t.Self | None:
					match name:
						case "embed":
							return self
						case _:
							return None

				def handle_dfs(self, name: str, *args: str, ctx: EmbedContextTD) -> str:
					ctx["embed"] = {
						"title": "Hello",
						"description": "This is a test embed.",
						"color": 0x00FF00,
					}

					return ""

			class DiscordEmbedAppContext(EmbedContextTD):
				pass

			ctx = DiscordEmbedAppContext(embed={})

			executor = Executor(
				DiscordEmbedPlaceholder(),
			)

			executor.execute(
				parse("Meow{embed}"),
				ctx=ctx,
			)

	if TYPE_CHECKING:  # typing check 3 (intersection of TDs)

		def __():
			from .abc import PlaceholderDFS
			from .parse_ import parse

			class EmbedContextTD(t.TypedDict):
				embed: dict[str, object]

			class LoggerContextTD(t.TypedDict):
				log: list[str]

			class DiscordEmbedPlaceholder(PlaceholderDFS[EmbedContextTD]):
				def match(self, name: str, ctx: EmbedContextTD) -> t.Self | None:
					match name:
						case "embed":
							return self
						case _:
							return None

				def handle_dfs(self, name: str, *args: str, ctx: EmbedContextTD) -> str:
					ctx["embed"] = {
						"title": "Hello",
						"description": "This is a test embed.",
						"color": 0x00FF00,
					}

					return ""

			class LoggerPlaceholder(PlaceholderDFS[LoggerContextTD]):
				def match(self, name: str, ctx: LoggerContextTD) -> t.Self | None:
					match name:
						case "log":
							return self
						case _:
							return None

				def handle_dfs(self, name: str, *args: str, ctx: LoggerContextTD) -> str:
					ctx["log"].append("|".join(args))
					return ""

			class DiscordEmbedWithLoggerAppContext(EmbedContextTD, LoggerContextTD):
				pass

			ctx = DiscordEmbedWithLoggerAppContext(
				embed={},
				log=[],
			)

			executor = Executor(
				DiscordEmbedPlaceholder(),
				LoggerPlaceholder(),
			)

			executor.execute(
				parse("Meow{embed} and {log}"),
				ctx=ctx,
			)

	if TYPE_CHECKING:

		def __():
			from .abc import PlaceholderDFS
			from .parse_ import parse

			class SillyPlaceholder(PlaceholderDFS[int]):
				def match(self, name: str, *_, ctx: int) -> t.Self | None:
					match name:
						case "silly":
							return self
						case _:
							return None

				def handle(self, name: str, *args: str, ctx: int) -> str:
					return f"ctx is {ctx}"

			class LoggerContextTD(t.TypedDict):
				log: list[str]

			class Logger2ContextTD(t.TypedDict):
				log: str

			class LoggerPlaceholder(PlaceholderDFS[LoggerContextTD]):
				def match(self, name: str, ctx: LoggerContextTD) -> t.Self | None:
					match name:
						case "log":
							return self
						case _:
							return None

				def handle_dfs(self, name: str, *args: str, ctx: LoggerContextTD) -> str:
					ctx["log"].append("|".join(args))
					return ""

			class Logger2Placeholder(PlaceholderDFS[Logger2ContextTD]):
				def match(self, name: str, ctx: Logger2ContextTD) -> t.Self | None:
					match name:
						case "log2":
							return self
						case _:
							return None

				def handle_dfs(self, name: str, *args: str, ctx: Logger2ContextTD) -> str:
					ctx["log"] += "|".join(args)
					return ""

			class MyCtx(
				LoggerContextTD,
				# Logger2ContextTD, # error expected
			):
				pass

			executor: Executor[MyCtx] = Executor(
				LoggerPlaceholder(),
				# Logger2Placeholder(), # error expected
			)

			executor.execute(
				parse("Meow meow {silly}"),
				ctx=MyCtx(log=[]),
			)

	if TYPE_CHECKING:  # cleanup
		del __  # ...of previous type checking tests' scopes, maybe some type checkers are smart enough to infer the attr doesnt exist at the end of the module.
