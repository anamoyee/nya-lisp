from typing import Self

import pytest

import nya_lisp as nl

# todo: write test which checks that subclassing from something that defines ARGC doesnt overwrite it with the basemost class value
# todo: actually maybe change the impl so it doesnt use __init_subclass__ because it's soo clunky. I mean might just change it to a method decorator? that would be fine... - and this approach doesnt reuqire some bullshit state at the class level like ARGC variable. Also have a @automatcher class decorator which replaces MATCH_NAMES - but first fix the error where it says there's some bullshit wehere it doesnt even run because obj is not instance or subclass of type?


class TstPlaceholder_ARGC_1(nl.PlaceholderBFS[nl.EmptyContext], ARGC=1):
	def match(self, name: str, *, ctx: nl.EmptyContext) -> Self:
		return self

	def handle_bfs(
		self,
		name: str,
		*args: tuple[nl.Node, ...],
		ctx: nl.EmptyContext,
		executor: nl.Executor[nl.EmptyContext],
	) -> str:
		return "handled"


class TstPlaceholder_ARGC_range2(nl.PlaceholderBFS[nl.EmptyContext], ARGC=range(2)):
	def match(self, name: str, *, ctx: nl.EmptyContext) -> Self:
		return self

	def handle_bfs(
		self,
		name: str,
		*args: tuple[nl.Node, ...],
		ctx: nl.EmptyContext,
		executor: nl.Executor[nl.EmptyContext],
	) -> str:
		return "handled"


def test_argc_int_raises_when_invalid():
	exe = nl.Executor(
		TstPlaceholder_ARGC_1(),
	)

	with pytest.raises(nl.error.TooManyOrFewPositionalArgumentsInHandlerError):
		exe.execute(
			nl.parse("{name|arg1|arg2}"),
			ctx={},
		)


def test_argc_range_raises_when_invalid():
	exe = nl.Executor(
		TstPlaceholder_ARGC_range2(),
	)

	with pytest.raises(nl.error.TooManyOrFewPositionalArgumentsInHandlerError):
		exe.execute(
			nl.parse("{name|arg1|arg2}"),
			ctx={},
		)


def test_argc_int_doesnt_raise_when_valid():
	exe = nl.Executor(
		TstPlaceholder_ARGC_1(),
	)

	assert (
		exe.execute(
			nl.parse("{name|arg1}"),
			ctx={},
		)
		== "handled"
	)


def test_argc_range_doesnt_raise_when_valid():
	exe = nl.Executor(
		TstPlaceholder_ARGC_range2(),
	)

	assert (
		exe.execute(
			nl.parse("{name|arg1}"),
			ctx={},
		)
		== "handled"
	)

	assert (
		exe.execute(
			nl.parse("{name}"),
			ctx={},
		)
		== "handled"
	)
