from __future__ import annotations

from dataclasses import dataclass

type Node = Node__Text | Node__Placeholder
import typing as t

from .context import ParserMetaContext, ParserMetaContext__default
from .error import RootLevelContainsArgumentSeparatorError, UnclosedOpenError, UnexpectedCloseError


@dataclass(frozen=True, slots=True)
class Node__Text:
	inner: str

	def stripped(self) -> Node__Text:
		"""Return a new copy of this Node__Text with leading and trailing whitespace stripped.

		Returns:
			A new copy of this Node__Text with leading and trailing whitespace stripped.
		"""
		return Node__Text(self.inner.strip())

	def unparse(self, ctx: ParserMetaContext) -> str:
		"""Return the string representation of this Node__Text, which is just its inner string."""
		return self.inner


@dataclass(frozen=True, slots=True)
class Node__Placeholder:
	args: tuple[  # args
		tuple[  # arg_parts
			Node,
			...,
		],
		...,
	]

	def unparse(self, ctx: ParserMetaContext) -> str:
		"""Return the string representation of this Node__Placeholder, which is the concatenation of its args, separated by the separator defined in the context, and wrapped in the parentheses defined in the context."""

		sep = ctx["meta::parse_sep"]
		open_paren, close_paren = ctx["meta::parse_parens"]

		return (
			open_paren
			+ sep.join(
				"".join(
					part.unparse(ctx)  #
					for part in arg_parts
				)
				for arg_parts in self.args
			)
			+ close_paren
		)

	def stripped(self) -> Node__Placeholder:
		"""For all args recursively strip the leading whitespace of the first arg part, and the trailing whitespace of the last arg part.

		Returns:
			A new copy Node__Placeholder with the args recursively stripped of whitespace.
		"""
		stripped_args: list[list[Node]] = []

		for arg_parts in self.args:
			if len(arg_parts) == 0:
				stripped_args.append([])
				continue

			if len(arg_parts) == 1:
				(part,) = arg_parts

				match part:
					case Node__Text():
						new_part = Node__Text(part.inner.strip())
					case Node__Placeholder():
						new_part = part.stripped()
					case _:
						t.assert_never(part)

				stripped_args.append([new_part])
				continue

			left_part, *middle_parts, right_part = arg_parts

			match left_part:
				case Node__Text():
					new_left_part = Node__Text(left_part.inner.lstrip())
				case Node__Placeholder():
					new_left_part = left_part.stripped()
				case _:
					t.assert_never(left_part)

			new_middle_parts: list[Node] = []
			for middle_part in middle_parts:
				match middle_part:
					case Node__Text():
						new_middle_parts.append(Node__Text(middle_part.inner.strip()))
					case Node__Placeholder():
						new_middle_parts.append(middle_part.stripped())
					case _:
						t.assert_never(middle_part)

			match right_part:
				case Node__Text():
					new_right_part = Node__Text(right_part.inner.rstrip())
				case Node__Placeholder():
					new_right_part = right_part.stripped()
				case _:
					t.assert_never(right_part)

			stripped_args.append([new_left_part, *new_middle_parts, new_right_part])

		return Node__Placeholder(tuple(tuple(arg) for arg in stripped_args))


