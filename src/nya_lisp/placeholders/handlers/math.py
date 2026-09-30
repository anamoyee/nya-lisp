import abc

from ...execute import EmptyTD, Handler


class _NumberStringConversionHandlerMixin[ContextT](Handler[ContextT], abc.ABC):
	def try_str2float(self, s: str) -> float:
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

	def float2str(self, n: float) -> str:
		return f"{n:g}"


class AddHandler(_NumberStringConversionHandlerMixin[EmptyTD]):
	def handle(self, name: str, *args: str, ctx: EmptyTD) -> str:
		return self.float2str(
			sum(
				self.try_str2float(arg)
				# propagate error of the impl of try_str2float() to the caller,
				# if this class is subclassed, and the try_str2float() method
				# is overriden to provide a safer impl, e.g. returning 0 on wrong
				#  input, it will be used.
				for arg in args
			)
		)


class SubHandler(_NumberStringConversionHandlerMixin[EmptyTD]):
	def handle(self, name: str, *args: str, ctx: EmptyTD) -> str:
		if len(args) == 0:
			return self.float2str(0.0)

		if len(args) == 1:
			return self.float2str(-self.try_str2float(args[0]))

		arg1, *rest = args

		return self.float2str(
			self.try_str2float(arg1)
			- sum(
				self.try_str2float(arg)
				# propagate error of the impl of try_str2float() to the caller,
				# if this class is subclassed, and the try_str2float() method
				# is overriden to provide a safer impl, e.g. returning 0 on wrong
				#  input, it will be used.
				for arg in rest
			)
		)
