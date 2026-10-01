import typing as t

from ...execute import Handler

VarContext = t.TypedDict(
	"VarContext",
	{
		"var::vars": t.NotRequired[dict[str, str]],
	},
)


class VarHandler(Handler[VarContext]):
	class TD(VarContext): ...

	def handle(self, name: str, *args: str, ctx: VarContext) -> str:
		self._assert_args_count(len(args), expect=(1, 2))

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
