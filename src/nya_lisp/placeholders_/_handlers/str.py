from __future__ import annotations

import typing as t

from ...abc import HandlerDFS, PlaceholderBFS
from ...context import EmptyContext
from ...parse_ import ParserMetaContext

if t.TYPE_CHECKING:
	from ...execute import Executor
	from ...parse_ import Node


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


class QuotePlaceholder(PlaceholderBFS[ParserMetaContext]):  # todo: write tests of does this work
	"""This is one of those magic placeholders which's idea is that it watches closely the name of the placeholder in its matcher, and if any placeholder expression starts with a `"` or `'` it captures it and returns the literal value of the innerds of it (without evaluating sub-placeholders). Also makes sure the last character is a proper closing quote, and strips off the two quotes (works simillar to unix's `/bin/[` in that regard of caring about the closing quote even though it could've worked without it ever being there as the closing brace would be enough to determine the end of the placeholder <-- tbh might switch to this behaviour where the ending quote is not expected to differentiate this from normal strings, as escaping here is not a thing, e.g. you can do `{'''}` and it means  same as python's `"'"`, because it ever looks for `{'` and `'}`, so the middle `'` is perfectly fine parsed as regular text. Perhaps a `{'quo'te}` placeholder would be less confusing than `{'quo'te'}` as in the former it is really obvious that the parsing stops at `}` and not at `'`?)."""

	Context = ParserMetaContext

	def handle_bfs(
		self,
		name: str,
		*args: tuple[Node, ...],
		ctx: ParserMetaContext,
		executor: Executor[t.Any],
	) -> str:
		# fmt: off
		rest = (
			part.unparse(ctx)  #
			for arg_parts in args
				for part in arg_parts
		)
		# fmt: on

		contents = ctx["meta::parse_sep"].join((
			name,
			*rest,
		))

		if len(contents) < 2 or contents[0] != contents[-1]:
			msg = "Unmatched quote."
			raise ValueError(msg)

		return name[1:-1]

	def match(self, name: str, *, ctx: ParserMetaContext) -> t.Self | None:
		if name and name[0] in {'"', "'"}:
			return self

		return None
