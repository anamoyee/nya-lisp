from __future__ import annotations

from dataclasses import dataclass

type Node = Node__Text | Node__Placeholder
from typing import TYPE_CHECKING, assert_never

if TYPE_CHECKING:
	from . import execute as m_execute


@dataclass(frozen=True, slots=True)
class Node__Text:
	inner: str

	def unparse(self, ctx: m_execute.ParserMetaContext) -> str:
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

	def unparse(self, ctx: m_execute.ParserMetaContext) -> str:
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

	def parse_with_parser_meta_context(self) -> tuple[Node__Placeholder, m_execute.ParserMetaContext]:
		return (
			self.parse(),
			{
				"meta::parse_parens": ("{", "}"),
				"meta::parse_sep": "|",
			},
		)

	def parse(self) -> Node__Placeholder:  # todo: make ParserMetaContext passable here, customize the parens and sep right away.
		node, closed = self._parse_placeholder(root=True)

		if closed:
			msg = f"Unexpected '}}' at position {self.pos - 1}"
			raise ParseError(msg)

		return node

	def _parse_placeholder(
		self,
		*,
		root: bool,
	) -> tuple[Node__Placeholder, bool]:
		args: list[list[Node]] = [[]]
		text_start = self.pos

		while self.pos < len(self.source):
			char = self.source[self.pos]

			if char == "{":
				if text_start != self.pos:
					args[-1].append(Node__Text(self.source[text_start : self.pos]))

				placeholder_start = self.pos
				self.pos += 1

				nested, closed = self._parse_placeholder(root=False)

				if not closed:
					msg = f"Unclosed placeholder starting at position {placeholder_start}"
					raise ParseError(msg)

				args[-1].append(nested)
				text_start = self.pos
				continue

			if char == "|":
				if text_start != self.pos:
					args[-1].append(Node__Text(self.source[text_start : self.pos]))

				args.append([])
				self.pos += 1
				text_start = self.pos
				continue

			if char == "}":
				if root:
					msg_0 = f"Unexpected '}}' at position {self.pos}"
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
