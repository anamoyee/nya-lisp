import typing as t

from ...abc import HandlerDFS

PyEvalExecContext = t.TypedDict(
	"PyEvalExecContext",
	{
		"pyevalexec::extra_locals": t.NotRequired[dict[str, object]],
	},
)


class PyEval(HandlerDFS[PyEvalExecContext]):
	"""Evaluate given source at arg0 as a Python expression and return the result stringified (exactly 1 arg required).

	### ‼️ This placeholder can run arbitrary code in your application. NEVER use it with untrusted input.
	"""

	Context = PyEvalExecContext

	def handle_dfs(self, name: str, *args: str, ctx: PyEvalExecContext) -> str:
		self._assert_argc(len(args), expect=1)

		if len(args) == 1:
			(arg,) = args

			compiled = compile(arg, "<PyEval placeholder>", mode="eval")

			locals_ = dict(
				name=name,
				args=args,
				ctx=ctx,
				**ctx.get("pyevalexec::extra_locals", {}),
			)

			return str(eval(compiled, locals_, globals()))

		msg = "unreachable: should have been caught by _assert_args_count"
		raise AssertionError(msg)


class PyExec(HandlerDFS[PyEvalExecContext]):
	"""Evaluate given source at arg0 as a Python code and return the value of the `_` variable stringified, unless it was not set, in which case return `""` (exactly 1 arg required).

	### ‼️ This placeholder can run arbitrary code in your application. NEVER use it with untrusted input.
	"""

	Context = PyEvalExecContext

	def handle_dfs(self, name: str, *args: str, ctx: PyEvalExecContext) -> str:
		self._assert_argc(len(args), expect=1)

		if len(args) == 1:
			(arg,) = args

			compiled = compile(arg, "<PyEval placeholder>", mode="exec")

			locals_ = dict(
				name=name,
				args=args,
				ctx=ctx,
				**ctx.get("pyevalexec::extra_locals", {}),
			)

			exec(compiled, locals_, globals())

			return str(locals_.get("_", ""))

		msg = "unreachable: should have been caught by _assert_args_count"
		raise AssertionError(msg)
