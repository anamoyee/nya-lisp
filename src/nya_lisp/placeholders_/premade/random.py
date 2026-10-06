from .._handlers import random as _h

__ALL__ = (
	(RANDOM := _h.RandomHandler().into_matcher("random", "rand", "randint", "randomint")),  #
)
