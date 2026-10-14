from __future__ import annotations

import abc
import dataclasses as _dc
import typing as t
from collections.abc import Iterable

from . import error

if t.TYPE_CHECKING:
	from .execute import Executor
	from .parse_ import Node


class Matcher[HandlerT: HandlerBFS, ContextT](abc.ABC):
	@abc.abstractmethod
	def match(self, name: str, *, ctx: ContextT) -> HandlerT | None:
		"""Return a matching handler for placeholder `name`, or `None` if no match is found."""


if True:  # Handler?FS

	@_dc.dataclass(frozen=True, slots=True, kw_only=True)
	class HandlerBFS[ContextT](abc.ABC):
		"""Base class for all handlers that operate in a breadth-first search/resolve (BFS) manner."""

		ARGC: t.ClassVar[int | range | None] = None
		"""Validate against a supported number or range of arguments.

		This performs a check on the length of args (i.e. does not take name, the first "argument" into account)

		Supported types:
		- `None`: No validation is performed (any number of arguments 0..∞ is considered valid).
		- `int`: The exact number of arguments expected.
		- `range`: Check whether the length of the arguments is within the given range.
		"""

		class _init_subclass_TD(t.TypedDict):
			ARGC: t.NotRequired[int | range | None]

		def __init_subclass__(
			cls,
			**kwargs: t.Unpack[_init_subclass_TD],
		) -> None:
			kwargs.setdefault("ARGC", cls.ARGC)

			match kwargs:
				case {
					"ARGC": ARGC,
					**rest,
				}:
					cls.ARGC = ARGC
					# NOTE: Cannot use super() here — @dataclass(slots=True) replaces the class
					# object after the class body runs, leaving the __class__ closure cell stale.
					# super() expands to super(__class__, cls) where __class__ is the original
					# pre-replacement class, so issubclass(cls, __class__) is False and it raises.
					# Fix: find the live declaring class from cls.__mro__ instead.
					declaring = next(c for c in cls.__mro__ if "__init_subclass__" in c.__dict__ and c is not cls)
					return super(declaring, cls).__init_subclass__(**rest)

			msg = f"Missing required keyword arguments in {cls.__name__} definition call (`__init_subclass__`): {kwargs!r}"
			raise TypeError(msg)

		def validate_argc(self, argc: int) -> bool:
			"""Return True if argc conforms to the `cls.ARGC` supported range of arguments, False otherwise.

			Args:
				argc: The actual number of arguments passed to the handler, should always be len(args) unless you're doing something sneaky.
			"""

			match self.ARGC:
				case None:
					return True  # assume manual validation in handler or all possible sets of arguments are valid
				case int() as exact:
					return argc == exact
				case range() as range_:
					return argc in range_
				case never:
					t.assert_never(never)

		def _handle_bfs(self, name: str, *args: tuple[Node, ...], ctx: ContextT, executor: Executor[t.Any]) -> str:
			"""A raw implementation of handle_bfs which calls the appropriate bfs validators and forwards the call to that function.

			This is there so that implementors of the handle_bfs method don't have to call super().handle_bfs() at all times (and possibly forget that which leads to missing validation)


			Args:
				name: The name of the placeholder to handle.
				args: The arguments to pass to the handler (unexecuted).
				ctx: The context to use during handling.
				executor: The executor to use for evaluating the placeholder.

			Returns:
				The resulting string after handling the placeholder.

			Raises:
				TooManyOrFewPositionalArgumentsInHandlerError: When a validator fails the validation of argument count.
			"""

			if self.validate_argc(argc := len(args)):
				assert self.ARGC is not None
				raise error.TooManyOrFewPositionalArgumentsInHandlerError(argc, self.ARGC)

			return self.handle_bfs(name, *args, ctx=ctx, executor=executor)

		@abc.abstractmethod
		def handle_bfs(
			self,
			name: str,
			*args: tuple[Node, ...],
			ctx: ContextT,
			executor: Executor[
				t.Any  # <-- Any is fine here, since executor is only ever passed by another Executor.execute() call, and the root call verifies the typing. I dont think there's a way to represent the bidirectionality of the context typing...
			],
		) -> str:
			"""Handle and evaluate the placeholder `name` with the given `args` and Context `ctx`, returning the evaluated string result.

			Args:
				name: The name of the placeholder to handle.
				args: The arguments to pass to the handler (unexecuted).
				ctx: The context to use during handling.
				executor: The executor to use for evaluating the placeholder.

			Returns:
				The resulting string after handling the placeholder.
			"""

		if True:  # _hh__* (handler helpers)

			def _hh__execute_args(self, *args: tuple[Node, ...], ctx: ContextT, executor: Executor[t.Any]) -> tuple[str, ...]:
				return tuple(self._hh__execute_arg(arg, ctx=ctx, executor=executor) for arg in args)

			def _hh__execute_arg(self, arg: tuple[Node, ...], *, ctx: ContextT, executor: Executor[t.Any]) -> str:
				return "".join(executor.execute(arg_part, ctx=ctx) for arg_part in arg)

			if True:  # _hh__*f*

				def _hh__mass_s2f(self, strs: Iterable[str], *, eager: bool = True) -> Iterable[float]:
					"""Convert a given iterable of strings to an iterable of numbers.

					### ❗ The `_NumberStringConversionHandlerMixin_` class may be subclassed to change the behavior of this method then mixed with same handler to create a new handler, e.g. for graceful handling of invalid input strings.

					Args:
						strs: An iterable of strings to convert to numbers.
						eager: If `True`, the returned iterable will be a tuple, otherwise it will be a generator.

					Returns:
						An iterable of numbers converted from the given strings.

					Raises:
						ValueError: If any of the strings cannot be converted to a number.
					"""  # ruff: ignore[docstring-extraneous-exception]
					it = (self._hh__s2f(str_) for str_ in strs)

					if eager:
						it = tuple(it)

					return it

				def _hh__s2f(self, s: str) -> float:
					"""Convert a given string to a number (float).

					### ❗ The `_NumberStringConversionHandlerMixin_` class may be subclassed to change the behavior of this method then mixed with same handler to create a new handler, e.g. for graceful handling of invalid input strings.

					Returns:
						A float instance constructed from the string.

					Raises:
						ValueError: If the string cannot be converted to a number.
					"""

					def normalize_leading_pluses_and_minuses(s: str) -> str:
						if not s:
							return s

						minus = False

						while (ch := s[0]) in {"+", "-"}:
							if ch == "-":
								minus = not minus

							s = s[1:]

						return f"{("-" if minus else "")}{s}"

					try:
						return float(normalize_leading_pluses_and_minuses(s))
					except ValueError as e:
						placeholder_name = (
							self.__class__.__name__  #
							.removesuffix("Placeholder")
							.removesuffix("Handler")
							.lower()
						)
						msg = f"Failed to convert input string {s!r} to a number, for the needs of a {placeholder_name!r} placeholder."
						raise ValueError(msg) from e

				def _hh__f2s(self, n: float) -> str:
					"""Convert a giveen number back to a string.
					### ❗ The `_NumberStringConversionHandlerMixin_` class may be subclassed to change the behavior of this method then mixed with same handler to create a new handler, e.g. for graceful handling of invalid input strings.

					Returns:
						A string representation of the number, with a decimal point if the number is a float, and without a decimal point if the number is an integer.
					"""
					return f"{n:zg}"

			if True:  # _hh__*i*

				def _hh__mass_s2i(self, strs: Iterable[str], *, eager: bool = True) -> Iterable[int]:
					"""Convert a given iterable of strings to an iterable of integers.

					### ❗ The `_NumberStringConversionHandlerMixin_` class may be subclassed to change the behavior of this method then mixed with same handler to create a new handler, e.g. for graceful handling of invalid input strings.

					Args:
						strs: An iterable of strings to convert to integers.
						eager: If `True`, the returned iterable will be a tuple, otherwise it will be a generator.

					Returns:
						An iterable of integers converted from the given strings.

					Raises:
						ValueError: If any of the strings cannot be converted to an integer.
					"""  # ruff: ignore[docstring-extraneous-exception]
					it = (self._hh__s2i(str_) for str_ in strs)

					if eager:
						it = tuple(it)

					return it

				def _hh__s2i(self, s: str) -> int:
					"""Convert a given string to an integer.

					Returns:
						An integer instance constructed from the string.

					Raises:
						ValueError: If the string cannot be converted to an integer.
					"""
					try:
						return int(s, base=0)
					except ValueError as e:
						placeholder_name = (
							self.__class__.__name__  #
							.removesuffix("Placeholder")
							.removesuffix("Handler")
							.lower()
						)
						msg = f"Failed to convert input string {s!r} to an integer, for the needs of a {placeholder_name!r} placeholder."
						raise ValueError(msg) from e

				def _hh__i2s(self, n: int) -> str:
					"""Convert a given integer back to a string.

					Returns:
						A string representation of the integer.
					"""
					return str(n)

	@_dc.dataclass(frozen=True, slots=True, kw_only=True)
	class HandlerDFS[ContextT](HandlerBFS[ContextT], abc.ABC):
		"""Base class for all handlers that operate in a depth-first search/resolve (DFS) manner."""

		def handle_bfs(
			self,
			name: str,
			*args: tuple[Node, ...],
			ctx: ContextT,
			executor: Executor[t.Any],
		) -> str:
			"""Handle and evaluate the placeholder `name` with the given `args` and Context `ctx`, returning the evaluated string result.

			Args:
				name: The name of the placeholder to handle.
				args: The arguments to pass to the handler (unexecuted).
				ctx: The context to use during handling.
				executor: The executor to use for evaluating the placeholder.

			Returns:
				The resulting string after handling the placeholder.
			"""
			return self.handle_dfs(name, *self._hh__execute_args(*args, ctx=ctx, executor=executor), ctx=ctx)

		@abc.abstractmethod
		def handle_dfs(
			self,
			name: str,
			*args: str,
			ctx: ContextT,
		) -> str:
			"""Handle and evaluate the placeholder `name` with the given `args` and Context `ctx`, returning the evaluated string result.

			Args:
				name: The name of the placeholder to handle.
				args: The arguments to pass to the handler (pre-executed).
				ctx: The context to use during handling.

			Returns:
				The resulting string after handling the placeholder.
			"""


