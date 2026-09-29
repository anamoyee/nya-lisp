import io

from . import node


def _parse(source: str, /, ctx: node.Context = node.Context.null()) -> node.NodeT:
	"""Parse source code into a node tree using the provided context.

	Args:
		source: The source code to parse.
		ctx: The context to use for parsing.

	Returns:
		A node tree representing the parsed source code.
	"""
	stream = io.StringIO(source)
	top_args: list[node.NodeT] = []

	while True:
		arg_node = _parse_argument(stream, ctx, stop_chars={"|"})
		top_args.append(arg_node)

		ch = stream.read(1)
		if ch == "|":
			continue
		break

	if len(top_args) == 1:
		return top_args[0]

	return node.BuiltinNodes__.Str__.Concat(name=None, args=tuple(top_args), ctx=ctx)


def _parse_argument(stream: io.StringIO, ctx: node.Context, stop_chars: set[str]) -> node.NodeT:
	parts: list[node.NodeT] = []
	buf: list[str] = []

	def flush_buf() -> None:
		if buf:
			parts.append(node._StaticNode(value="".join(buf)))
			buf.clear()

	while True:
		ch = stream.read(1)
		if not ch or ch in stop_chars:
			if ch:
				# Rewind stop character so caller loop can handle it
				stream.seek(stream.tell() - 1)
			break

		if ch == "{":
			flush_buf()
			expr_node = _parse_expr(stream, ctx)
			parts.append(expr_node)
		else:
			buf.append(ch)

	flush_buf()

	if not parts:
		return node._StaticNode(value="")

	if len(parts) == 1:
		return parts[0]

	return node.BuiltinNodes__.Str__.Concat(name=None, args=tuple(parts), ctx=ctx)


def _parse_expr(stream: io.StringIO, ctx: node.Context) -> node.NodeT:
	name_then_args: list[node.NodeT] = []

	while True:
		arg_node = _parse_argument(stream, ctx, stop_chars={"|", "}"})
		name_then_args.append(arg_node)

		ch = stream.read(1)
		if ch == "|":
			continue
		if ch == "}":
			break
		if not ch:
			break

	return node._ExprNode.new_from_args(*name_then_args, ctx=ctx)
