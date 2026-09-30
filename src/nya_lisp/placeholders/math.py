from ..execute import EmptyTD, Matcher
from .handlers import math as h


class AddPlaceholder(h.AddHandler, Matcher[h.AddHandler, EmptyTD]):
	def match(self, name: str, *_, ctx: EmptyTD) -> h.AddHandler | None:
		if name in {"add", "sum", "+"}:
			return self

		return None