class Parser:
	def __init__(self, source: str) -> None:
		self.source = source
		self.pos = 0

	@classmethod
	def _raise_for_improper_meta_context(cls, ctx: ParserMetaContext) -> None:
		if ctx["meta::parse_parens"][0].__len__() != 1 or ctx["meta::parse_parens"][1].__len__() != 1:
			msg = f"{cls.__name__!r} currently doesnt support non-one length (i.e. 0, 2, 3, 4, ...) str as ctx::[meta::parse_parens][*]"
			raise ValueError(msg)
		if ctx["meta::parse_sep"].__len__() != 1:
			msg = f"{cls.__name__!r} currently doesnt support non-one length (i.e. 0, 2, 3, 4, ...) str as ctx::[meta::parse_sep]"
			raise ValueError(msg)

	def parse_one(self, ctx: ParserMetaContext = ParserMetaContext__default()) -> tuple[Node, ...]:
		placeholder_node = self.parse_into_node(ctx=ctx)

		match placeholder_node.args:
			case (first_args_arg_parts,):
				return first_args_arg_parts

		msg = "Root level of the source string passed to `parse_one()` contains an argument separator, which is not allowed. (i.e. the root level must be a placeholder with just one 'argument' which is considered a raw string)."
		raise RootLevelContainsArgumentSeparatorError(msg)

	def parse_into_node(
		self,
		ctx: ParserMetaContext = ParserMetaContext__default(),
	) -> Node__Placeholder:
		"""Parse the source string into a Node__Placeholder tree. Wrap the root source into a Node__Placeholder (aka, the root level CAN contain argument separators - if you don't want this behaviour, use `.parse_one()` which forbids separators and gives you a plug-and-play (to execute) output).

		Returns:
			The root Node__Placeholder of the parsed tree. (think of like if your input was wrapped in a placeholder: `{...}`, note that if the user expects the root scope to function as str.join, you should execute .args of this return value and not the return value itself, otherwise you'd be interpreting user's literal as matcher/handler name).

		Raises:
			UnexpectedCloseError: If an unexpected closing brace is encountered during parsing.
			UnclosedOpenError: If an opening brace is not closed during parsing.
			ValueError: If the ctx is not a valid ParserMetaContext (e.g. if the parens or sep are not one character long, unfortunately Parser does not support multi-char delimiters (yet).).
		"""  # ruff: ignore[docstring-extraneous-exception]

		self._raise_for_improper_meta_context(ctx)

		node, closed = self._parse_placeholder(root=True, ctx=ctx)

		if closed:
			msg = f"Unexpected {ctx["meta::parse_parens"][1]!r} at position {self.pos - 1}"
			raise UnexpectedCloseError(msg)

		return node

	def _parse_placeholder(
		self,
		*,
		root: bool,
		ctx: ParserMetaContext,
	) -> tuple[Node__Placeholder, bool]:
		args: list[list[Node]] = [[]]
		text_start = self.pos

		while self.pos < len(self.source):
			char = self.source[self.pos]

			if char == ctx["meta::parse_parens"][0]:
				if text_start != self.pos:
					args[-1].append(Node__Text(self.source[text_start : self.pos]))

				placeholder_start = self.pos
				self.pos += 1

				nested, closed = self._parse_placeholder(root=False, ctx=ctx)

				if not closed:
					msg = f"Unclosed placeholder starting at position {placeholder_start}"
					raise UnclosedOpenError(msg)

				args[-1].append(nested)
				text_start = self.pos
				continue

			if char == ctx["meta::parse_sep"]:
				if text_start != self.pos:
					args[-1].append(Node__Text(self.source[text_start : self.pos]))

				args.append([])
				self.pos += 1
				text_start = self.pos
				continue

			if char == ctx["meta::parse_parens"][1]:
				if root:
					msg_0 = f"Unexpected {ctx["meta::parse_parens"][1]!r} at position {self.pos}"
					raise UnexpectedCloseError(msg_0)

				if text_start != self.pos:
					args[-1].append(Node__Text(self.source[text_start : self.pos]))

				self.pos += 1

				return (
					Node__Placeholder(tuple(tuple(arg) for arg in args)),
					True,
				)

			self.pos += 1

		if not root:
			msg_1 = "Unclosed placeholder at end of input"
			raise UnclosedOpenError(msg_1)

		if text_start != self.pos:
			args[-1].append(Node__Text(self.source[text_start : self.pos]))

		return (
			Node__Placeholder(tuple(tuple(arg) for arg in args)),
			False,
		)


def parse(source: str, *, ctx: ParserMetaContext = ParserMetaContext__default()) -> tuple[Node, ...]:
	return Parser(source).parse_one(ctx=ctx)


def unparse(nodes: tuple[Node, ...] | Node, ctx: ParserMetaContext) -> str:
	"""Unparse a tuple of nodes (or a single Node) into a string representation.

	Args:
		nodes: A tuple of nodes to unparse.
		ctx: The parser meta context to use for unparsing.

	Returns:
		A string representation of the nodes.
	"""
	if not isinstance(nodes, tuple):
		nodes = (nodes,)

	return "".join(node.unparse(ctx) for node in nodes)


@t.overload
def stripped(nodes: tuple[Node, ...]) -> tuple[Node, ...]: ...


@t.overload
def stripped(nodes: Node) -> Node: ...


def stripped(nodes: tuple[Node, ...] | Node) -> tuple[Node, ...] | Node:
	"""Return a new copy of the given nodes (or a single Node) with leading and trailing whitespace stripped.

	Args:
		nodes: A tuple of nodes or a single Node to strip.

	Returns:
		A new copy of the given nodes (or a single Node) with leading and trailing whitespace stripped.
	"""
	if not isinstance(nodes, tuple):
		return nodes.stripped()

	return tuple(node.stripped() for node in nodes)
