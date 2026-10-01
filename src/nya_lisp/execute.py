from __future__ import annotations

import typing as t
from collections.abc import Sequence
from typing import TYPE_CHECKING

from .parse_ import Node__Placeholder, Node__Text

if TYPE_CHECKING:
	from .abc import Handler, Matcher
	from .parse_ import Node


if True:  # Errors

	class BaseExecutorError(Exception):
		"""Raised when an error occurs during the execution of a placeholder."""

	class ExecutorNoMatchingHandlerError[ContextT](BaseExecutorError):
		"""Raised when no handler is found for a placeholder during execution."""

		name: str
		args: tuple[str, ...]
		ctx: ContextT

		def __init__(self, name: str, *args: str, ctx: ContextT) -> None:
			self.name = name
			self.args = args
			self.ctx = ctx

			super().__init__(f"No matching handler found for placeholder {name!r} with args {args!r} and context {ctx!r}")

	class ExecutorHandlerRaisedError(BaseExecutorError):
		"""A matched handler's handle() method raised an exception while trying to compute its result."""

		original_exception: BaseException

		def __init__(self, original_exception: BaseException) -> None:
			self.original_exception = original_exception
			super().__init__(f"An error occurred while handling a placeholder: {original_exception!r}")


class Executor[ContextT]:
	def __init__(self, *matchers: Matcher[Handler[ContextT], ContextT]) -> None:
		self.matchers = matchers

	def find_handler(self, name: str, *args: str, ctx: ContextT) -> Handler[ContextT] | None:
		for matcher in self.matchers:
			handler = matcher.match(name, *args, ctx=ctx)
			if handler is not None:
				return handler

		return None

	def construct(self, *implicitly_separated_parts: Node, ctx: ContextT) -> str:
		"""Return a string constructed from the given Nodes, assuming a "".join() is required after executing each Node that needs executing (assume this set of nodes represents a single logical argument)."""

		return "".join(self.execute(part, ctx=ctx) for part in implicitly_separated_parts)

	def execute(
		self,
		source:
		#
		Node
		| Sequence[  # arguments, separated by |
			Sequence[  # same argument, only implicit spliting of nodes which have to be of differing type.
				Node
			],
		],
		*,
		ctx: ContextT,
	) -> str:
		"""Execute the given source and return the resulting string.

		Args:
			source: The source to execute, which can be a `Node` or `Node__Placeholder().args` value.
			ctx: The context to pass to the handlers during execution. You may view the mutation of this context after execution if you assign it to a variable in your scope.

		Returns:
			The resulting string after executing the source with the given context.

		Raises:
			ExecutorNoMatchingHandlerError[ContextT]: If no matching handler is found for a placeholder during execution
			ExecutorHandlerRaisedError: If a matched handler's handle() method raised an exception
		"""  # ruff: ignore[docstring-extraneous-exception]

		match source:
			case Node__Text():
				return source.inner
			case Node__Placeholder():
				source = (
					(
						source,  #
					),
				)

		name_unconstructed, *args_unconstructed = source

		name = self.construct(*name_unconstructed, ctx=ctx)
		args = [self.construct(*arg, ctx=ctx) for arg in args_unconstructed]

		handler = self.find_handler(name, *args, ctx=ctx)

		if handler is None:
			raise ExecutorNoMatchingHandlerError[ContextT](name, *args, ctx=ctx)

		try:
			return handler.handle(name, *args, ctx=ctx)
		except BaseException as e:
			raise ExecutorHandlerRaisedError(e) from e


if True:  # type checking tests:
	if TYPE_CHECKING:  # type checking test 1 (empty TD)

		def __():
			from .abc import Placeholder
			from .parse_ import parse

			class EmptyTD(t.TypedDict):
				pass

			class ReturnHelloPlaceholder(Placeholder[EmptyTD]):
				def match(self, name: str, *_, ctx: EmptyTD) -> t.Self | None:
					match name:
						case "hello":
							return self
						case _:
							return None

				def handle(self, name: str, *args: str, ctx: EmptyTD) -> str:
					return "hi!"

			class ReturnHelloAppContext(t.TypedDict):
				pass

			ctx = ReturnHelloAppContext()

			executor = Executor(
				ReturnHelloPlaceholder(),
			)

			executor.execute(
				parse("Meow meow {hello}").args,
				ctx=ctx,
			)

	if TYPE_CHECKING:  # typing check 2 (non-empty TD)

		def __():
			from .abc import Placeholder
			from .parse_ import parse

			class EmbedContextTD(t.TypedDict):
				embed: dict[str, object]

			class DiscordEmbedPlaceholder(Placeholder[EmbedContextTD]):
				def match(self, name: str, *_, ctx: EmbedContextTD) -> t.Self | None:
					match name:
						case "embed":
							return self
						case _:
							return None

				def handle(self, name: str, *args: str, ctx: EmbedContextTD) -> str:
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
				parse("Meow{embed}").args,
				ctx=ctx,
			)

	if TYPE_CHECKING:  # typing check 3 (intersection of TDs)

		def __():
			from .abc import Placeholder
			from .parse_ import parse

			class EmbedContextTD(t.TypedDict):
				embed: dict[str, object]

			class LoggerContextTD(t.TypedDict):
				log: list[str]

			class DiscordEmbedPlaceholder(Placeholder[EmbedContextTD]):
				def match(self, name: str, *_, ctx: EmbedContextTD) -> t.Self | None:
					match name:
						case "embed":
							return self
						case _:
							return None

				def handle(self, name: str, *args: str, ctx: EmbedContextTD) -> str:
					ctx["embed"] = {
						"title": "Hello",
						"description": "This is a test embed.",
						"color": 0x00FF00,
					}

					return ""

			class LoggerPlaceholder(Placeholder[LoggerContextTD]):
				def match(self, name: str, *_, ctx: LoggerContextTD) -> t.Self | None:
					match name:
						case "log":
							return self
						case _:
							return None

				def handle(self, name: str, *args: str, ctx: LoggerContextTD) -> str:
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
				parse("Meow{embed} and {log}").args,
				ctx=ctx,
			)

	if TYPE_CHECKING:

		def __():
			from .abc import Placeholder
			from .parse_ import parse

			class SillyPlaceholder(Placeholder[int]):
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

			class LoggerPlaceholder(Placeholder[LoggerContextTD]):
				def match(self, name: str, *_, ctx: LoggerContextTD) -> t.Self | None:
					match name:
						case "log":
							return self
						case _:
							return None

				def handle(self, name: str, *args: str, ctx: LoggerContextTD) -> str:
					ctx["log"].append("|".join(args))
					return ""

			class Logger2Placeholder(Placeholder[Logger2ContextTD]):
				def match(self, name: str, *_, ctx: Logger2ContextTD) -> t.Self | None:
					match name:
						case "log2":
							return self
						case _:
							return None

				def handle(self, name: str, *args: str, ctx: Logger2ContextTD) -> str:
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
				parse("Meow meow {silly}").args,
				ctx=MyCtx(log=[]),
			)

	if TYPE_CHECKING:  # cleanup
		del __  # ...of previous type checking tests' scopes, maybe some type checkers are smart enough to infer the attr doesnt exist at the end of the module.
