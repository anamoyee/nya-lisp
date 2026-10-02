from ...context import EmptyContext
from ...execute import Handler


class ChrHandler(Handler[EmptyContext]):
	def handle(self, name: str, *args: str, ctx: EmptyContext) -> str:
		self._assert_args_count(len(args), expect=1)

		arg = args[0]

		try:
			num = int(arg, base=0)
		except ValueError as e:
			msg = f"Failed to convert input string {arg!a} to an integer."
			raise ValueError(msg) from e

		if not (0 <= num <= 0x10FFFF):
			msg = f"Input integer {num} is out of range for 'chr'. Valid range is 0 to 0x10FFFF."
			raise ValueError(msg)

		return chr(num)


class OrdHandler(Handler[EmptyContext]):
	def handle(self, name: str, *args: str, ctx: EmptyContext) -> str:
		self._assert_args_count(len(args), expect=1)

		arg = args[0]

		if len(arg) != 1:
			msg = f"Input string {arg!a} must be a single character for 'ord'."
			raise ValueError(msg)

		return str(ord(arg))
