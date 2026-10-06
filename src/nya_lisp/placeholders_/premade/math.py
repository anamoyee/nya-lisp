from .._handlers import math as _h

__ALL__ = (
	*(
		__ALL_BASIC__ := (
			(ADD := _h.AddHandler().into_matcher("add", "sum", "+")),
			(SUB := _h.SubHandler().into_matcher("sub", "subtract", "-")),
			(MUL := _h.MulHandler().into_matcher("mul", "multiply", "*")),
			(TRUEDIV := _h.TrueDivHandler().into_matcher("tdiv", "div", "truediv", "divide", "/")),
			(FLOORDIV := _h.FloorDivHandler().into_matcher("fdiv", "floordiv", "floordivide", "//")),
			(POW := _h.PowHandler().into_matcher("pow", "power", "**")),
			(SQRT := _h.SqrtHandler().into_matcher("sqrt", "√")),
		)
	),
)
