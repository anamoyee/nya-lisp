import abc
import functools
import math
from collections.abc import Iterable

from ...context import EmptyContext
from ...execute import Handler


def assume_floats(strs: Iterable[str]) -> Iterable[float]:
	return (float(s) for s in strs)


class _NumberStringConversionHandlerMixin[ContextT](Handler[ContextT], abc.ABC):
	# todo: move common conversions to Handler class, (also rename them, while still keeping names short: number2s, s2f, s2i, s2f_mass, s2i_mass), also move the below todo to the base class as it still applies.

	# todo: conver to dataclass to make a addable-to constructor in which you include graceful_failed_to_parse_as_number (think of a different name), then change the docstrings.

	def fs(self, strs: Iterable[str], *, eager: bool = True) -> Iterable[float]:
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
		it = (self.f(str_) for str_ in strs)

		if eager:
			it = tuple(it)

		return it

	def f(self, s: str) -> float:
		"""Convert a given string to a number.

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

	def s(self, n: float) -> str:
		"""Convert a giveen number back to a string.

		Returns:
			A string representation of the number, with a decimal point if the number is a float, and without a decimal point if the number is an integer.
		"""
		return f"{n:zg}"


class AddHandler(_NumberStringConversionHandlerMixin[EmptyContext]):
	def handle(self, name: str, *args: str, ctx: EmptyContext) -> str:
		return self.s(sum(self.fs(args)))


class SubHandler(_NumberStringConversionHandlerMixin[EmptyContext]):
	def handle(self, name: str, *args: str, ctx: EmptyContext) -> str:
		if len(args) == 0:
			return self.s(0.0)  # identity

		if len(args) == 1:
			return self.s(-self.f(args[0]))

		return self.s(
			functools.reduce(
				lambda x, y: x - y,
				self.fs(args),
			)
		)


class MulHandler(_NumberStringConversionHandlerMixin[EmptyContext]):
	def handle(self, name: str, *args: str, ctx: EmptyContext) -> str:
		result = math.prod(self.fs(args))

		return self.s(result)


class DivHandler(_NumberStringConversionHandlerMixin[EmptyContext]):
	def handle(self, name: str, *args: str, ctx: EmptyContext) -> str:
		if len(args) == 0:
			return self.s(1.0)  # identity

		if len(args) == 1:
			return self.s(self.f(args[0]))

		return self.s(
			functools.reduce(
				lambda x, y: x / y,
				self.fs(args),
			)
		)


def _float_pow_javascriptlike(x: float, y: float) -> float:
	try:
		return float(x**y)
	except OverflowError:
		# Negative base cases
		if x < 0:
			# If the exponent is a whole number, its parity determines the sign
			if y.is_integer():
				return float("inf") if int(y) % 2 == 0 else float("-inf")

			# Fractional power of a negative number yields a complex number (NaN in standard real-only JS/Python floats)
			return float("nan")

		# Positive base cases
		return float("inf")


class PowHandler(_NumberStringConversionHandlerMixin[EmptyContext]):
	"""For >2 len of input values, applies the power operation from left to right, e.g. 2^3^2 = (2^3)^2 = 64, NOT: ~~2^(3^2) = 512~~."""

	def handle(self, name: str, *args: str, ctx: EmptyContext) -> str:
		if len(args) == 0:
			return self.s(1.0)  # identity

		if len(args) == 1:
			return self.s(self.f(args[0]))

		return self.s(
			functools.reduce(
				_float_pow_javascriptlike,  # applies the power operation from left to right, e.g. 2^3^2 = (2^3)^2 = 64, NOT: ~~2^(3^2) = 512~~
				self.fs(args),
			)
		)


class SqrtHandler(_NumberStringConversionHandlerMixin[EmptyContext]):
	def handle(self, name: str, *args: str, ctx: EmptyContext) -> str:
		self._assert_args_count(len(args), expect=(0, 1))

		if len(args) == 0:
			return self.s(1.0)  # identity

		if len(args) == 1:
			return self.s(math.sqrt(self.f(args[0])))

		msg = "unreachable: should have been caught by _assert_args_count"
		raise AssertionError(msg)
