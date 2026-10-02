import functools
import math
from collections.abc import Iterable

from ...context import EmptyContext
from ...execute import Handler


def assume_floats(strs: Iterable[str]) -> Iterable[float]:
	return (float(s) for s in strs)


class AddHandler(Handler[EmptyContext]):
	def handle(self, name: str, *args: str, ctx: EmptyContext) -> str:
		return self._hh__f2s(sum(self._hh__mass_s2f(args)))


class SubHandler(Handler[EmptyContext]):
	def handle(self, name: str, *args: str, ctx: EmptyContext) -> str:
		if len(args) == 0:
			return self._hh__f2s(0.0)  # identity

		if len(args) == 1:
			return self._hh__f2s(-self._hh__s2f(args[0]))

		return self._hh__f2s(
			functools.reduce(
				lambda x, y: x - y,
				self._hh__mass_s2f(args),
			)
		)


class MulHandler(Handler[EmptyContext]):
	def handle(self, name: str, *args: str, ctx: EmptyContext) -> str:
		result = math.prod(self._hh__mass_s2f(args))

		return self._hh__f2s(result)


class TrueDivHandler(Handler[EmptyContext]):
	def handle(self, name: str, *args: str, ctx: EmptyContext) -> str:
		if len(args) == 0:
			return self._hh__f2s(1.0)  # identity

		if len(args) == 1:
			return self._hh__f2s(self._hh__s2f(args[0]))

		return self._hh__f2s(
			functools.reduce(
				lambda x, y: x / y,
				self._hh__mass_s2f(args),
			)
		)


class FloorDivHandler(Handler[EmptyContext]):
	def handle(self, name: str, *args: str, ctx: EmptyContext) -> str:
		if len(args) == 0:
			return self._hh__f2s(1.0)  # identity

		if len(args) == 1:
			return self._hh__f2s(self._hh__s2f(args[0]))

		return self._hh__f2s(
			functools.reduce(
				lambda x, y: x // y,
				self._hh__mass_s2f(args),
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


class PowHandler(Handler[EmptyContext]):
	"""For >2 len of input values, applies the power operation from left to right, e.g. 2^3^2 = (2^3)^2 = 64, NOT: ~~2^(3^2) = 512~~."""

	def handle(self, name: str, *args: str, ctx: EmptyContext) -> str:
		if len(args) == 0:
			return self._hh__f2s(1.0)  # identity

		if len(args) == 1:
			return self._hh__f2s(self._hh__s2f(args[0]))

		return self._hh__f2s(
			functools.reduce(
				_float_pow_javascriptlike,  # applies the power operation from left to right, e.g. 2^3^2 = (2^3)^2 = 64, NOT: ~~2^(3^2) = 512~~
				self._hh__mass_s2f(args),
			)
		)


class SqrtHandler(Handler[EmptyContext]):
	def handle(self, name: str, *args: str, ctx: EmptyContext) -> str:
		self._assert_args_count(len(args), expect=(0, 1))

		if len(args) == 0:
			return self._hh__f2s(1.0)  # identity

		if len(args) == 1:
			return self._hh__f2s(math.sqrt(self._hh__s2f(args[0])))

		msg = "unreachable: should have been caught by _assert_args_count"
		raise AssertionError(msg)
