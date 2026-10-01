import abc
import dataclasses as _dc
import typing as t
from collections.abc import Iterable

from .error import TooManyOrFewPositionalArgumentsInHandlerError


class Matcher[HandlerT, ContextT](abc.ABC):
	@abc.abstractmethod
	def match(self, name: str, *args: str, ctx: ContextT) -> HandlerT | None:
		"""Return a matching handler for placeholder `name`, or `None` if no match here is found."""


@_dc.dataclass(
	frozen=True, slots=True
)  # no fields but a hint for any mixin classes which might want to add e.g. graceful overrides of the mathematical functions, they may add a
class Handler[ContextT](abc.ABC):
	@abc.abstractmethod
	def handle(self, name: str, *args: str, ctx: ContextT) -> str:
		"""Handle and evaluate the placeholder `name` with the given `args` and Context `ctx`, returning the evaluated string result."""

	def into_matcher(self, name: str, *aliases: str) -> Matcher[t.Self, ContextT]:
		"""Return a matcher that matches the given `name` and `aliases` to this handler.

		Args:
			name: The primary name of the placeholder to match. (for now there's no distinction between a primary name and an alias, but handlers or matchers may decide to do different things on one given name, but they dont know which is primary)
			aliases: Additional names that should also match this handler.

		Raises:
			ValueError: If any of the names have leading or trailing whitespace, which is not supported in `into_matcher()`, if you REALLY need leading or trailing whitespace, write a verbose matcher impl.
		"""

		if (name, *aliases) != tuple({name, *aliases}):
			msg = f"Duplicate placeholder names found in {name!r} and {aliases!r}. Each name must be unique. Edit the callsite, this meant to be more of a static helper, if you're using this dynamically, wrap your args in `*{{...}}`"
			raise ValueError(msg)

		names = {name, *aliases}

		for name_ in names:
			if name_.strip() != name_:
				msg = f"Placeholder name {name_!r} has leading or trailing whitespace, which is not supported in `into_matcher()`, if you REALLY need leading or trailing whitespace, write a verbose matcher impl."
				raise ValueError(msg)

		handler = self

		_Matcher = type(
			f"{self.__class__.__name__}AutoMatcher",
			(Matcher,),
			{
				"match": lambda self, name, *args, ctx: handler if name.lower() in names else None,  # ruff: ignore[unused-lambda-argument]
			},
		)

		return _Matcher()

	def _assert_args_count[T](self, len_args: int, *, expect: int | tuple[int | None, int] | tuple[int, int | None]) -> None:
		if isinstance(expect, int):
			expect = (expect, expect)

		if expect[0] is not None and len_args < expect[0]:
			raise TooManyOrFewPositionalArgumentsInHandlerError(len_args, expect)
		if expect[1] is not None and len_args > expect[1]:
			raise TooManyOrFewPositionalArgumentsInHandlerError(len_args, expect)

	if True:  # _hh__* (handler helpers)

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
			try:
				return float(s)
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

			Returns:
				A string representation of the number, with a decimal point if the number is a float, and without a decimal point if the number is an integer.
			"""
			return f"{n:zg}"


class Placeholder[ContextT](Matcher[Handler[ContextT], ContextT], Handler[ContextT]):
	"""A placeholder is a matcher and handler for a specific placeholder name. This is only a shorthand, functions as a convenience for the implementor. The mechanism actually looks for a `Matcher[Handler[...], ...]`."""
