import typing as t

from ...abc import HandlerDFS

VarContext = t.TypedDict(
	"VarContext",
	{
		"var::vars": t.NotRequired[dict[str, str]],
	},
)


class VarHandler(HandlerDFS[VarContext]):
	Context = VarContext

	def handle_dfs(self, name: str, *args: str, ctx: VarContext) -> str:
		self._assert_argc(len(args), expect=(1, 2))

		if "var::vars" not in ctx:
			ctx["var::vars"] = {}

		vars_dict = ctx["var::vars"]

		match args:
			case [var_name]:
				return var_name
			case [var_name, var_value]:
				vars_dict[var_name] = var_value
				return ""
			case _:
				msg = "unreachable: should have been caught by _assert_args_count"
				raise AssertionError(msg)
