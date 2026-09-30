from __future__ import annotations

import pytest

from nya_lisp import Node__Placeholder, Node__Text, ParseError, Parser, parse


class TestParsePlainText:
	def test_empty_string(self) -> None:
		assert parse("") == Node__Placeholder(args=((),))

	def test_simple_text(self) -> None:
		assert parse("hello world") == Node__Placeholder(
			args=(
				(  #
					Node__Text("hello world"),
				),
			),
		)

	def test_whitespace(self) -> None:
		source = "  line1  line2 \t "
		assert parse(source) == Node__Placeholder(
			args=(
				(  #
					Node__Text("  line1  line2 \t "),
				),
			),
		)

	def test_newlines(self) -> None:
		source = "line1 \n line2"
		assert parse(source) == Node__Placeholder(
			args=(
				(  #
					Node__Text("line1 \n line2"),
				),
			),
		)

	def test_unicode_text(self) -> None:
		source = "Hello 🐱 World 🌍"
		assert parse(source) == Node__Placeholder(
			args=(
				(  #
					Node__Text("Hello 🐱 World 🌍"),
				),
			),
		)

	def test_special_characters_prose(self) -> None:
		source = "1 + 2 = 3; [x] * (y) / $100 \\ escaping"
		assert parse(source) == Node__Placeholder(
			args=(
				(  #
					Node__Text("1 + 2 = 3; [x] * (y) / $100 \\ escaping"),
				),
			)
		)


class TestParseSimplePlaceholders:
	def test_single_placeholder(self) -> None:
		assert parse("{foo}") == Node__Placeholder(
			args=(
				(
					Node__Placeholder(
						args=(
							(  #
								Node__Text("foo"),
							),
						)
					),
				),
			)
		)

	def test_empty_placeholder(self) -> None:
		assert parse("{}") == Node__Placeholder(
			args=(
				(
					Node__Placeholder(
						args=(  #
							(),
						)
					),
				),
			)
		)

	def test_placeholder_surrounded_by_text(self) -> None:
		assert parse("prefix{var}suffix") == Node__Placeholder(
			args=(
				(
					Node__Text("prefix"),
					Node__Placeholder(
						args=(
							(  #
								Node__Text("var"),
							),
						)
					),
					Node__Text("suffix"),
				),
			)
		)

	def test_multiple_consecutive_placeholders(self) -> None:
		assert parse("{a}{b}{c}") == Node__Placeholder(
			args=(
				(
					Node__Placeholder(
						args=(
							(  #
								Node__Text("a"),
							),
						)
					),
					Node__Placeholder(
						args=(
							(  #
								Node__Text("b"),
							),
						)
					),
					Node__Placeholder(
						args=(
							(  #
								Node__Text("c"),
							),
						)
					),
				),
			)
		)

	def test_multiple_placeholders_interspersed_with_text(self) -> None:
		assert parse("A{x}B{y}C") == Node__Placeholder(
			args=(
				(
					Node__Text("A"),
					Node__Placeholder(
						args=(
							(  #
								Node__Text("x"),
							),
						)
					),
					Node__Text("B"),
					Node__Placeholder(
						args=(
							(  #
								Node__Text("y"),
							),
						)
					),
					Node__Text("C"),
				),
			)
		)


class TestParsePlaceholdersWithArguments:
	def test_two_arguments(self) -> None:
		assert parse("{a|b}") == Node__Placeholder(
			args=(
				(
					Node__Placeholder(
						args=(
							(  #
								Node__Text("a"),
							),
							(  #
								Node__Text("b"),
							),
						)
					),
				),
			)
		)

	def test_multiple_arguments(self) -> None:
		assert parse("{a|b|c|d}") == Node__Placeholder(
			args=(
				(
					Node__Placeholder(
						args=(
							(  #
								Node__Text("a"),
							),
							(  #
								Node__Text("b"),
							),
							(  #
								Node__Text("c"),
							),
							(  #
								Node__Text("d"),
							),
						)
					),
				),
			)
		)

	def test_empty_arguments(self) -> None:
		assert parse("{|}") == Node__Placeholder(
			args=(
				(
					Node__Placeholder(
						args=(  #
							(),
							(),
						)
					),
				),
			)
		)

	def test_empty_first_argument(self) -> None:
		assert parse("{|b}") == Node__Placeholder(
			args=(
				(
					Node__Placeholder(
						args=(
							(),
							(  #
								Node__Text("b"),
							),
						)
					),
				),
			)
		)

	def test_empty_second_argument(self) -> None:
		assert parse("{a|}") == Node__Placeholder(
			args=(
				(
					Node__Placeholder(
						args=(
							(  #
								Node__Text("a"),
							),
							(),
						)
					),
				),
			)
		)

	def test_multiple_empty_arguments(self) -> None:
		assert parse("{||}") == Node__Placeholder(
			args=(
				(
					Node__Placeholder(
						args=(  #
							(),
							(),
							(),
						)
					),
				),
			)
		)

	def test_whitespace_in_arguments(self) -> None:
		assert parse("{  foo  |  bar  }") == Node__Placeholder(
			args=(
				(
					Node__Placeholder(
						args=(
							(  #
								Node__Text("  foo  "),
							),
							(  #
								Node__Text("  bar  "),
							),
						)
					),
				),
			)
		)


