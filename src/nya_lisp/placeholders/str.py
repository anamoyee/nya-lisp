from .handlers import str as _h

# todo: using nya_scope add scopes which you can easily select all item of, so no need to mention all identifiers STR_* one-by-one

STR_JOIN = _h.StrJoinHandler().into_matcher("join", "str.join")

STR_LOWER = _h.StrLowerHandler().into_matcher("lower", "lowercase", "str.lower")
STR_UPPER = _h.StrUpperHandler().into_matcher("upper", "uppercase", "str.upper")
STR_TITLE = _h.StrTitleHandler().into_matcher("title", "titlecase", "str.title")
