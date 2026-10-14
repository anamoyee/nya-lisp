import nya_lisp as nl
import nya_lisp.placeholders._handlers as _h


def test_handle_dfs():
	h = _h.math.AddHandler()

	assert h.handle_dfs("add", "1", "2", ctx={}) == "3"


def test_handle_bfs():
	h = _h.math.AddHandler()

	assert (
		h.handle_bfs(
			"add",
			(nl.Node__Text("1"),),
			(nl.Node__Text("2"),),
			ctx={},
			executor=nl.Executor[None](),  # empty executor can execute text nodes just fine
		)
		== "3"
	)
