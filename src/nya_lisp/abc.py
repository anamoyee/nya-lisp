import abc
import typing as t

from .error import TooManyOrFewPositionalArgumentsInHandlerError


class Matcher[HandlerT, ContextT](abc.ABC):
	@abc.abstractmethod
	def match(self, name: str, *args: str, ctx: ContextT) -> HandlerT | None:
		"""Return a matching handler for placeholder `name`, or `None` if no match here is found."""


class Handler[ContextT](abc.ABC):
	@abc.abstractmethod
	def handle(self, name: str, *args: str, ctx: ContextT) -> str:
		"""Handle and evaluate the placeholder `name` with the given `args` and Context `ctx`, returning the evaluated string result."""

	def into_matcher(self, name: str, *aliases: str) -> Matcher[t.Self, ContextT]:
		"""Return a matcher that matches the given `name` and `aliases` to this handler.

		Args:
			name: The primary name of the placeholder to match. (for now there's no distinction between a primary name and an alias, but handlers or matchers may decide to do different things on one given name, but they dont know which is primary)
			aliases: Additional names that should also match this handler.

		Raises:
			ValueError: If any of the names have leading or trailing whitespace, which is not supported in `into_matcher()`, if you REALLY need leading or trailing whitespace, write a verbose matcher impl.
		"""

		if (name, *aliases) != tuple({name, *aliases}):
			msg = f"Duplicate placeholder names found in {name!r} and {aliases!r}. Each name must be unique. Edit the callsite, this meant to be more of a static helper, if you're using this dynamically, wrap your args in `*{{...}}`"
			raise ValueError(msg)

		names = {name, *aliases}

		for name_ in names:
			if name_.strip() != name_:
				msg = f"Placeholder name {name_!r} has leading or trailing whitespace, which is not supported in `into_matcher()`, if you REALLY need leading or trailing whitespace, write a verbose matcher impl."
				raise ValueError(msg)

		handler = self

		_Matcher = type(
			f"{self.__class__.__name__}AutoMatcher",
			(Matcher,),
			{
				"match": lambda self, name, *args, ctx: handler if name.lower() in names else None,  # ruff: ignore[unused-lambda-argument]
			},
		)

		return _Matcher()

	def _assert_args_count[T](self, len_args: int, *, expect: int | tuple[int | None, int] | tuple[int, int | None]) -> None:
		if isinstance(expect, int):
			expect = (expect, expect)

		if expect[0] is not None and len_args < expect[0]:
			raise TooManyOrFewPositionalArgumentsInHandlerError(len_args, expect)
		if expect[1] is not None and len_args > expect[1]:
			raise TooManyOrFewPositionalArgumentsInHandlerError(len_args, expect)


class Placeholder[ContextT](Matcher[Handler[ContextT], ContextT], Handler[ContextT]):
	"""A placeholder is a matcher and handler for a specific placeholder name. This is only a shorthand, functions as a convenience for the implementor. The mechanism actually looks for a `Matcher[Handler[...], ...]`."""
