import typing as t

if t.TYPE_CHECKING:
	import typing_extensions as te


class EmptyContext(t.TypedDict):  # imported by placeholders/
	pass


ParserMetaContext = t.TypedDict(
	"ParserMetaContext",
	{
		"meta::parse_parens": "te.ReadOnly[tuple[str, str]]",
		"meta::parse_sep": "te.ReadOnly[str]",
	},
)


def ParserMetaContext__default() -> ParserMetaContext:
	return {
		"meta::parse_parens": ("{", "}"),
		"meta::parse_sep": "|",
	}


def ParserMetaContext__lisp() -> ParserMetaContext:
	return {
		"meta::parse_parens": ("(", ")"),
		"meta::parse_sep": " ",
	}
