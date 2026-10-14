# todo: impl random

from __future__ import annotations

import random

from ...abc import HandlerDFS
from ...context import EmptyContext


class RandomHandler(HandlerDFS[EmptyContext]):
	def handle_dfs(self, name: str, *args: str, ctx: EmptyContext) -> str:
		self._assert_argc(len(args), expect=(0, 2))

		if len(args) == 0:
			return str(random.random())

		if len(args) == 1:
			a = self._hh__s2i(*args)

			return str(random.randint(0, a))

		a, b = self._hh__mass_s2i(args)

		return str(random.randint(a, b))
