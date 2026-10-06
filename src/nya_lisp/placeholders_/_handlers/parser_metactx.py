from ...abc import HandlerDFS
from ...context import ParserMetaContext


class ParserSeparatorHandler(HandlerDFS[ParserMetaContext]):
	Context = ParserMetaContext

	def handle_dfs(self, name: str, *args: str, ctx: ParserMetaContext) -> str:
		self._assert_argc(len(args), expect=0)

		return ctx["meta::parse_sep"]


class ParserOpenParenHandler(HandlerDFS[ParserMetaContext]):
	Context = ParserMetaContext

	def handle_dfs(self, name: str, *args: str, ctx: ParserMetaContext) -> str:
		self._assert_argc(len(args), expect=0)

		return ctx["meta::parse_parens"][0]


class ParserCloseParenHandler(HandlerDFS[ParserMetaContext]):
	Context = ParserMetaContext

	def handle_dfs(self, name: str, *args: str, ctx: ParserMetaContext) -> str:
		self._assert_argc(len(args), expect=0)

		return ctx["meta::parse_parens"][1]
