from ...context import EmptyContext
from ...execute import Handler


class StrJoinHandler(Handler[EmptyContext]):
	def handle(self, name: str, *args: str, ctx: EmptyContext) -> str:
		self._assert_args_count(len(args), expect=(1, None))

		joiner, *rest = args

		return joiner.join(rest)


class StrLowerHandler(Handler[EmptyContext]):
	def handle(self, name: str, *args: str, ctx: EmptyContext) -> str:
		self._assert_args_count(len(args), expect=1)

		arg = args[0]

		return arg.lower()


class StrUpperHandler(Handler[EmptyContext]):
	def handle(self, name: str, *args: str, ctx: EmptyContext) -> str:
		self._assert_args_count(len(args), expect=1)

		arg = args[0]

		return arg.upper()


class StrTitleHandler(Handler[EmptyContext]):
	def handle(self, name: str, *args: str, ctx: EmptyContext) -> str:
		self._assert_args_count(len(args), expect=1)

		arg = args[0]

		return arg.title()
