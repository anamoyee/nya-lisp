import dataclasses as _dc
import operator


class BaseNyaLispError(Exception):
	"""A base class for all errors raised by the `nya-lisp` library."""


if True:  # ParseError

	class ParseError(BaseNyaLispError):
		"""Raised when a parsing error occurs in the input string, when parsing as a `nya-lisp` syntax tree."""

	class UnexpectedCloseError(ParseError):
		"""Raised when an unexpected closing brace is encountered during parsing."""

	class UnclosedOpenError(ParseError):
		"""Raised when an opening brace is not closed during parsing."""

	class RootLevelContainsArgumentSeparatorError(ParseError):
		"""Raised when Parser.parse_one() is called with an input that looks like an innerds of a placeholder, e.g. "arg1|arg2", whereas a trivially joinable (`"".join(...)`) len=1 args was expected in this method."""


if True:  # ExecuteError

	class ExecuteError(BaseNyaLispError):
		"""Raised when an error occurs during the execution of a `nya-lisp` placeholder."""

	class ExecutorNoMatchingHandlerError[ContextT](ExecuteError):
		"""Raised when no handler is found for the given name and context during execution."""

		name: str
		ctx: ContextT

		def __init__(self, name: str, ctx: ContextT) -> None:
			self.name = name
			self.ctx = ctx

			super().__init__(f"No matching handler found for placeholder {name!r} in the given context.")

	class ExecutorHandlerRaisedError(ExecuteError):
		"""A matched handler's handle() method raised an exception while trying to compute its result."""

		original_exception: BaseException

		def __init__(self, original_exception: BaseException) -> None:
			self.original_exception = original_exception
			super().__init__(f"An error occurred while handling a placeholder: {original_exception!r}")


if True:  # HandlerError

	class HandlerError(BaseNyaLispError):
		"""A base class for all errors raised when an expected error occurs in a `nya-lisp` handler, e.g. too many arguments (as opposed to an unexpected error like an AttributeError caused by a bug in the code)."""

	@_dc.dataclass(frozen=True, slots=True)
	class TooManyOrFewPositionalArgumentsInHandlerError(HandlerError):
		"""Raised when a handler receives more or fewer positional arguments than it supports."""

		actual: int
		"""Represents the actual number of arguments received by the handler."""

		expected: tuple[int | None, int] | tuple[int, int | None] | None
		"""Represents an inclusive range of the expected number of arguments for the handler, if it's not possible to derive a specific range of arguments count, set this to an untupled None, None in tuple means unbounded on this side."""

		def message_to_user(self) -> str:
			assert self.expected != (None, None), "At least one side of the expected range must be bounded (not None)."

			if self.expected is None:
				return f"received {self.actual} positional arguments, which is not a valid amount"

			if operator.eq(*self.expected):
				assert self.expected[0] is not None
				return f"received {self.actual} positional arguments (too {"few" if self.actual < self.expected[0] else "many"}), but expected exactly {self.expected[0]}"

			if self.expected[0] is not None and self.actual < self.expected[0]:
				return f"received {self.actual} positional arguments, but expected at least {self.expected[0]}"

			if self.expected[1] is not None and self.actual > self.expected[1]:
				return f"received {self.actual} positional arguments, but expected at most {self.expected[1]}"

			return f"received {self.actual} positional arguments, which is not a valid amount"
