from .handlers import parser_metactx as _h

PARSER_META = [
	_h.ParserSeparatorHandler().into_matcher("meta_separator"),
	_h.ParserOpenParenHandler().into_matcher("meta_open_paren"),
	_h.ParserCloseParenHandler().into_matcher("meta_close_paren"),
]
