from __future__ import annotations

from dataclasses import dataclass

type Node = Node__Text | Node__Placeholder


@dataclass(frozen=True, slots=True)
class Node__Text:
	inner: str


@dataclass(frozen=True, slots=True)
class Node__Placeholder:
	args: tuple[tuple[Node, ...], ...]


class ParseError(ValueError):
	"""Raised when a parsing error occurs in the input string."""


class Parser:
	def __init__(self, source: str) -> None:
		self.source = source
		self.pos = 0

	def parse(self) -> Node__Placeholder:
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
