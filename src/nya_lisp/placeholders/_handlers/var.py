import typing as t
from collections.abc import MutableMapping

from ...abc import HandlerDFS

VarContext = t.TypedDict(
	"VarContext",
	{
		"var::vars": MutableMapping[str, str],
	},
)


class VarHandler(HandlerDFS[VarContext]):
	Context = VarContext

	def handle_dfs(self, name: str, *args: str, ctx: VarContext) -> str:
		self._assert_argc(len(args), expect=(1, 2))

		vars_mapping = ctx["var::vars"]

		match args:
			case [var_name]:
				return var_name
			case [var_name, var_value]:
				vars_mapping[var_name] = var_value
				return ""
			case _:
				msg = "unreachable: should have been caught by _assert_args_count"
				raise AssertionError(msg)
