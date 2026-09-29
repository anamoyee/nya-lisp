import re

import nya_fmt as nf
import pytest

import nya_lisp as nl
from nya_lisp.node import BuiltinNodes__ as Nodes__
from nya_lisp.node import _ExprNode as Expr
from nya_lisp.node import _StaticNode as Static


@pytest.fixture
def nullctx():
	yield (given_ctx := nl.Context.null())

	assert given_ctx == nl.Context.null()


@pytest.fixture
def ctx():
	return nl.Context.default()


@pytest.fixture
def fmt():
	return nf.Formatter(
		include_at_notation=False,
		no_quoteless_str=True,
	)


def test_empty_str(nullctx: nl.Context, fmt: nf.Formatter):
	tree = nl._parse("", ctx=nullctx)

	match tree:
		case Static(""):
			pass
		case _:
			msg = "Unexpected shape of parsed node tree."
			e = AssertionError(msg)
			e.add_note(fmt(tree).plain)
			raise e


def test_static_str(nullctx: nl.Context, fmt: nf.Formatter):
	tree = nl._parse("text", ctx=nullctx)

	match tree:
		case Static("text"):
			pass
		case _:
			msg = "Unexpected shape of parsed node tree."
			e = AssertionError(msg)
			e.add_note(fmt(tree).plain)
			raise e


def test_single_expr(ctx: nl.Context, fmt: nf.Formatter):
	tree = nl._parse("{+|1|2}", ctx=ctx)

	match tree:
		case Nodes__.Math__.Add(
			name="+",
			args=(
				Static("1"),
				Static("2"),
			),
		):
			pass
		case _:
			msg = "Unexpected shape of parsed node tree."
			e = AssertionError(msg)
			e.add_note(fmt(tree).plain)
			raise e

	assert tree.resolve() == "3"


def test_single_empty_expr(ctx: nl.Context, fmt: nf.Formatter):
	tree = nl._parse("{}", ctx=ctx)

	match tree:
		case Nodes__.Str__.Concat(
			name="",
			args=(),
		):
			pass
		case _:
			msg = "Unexpected shape of parsed node tree."
			e = AssertionError(msg)
			e.add_note(fmt(tree).plain)
			raise ez

	assert tree.resolve() == ""


def test_non_existent_expr_is_error(nullctx: nl.Context):
	non_existent_expr_name = "non_existent_expr"

	# todo: make errors actually contain source code and highlight the error location.
	with pytest.raises(KeyError, match=rf"^{re.escape(repr(non_existent_expr_name))}$"):
		nl._parse("{%s}" % non_existent_expr_name, ctx=nullctx)  # ruff: ignore[printf-string-formatting]
