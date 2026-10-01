from __future__ import annotations

from dataclasses import dataclass

type Node = Node__Text | Node__Placeholder
from typing import assert_never

from .context import ParserMetaContext, ParserMetaContext__default


@dataclass(frozen=True, slots=True)
class Node__Text:
	inner: str

	def unparse(self, ctx: ParserMetaContext) -> str:
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
						assert_never(part)

				stripped_args.append([new_part])
				continue

			left_part, *middle_parts, right_part = arg_parts

			match left_part:
				case Node__Text():
					new_left_part = Node__Text(left_part.inner.lstrip())
				case Node__Placeholder():
					new_left_part = left_part.stripped()
				case _:
					assert_never(left_part)

			new_middle_parts: list[Node] = []
			for middle_part in middle_parts:
				match middle_part:
					case Node__Text():
						new_middle_parts.append(Node__Text(middle_part.inner.strip()))
					case Node__Placeholder():
						new_middle_parts.append(middle_part.stripped())
					case _:
						assert_never(middle_part)

			match right_part:
				case Node__Text():
					new_right_part = Node__Text(right_part.inner.rstrip())
				case Node__Placeholder():
					new_right_part = right_part.stripped()
				case _:
					assert_never(right_part)

			stripped_args.append([new_left_part, *new_middle_parts, new_right_part])

		return Node__Placeholder(tuple(tuple(arg) for arg in stripped_args))


class ParseError(ValueError):
	"""Raised when a parsing error occurs in the input string."""


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

	def parse(
		self,
		ctx: ParserMetaContext = ParserMetaContext__default(),
	) -> Node__Placeholder:
		"""Parse the source string into a Node__Placeholder tree.

		Returns:
			The root Node__Placeholder of the parsed tree. (think of like if your input was wrapped in a placeholder: `{...}`, note that if the user expects the root scope to function as str.join, you should execute .args of this return value and not the return value itself, otherwise you'd be interpreting user's literal as matcher/handler name).

		Raises:
			ParseError: If the source string is not a valid placeholder expression.
			ValueError: If the ctx is not a valid ParserMetaContext (e.g. if the parens or sep are not one character long, unfortunately Parser does not support multi-char delimiters (yet).).
		"""  # ruff: ignore[docstring-extraneous-exception]

		self._raise_for_improper_meta_context(ctx)

		node, closed = self._parse_placeholder(root=True, ctx=ctx)

		if closed:
			msg = f"Unexpected {ctx["meta::parse_parens"][1]!r} at position {self.pos - 1}"
			raise ParseError(msg)

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
					raise ParseError(msg)

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
					raise ParseError(msg_0)

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
			raise ParseError(msg_1)

		if text_start != self.pos:
			args[-1].append(Node__Text(self.source[text_start : self.pos]))

		return (
			Node__Placeholder(tuple(tuple(arg) for arg in args)),
			False,
		)


def parse(source: str) -> Node__Placeholder:
	return Parser(source).parse()
