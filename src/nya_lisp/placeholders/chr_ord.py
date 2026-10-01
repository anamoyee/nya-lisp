from .handlers import chr_ord as _h

CHR = _h.ChrHandler().into_matcher("chr")
ORD = _h.OrdHandler().into_matcher("ord")
