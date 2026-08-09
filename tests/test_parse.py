import pytest

from nya_lisp.parse import (
	AST__,
	UnexpectedClosingBraceError,
	UnexpectedPipeError,
	parse,
)

# ==============================================================================
# Normal / Valid Cases
# ==============================================================================


def test_parse_empty_string():
	assert parse("") == []


def test_parse_empty_braces():
	assert parse("{}") == [
		AST__.Expr(name=AST__.Constant(""), children=()),
	]


def test_parse_single_constant():
	assert parse("{asdf}") == [
		AST__.Expr(name=AST__.Constant("asdf"), children=()),
	]


def test_parse_single_expr_with_children():
	assert parse("{asdfasf|sfasdf}") == [
		AST__.Expr(
			name=AST__.Constant("asdfasf"),
			children=(AST__.Constant("sfasdf"),),
		)
	]


def test_parse_multiple_children():
	assert parse("{a|b|c|d}") == [
		AST__.Expr(
			name=AST__.Constant("a"),
			children=(
				AST__.Constant("b"),
				AST__.Constant("c"),
				AST__.Constant("d"),
			),
		)
	]


def test_parse_nested_expr_in_child():
	assert parse("{a|{b|c}|d}") == [
		AST__.Expr(
			name=AST__.Constant("a"),
			children=(
				AST__.Expr(
					name=AST__.Constant("b"),
					children=(AST__.Constant("c"),),
				),
				AST__.Constant("d"),
			),
		)
	]


def test_parse_nested_expr_in_name():
	assert parse("{{asdf}}") == [
		AST__.Expr(
			name=AST__.Expr(name=AST__.Constant("asdf"), children=()),
			children=(),
		)
	]


def test_parse_multiple_top_level_expressions():
	assert parse("{a|b}{c|d}") == [
		AST__.Expr(
			name=AST__.Constant("a"),
			children=(AST__.Constant("b"),),
		),
		AST__.Expr(
			name=AST__.Constant("c"),
			children=(AST__.Constant("d"),),
		),
	]


def test_parse_preserves_spaces_and_special_characters():
	input_str = "{hello world!| @#$%^&*()\n\t }"
	assert parse(input_str) == [
		AST__.Expr(
			name=AST__.Constant("hello world!"),
			children=(AST__.Constant(" @#$%^&*()\n\t "),),
		)
	]


def test_parse_empty_fields():
	# Tests handling of consecutive pipes and trailing pipes
	assert parse("{|a||}") == [
		AST__.Expr(
			name=AST__.Constant(""),
			children=(
				AST__.Constant("a"),
				AST__.Constant(""),
				AST__.Constant(""),
			),
		)
	]


# ==============================================================================
# Error Cases
# ==============================================================================


def test_parse_top_level_constant_and_expr():
	assert parse("a{b}") == [
		AST__.Constant("a"),
		AST__.Expr(name=AST__.Constant("b"), children=()),
	]


def test_error_top_level_text():
	with pytest.raises(UnexpectedPipeError) as exc_info:
		parse("asdfasdf|asdfasdf")

	assert exc_info.value.char == "|"
	assert exc_info.value.pos == 8


def test_error_unexpected_pipe_at_top_level():
	with pytest.raises(UnexpectedPipeError) as exc_info:
		parse("|")

	assert exc_info.value.char == "|"
	assert exc_info.value.pos == 0


def test_error_unexpected_pipe_after_valid_expr():
	with pytest.raises(UnexpectedPipeError) as exc_info:
		parse("{a}|")

	assert exc_info.value.char == "|"
	assert exc_info.value.pos == 3


def test_error_unexpected_closing_brace_top_level():
	with pytest.raises(UnexpectedClosingBraceError) as exc_info:
		parse("}")

	assert exc_info.value.char == "}"
	assert exc_info.value.pos == 0


def test_error_unmatched_extra_closing_brace():
	with pytest.raises(UnexpectedClosingBraceError) as exc_info:
		parse("{a}}")

	assert exc_info.value.char == "}"
	assert exc_info.value.pos == 3


def test_error_unmatched_opening_brace_at_eof():
	with pytest.raises(UnexpectedClosingBraceError) as exc_info:
		parse("{a|b")

	assert exc_info.value.char == "}"
	assert exc_info.value.pos == 4


def test_error_nested_unmatched_opening_brace():
	with pytest.raises(UnexpectedClosingBraceError) as exc_info:
		parse("{a|{b|c}")

	assert exc_info.value.char == "}"
	assert exc_info.value.pos == 8
