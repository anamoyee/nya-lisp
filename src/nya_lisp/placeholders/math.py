from .handlers import math as _h

ADD = _h.AddHandler().into_matcher("add", "sum", "+")
SUB = _h.SubHandler().into_matcher("sub", "subtract", "-")
MUL = _h.MulHandler().into_matcher("mul", "multiply", "*")
DIV = _h.DivHandler().into_matcher("div", "divide", "/")
POW = _h.PowHandler().into_matcher("pow", "power", "**")
SQRT = _h.SqrtHandler().into_matcher("sqrt")
