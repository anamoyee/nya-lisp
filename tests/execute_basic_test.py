import string

import pytest

import nya_lisp as nl
from nya_lisp import Executor, ParserMetaContext__default, parse


@pytest.mark.parametrize(
	"source",
	[
		"",
		"a",
		"Chujowy World.",
		"Meow meow meow",
		string.ascii_letters,
		string.whitespace,
		string.digits,
	],
)
def test_execute_no_placeholders_unchanged(source: str) -> None:
	empty_executor = Executor()

	ctx = ParserMetaContext__default()

	result = empty_executor.execute(
		parse(source, ctx=ctx),
		ctx=ctx,
	)

	assert result == source


@pytest.mark.parametrize(
	"source",
	[
		"{}",
		"{hello}",
		"Meow meow {hello}",
		"{hello} meow meow",
		"Meow {hello} meow",
	],
)
def test_execute_unmatched_placeholder_raises(source: str) -> None:
	empty_executor = Executor()

	ctx = ParserMetaContext__default()

	with pytest.raises(nl.error.ExecutorNoMatchingHandlerError):
		empty_executor.execute(
			parse(source, ctx=ctx),
			ctx=ctx,
		)
