from .handlers import var as _h

VAR = _h.VarHandler().into_matcher("$", "var", "var-set", "var-get")
