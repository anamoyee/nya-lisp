import dataclasses as _dc

if True:  # ParseError

	class ParseError(ValueError):
		"""Raised when a parsing error occurs in the input string."""


if True:  # HandlerError

	class HandlerError(Exception):
		"""A base class for all errors raised when an expected error occurs in a `nya-lisp` handler, e.g. too many arguments (as opposed to an unexpected error like an AttributeError caused by a bug in the code)."""

	@_dc.dataclass(frozen=True, slots=True)
	class TooManyOrFewPositionalArgumentsInHandlerError(HandlerError):
		"""Raised when a handler receives more or fewer positional arguments than it supports."""

		actual: int
		"""Represents the actual number of arguments received by the handler."""

		expected: tuple[int | None, int] | tuple[int, int | None] | None
		"""Represents an inclusive range of the expected number of arguments for the handler, if it's not possible to derive a specific range of arguments count, set this to an untupled None, None in tuple means unbounded on this side."""

		def message_to_user(self) -> str:
			if self.expected is None:
				return f"received {self.actual} positional arguments, which is not a valid amount"

			if self.expected[0] is not None and self.actual < self.expected[0]:
				return f"received {self.actual} positional arguments, but expected at least {self.expected[0]}"
			if self.expected[1] is not None and self.actual > self.expected[1]:
				return f"received {self.actual} positional arguments, but expected at most {self.expected[1]}"

			return f"received {self.actual} positional arguments, which is not a valid amount"
