from .._handlers import str as _h

__ALL__ = (
	(JOIN := _h.StrJoinHandler().into_matcher("join", "str.join")),
	(LOWER := _h.StrLowerHandler().into_matcher("lower", "lowercase", "str.lower")),
	(UPPER := _h.StrUpperHandler().into_matcher("upper", "uppercase", "str.upper")),
	(TITLE := _h.StrTitleHandler().into_matcher("title", "titlecase", "str.title")),
)
