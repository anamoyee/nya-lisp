import abc
from typing import Self


class LispSerde(abc.ABC):
	type Serialized = tuple[tuple[str, ...], dict[str, str]] | tuple[str, ...] | dict[str, str]

	class InvalidDeserializeInputError(Exception):
		"""Raised when deserialize() received args, kwargs pair that isn't valid to create a new instance of this type."""

	@abc.abstractmethod
	def serialize(self) -> Serialized:
		"""Serialize a lisp positional/keyword representation of this type, parsable back by from_str."""

	@classmethod
	@abc.abstractmethod
	def deserialize(cls, *args: str, **kwargs: str) -> Self:
		"""Deserialize this lisp type's instance from *args: str, **kwargs: str (split by the type delimeter, e.g. ","). The type tag is not included, you can derive it with `cls.__name__.casefold()`."""
