from ...execute import Handler, ParserMetaContext


class ParserSeparatorHandler(Handler[ParserMetaContext]):
	def handle(self, name: str, *args: str, ctx: ParserMetaContext) -> str:
		self._assert_args_count(len(args), expect=(0, 0))

		return ctx["meta::parse_sep"]


class ParserOpenParenHandler(Handler[ParserMetaContext]):
	def handle(self, name: str, *args: str, ctx: ParserMetaContext) -> str:
		self._assert_args_count(len(args), expect=(0, 0))

		return ctx["meta::parse_parens"][0]


class ParserCloseParenHandler(Handler[ParserMetaContext]):
	def handle(self, name: str, *args: str, ctx: ParserMetaContext) -> str:
		self._assert_args_count(len(args), expect=(0, 0))

		return ctx["meta::parse_parens"][1]
