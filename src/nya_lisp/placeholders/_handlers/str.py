from __future__ import annotations

from ...abc import HandlerDFS
from ...context import EmptyContext


class StrJoinHandler(HandlerDFS[EmptyContext]):
	def handle_dfs(self, name: str, *args: str, ctx: EmptyContext) -> str:
		self._assert_argc(len(args), expect=(1, None))

		joiner, *rest = args

		return joiner.join(rest)


class StrLowerHandler(HandlerDFS[EmptyContext]):
	def handle_dfs(self, name: str, *args: str, ctx: EmptyContext) -> str:
		self._assert_argc(len(args), expect=1)

		arg = args[0]

		return arg.lower()


class StrUpperHandler(HandlerDFS[EmptyContext]):
	def handle_dfs(self, name: str, *args: str, ctx: EmptyContext) -> str:
		self._assert_argc(len(args), expect=1)

		arg = args[0]

		return arg.upper()


class StrTitleHandler(HandlerDFS[EmptyContext]):
	def handle_dfs(self, name: str, *args: str, ctx: EmptyContext) -> str:
		self._assert_argc(len(args), expect=1)

		arg = args[0]

		return arg.title()