class TestParseRootLevelPipes:
	def test_root_two_branches(self) -> None:
		assert parse("a|b") == Node__Placeholder(
			args=(
				(  #
					Node__Text("a"),
				),
				(  #
					Node__Text("b"),
				),
			)
		)

	def test_root_multiple_branches(self) -> None:
		assert parse("a|b|c") == Node__Placeholder(
			args=(
				(  #
					Node__Text("a"),
				),
				(  #
					Node__Text("b"),
				),
				(  #
					Node__Text("c"),
				),
			)
		)

	def test_root_single_pipe(self) -> None:
		assert parse("|") == Node__Placeholder(
			args=(  #
				(),
				(),
			)
		)

	def test_root_empty_left(self) -> None:
		assert parse("|b") == Node__Placeholder(
			args=(
				(),
				(  #
					Node__Text("b"),
				),
			)
		)

	def test_root_empty_right(self) -> None:
		assert parse("a|") == Node__Placeholder(
			args=(
				(  #
					Node__Text("a"),
				),
				(),
			)
		)

	def test_root_multiple_pipes_empty(self) -> None:
		assert parse("||") == Node__Placeholder(
			args=(  #
				(),
				(),
				(),
			)
		)

	def test_root_pipes_with_placeholders(self) -> None:
		assert parse("foo|{bar}|baz") == Node__Placeholder(
			args=(
				(  #
					Node__Text("foo"),
				),
				(
					Node__Placeholder(
						args=(
							(  #
								Node__Text("bar"),
							),
						)
					),
				),
				(  #
					Node__Text("baz"),
				),
			)
		)


class TestParseNestedPlaceholders:
	def test_directly_nested(self) -> None:
		assert parse("{{a}}") == Node__Placeholder(
			args=(
				(
					Node__Placeholder(
						args=(
							(
								Node__Placeholder(
									args=(
										(  #
											Node__Text("a"),
										),
									)
								),
							),
						)
					),
				),
			)
		)

	def test_nested_within_text(self) -> None:
		assert parse("{a{b}c}") == Node__Placeholder(
			args=(
				(
					Node__Placeholder(
						args=(
							(
								Node__Text("a"),
								Node__Placeholder(
									args=(
										(  #
											Node__Text("b"),
										),
									)
								),
								Node__Text("c"),
							),
						)
					),
				),
			)
		)

	def test_nested_inside_argument(self) -> None:
		assert parse("{a|{b|c}|d}") == Node__Placeholder(
			args=(
				(
					Node__Placeholder(
						args=(
							(  #
								Node__Text("a"),
							),
							(
								Node__Placeholder(
									args=(
										(  #
											Node__Text("b"),
										),
										(  #
											Node__Text("c"),
										),
									)
								),
							),
							(  #
								Node__Text("d"),
							),
						)
					),
				),
			)
		)

	def test_deeply_nested(self) -> None:
		assert parse("{{{a}}}") == Node__Placeholder(
			args=(
				(
					Node__Placeholder(
						args=(
							(
								Node__Placeholder(
									args=(
										(
											Node__Placeholder(
												args=(
													(  #
														Node__Text("a"),
													),
												)
											),
										),
									)
								),
							),
						)
					),
				),
			)
		)

	def test_complex_nesting_mix(self) -> None:
		assert parse("start {fn|{arg1}|val_{arg2}} end") == Node__Placeholder(
			args=(
				(
					Node__Text("start "),
					Node__Placeholder(
						args=(
							(  #
								Node__Text("fn"),
							),
							(
								Node__Placeholder(
									args=(
										(  #
											Node__Text("arg1"),
										),
									)
								),
							),
							(
								Node__Text("val_"),
								Node__Placeholder(
									args=(
										(  #
											Node__Text("arg2"),
										),
									)
								),
							),
						)
					),
					Node__Text(" end"),
				),
			)
		)


class TestParseErrors:
	@pytest.mark.parametrize(
		("source", "expected_msg_pattern"),
		[
			("}", r"Unexpected '}' at position 0"),
			("abc}", r"Unexpected '}' at position 3"),
			("{a}}", r"Unexpected '}' at position 3"),
			("a|b}", r"Unexpected '}' at position 3"),
			("foo}bar", r"Unexpected '}' at position 3"),
		],
	)
	def test_unexpected_closing_brace(self, source: str, expected_msg_pattern: str) -> None:
		with pytest.raises(ParseError, match=expected_msg_pattern):
			parse(source)

	@pytest.mark.parametrize(
		"source",
		[
			"{",
			"{abc",
			"{a|b",
			"{a{b}",
			"prefix{unclosed",
			"{a|{b}",
			"{{",
			"{}{",
			"{{}",
		],
	)
	def test_unclosed_placeholder(self, source: str) -> None:
		with pytest.raises(ParseError, match=r"Unclosed placeholder"):
			parse(source)


class TestDataNodes:
	"""Tests checking Node dataclass properties."""

	def test_text_node_equality(self) -> None:
		node1 = Node__Text("hello")
		node2 = Node__Text("hello")
		node3 = Node__Text("world")
		assert node1 == node2
		assert node1 != node3

	def test_text_node_frozen(self) -> None:
		node = Node__Text("hello")
		with pytest.raises(AttributeError):
			node.inner = "change"  # ty: ignore[invalid-assignment]

	def test_placeholder_node_equality(self) -> None:
		p1 = Node__Placeholder(
			args=(
				(  #
					Node__Text("x"),
				),
			)
		)
		p2 = Node__Placeholder(
			args=(
				(  #
					Node__Text("x"),
				),
			)
		)
		assert p1 == p2

	def test_placeholder_node_frozen(self) -> None:
		p1 = Node__Placeholder(
			args=(
				(  #
					Node__Text("x"),
				),
			)
		)
		with pytest.raises(AttributeError):
			p1.args = ()  # ty: ignore[invalid-assignment]


def test_parser_class() -> None:
	assert Parser("{test}").parse() == Node__Placeholder(
		args=(
			(
				Node__Placeholder(
					args=(
						(  #
							Node__Text("test"),
						),
					)
				),
			),
		)
	)