if True:  # utility mixins

	class IntoMatcher__FromHandler_ByNames[HandlerT: HandlerBFS, ContextT](Matcher[HandlerBFS[ContextT], ContextT], HandlerBFS[ContextT]):
		MATCH_NAMES: t.ClassVar[set[str]] = set()
		MATCH_CASEFOLD: t.ClassVar[bool] = True
		# todo: Add tests for casefold, kinda important because i almost screwed up the casefolding, but caught myself and fixed it now

		class _init_subclass_TD(HandlerBFS._init_subclass_TD):
			# all have to be NotRequired because otherwise all subclasses would have to explicitly re-define them with the same value which would be annoying...
			MATCH_NAMES: t.NotRequired[set[str]]
			MATCH_CASEFOLD: t.NotRequired[bool]

		def __init_subclass__(
			cls,
			**kwargs: t.Unpack[_init_subclass_TD],
		) -> None:
			kwargs.setdefault("MATCH_CASEFOLD", cls.MATCH_CASEFOLD)
			kwargs.setdefault("MATCH_NAMES", cls.MATCH_NAMES)

			if kwargs["MATCH_NAMES"] == set():
				msg = f"MATCH_NAMES must be a non-empty set of strings in {cls.__name__!r} definition call (`__init_subclass__`)"
				raise ValueError(msg)

			match kwargs:
				case {
					"ARGC": ARGC,
					"MATCH_NAMES": MATCH_NAMES,
					"MATCH_CASEFOLD": MATCH_CASEFOLD,
					**rest,
				}:
					cls.MATCH_CASEFOLD = MATCH_CASEFOLD
					cls.MATCH_NAMES = MATCH_NAMES
					# NOTE: Same super() / @dataclass(slots=True) stale __class__ issue as in
					# HandlerBFS.__init_subclass__ — use live MRO lookup instead.
					declaring = next(c for c in cls.__mro__ if "__init_subclass__" in c.__dict__ and c is not cls)
					return super(declaring, cls).__init_subclass__(ARGC=ARGC, **rest)

			msg = f"Missing required keyword arguments in {cls.__name__} definition call (`__init_subclass__`): {kwargs!r}"
			raise TypeError(msg)

		def match(self, name: str, *, ctx: ContextT) -> HandlerBFS[ContextT] | None:
			if self.MATCH_CASEFOLD:  # ruff: ignore[if-else-block-instead-of-if-exp]
				matched = name.casefold() in {n.casefold() for n in self.MATCH_NAMES}
			else:
				matched = name in self.MATCH_NAMES

			if matched:
				return self

			return None


if True:  # Placeholder

	class PlaceholderBFS[ContextT](HandlerBFS[ContextT], Matcher[HandlerBFS[ContextT], ContextT]):
		"""A placeholder is a matcher and handler in one type. This is only a shorthand, functions as a convenience for the implementor. The mechanism actually looks for a `Matcher[Handler[...], ...]`."""

	class PlaceholderDFS[ContextT](HandlerDFS[ContextT], Matcher[HandlerDFS[ContextT], ContextT]):
		"""A placeholder is a matcher and handler in one type. This is only a shorthand, functions as a convenience for the implementor. The mechanism actually looks for a `Matcher[Handler[...], ...]`."""
