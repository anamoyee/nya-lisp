from ...abc import HandlerDFS, _Matcher__FromHandlerByNames
from ...context import EmptyContext


class ChrHandler(HandlerDFS[EmptyContext], _Matcher__FromHandlerByNames):
	def handle_dfs(self, name: str, *args: str, ctx: EmptyContext) -> str:
		self._assert_argc(len(args), expect=1)

		num = self._hh__s2i(*args)

		if not (0 <= num <= 0x10FFFF):
			msg = f"Input integer {num} is out of range for 'chr'. Valid range is 0 to 0x10FFFF."
			raise ValueError(msg)

		return chr(num)


class OrdHandler(HandlerDFS[EmptyContext]):
	def handle_dfs(self, name: str, *args: str, ctx: EmptyContext) -> str:
		self._assert_argc(len(args), expect=1)

		arg = args[0]

		if len(arg) != 1:
			msg = f"Input string {arg!a} must be a single character for 'ord'."
			raise ValueError(msg)

		return str(ord(arg))
