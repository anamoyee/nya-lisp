import pytest

from nya_lisp.client import Client
from nya_lisp.parse import UnknownResolverError
from nya_lisp.resolvers import Add, Comment, Concat, ResolverT, Sub


class SideEffectResolver(ResolverT[str]):
	executed = False

	@classmethod
	def accept(cls, name: str) -> bool:
		return name == "side_effect"

	def resolve(self) -> str:
		SideEffectResolver.executed = True
		return "MUTATED"


class IfResolver(ResolverT[str]):
	@classmethod
	def accept(cls, name: str) -> bool:
		return name == "if"

	def resolve(self) -> str:
		if not self.args:
			return ""
		cond = self.args[0].resolve()
		if cond and cond != "0" and cond.lower() != "false":
			return self.args[1].resolve() if len(self.args) > 1 else ""
		return self.args[2].resolve() if len(self.args) > 2 else ""


def test_add_resolver():
	client = Client()
	assert client("{add|1|2}") == "3"
	assert client("{add|10|20|30}") == "60"


def test_sub_resolver():
	client = Client()
	assert client("{sub|10|4}") == "6"
	assert client("{sub|10|2|3}") == "5"


def test_nested_resolvers_child_first():
	client = Client()
	assert client("{add|1|{sub|10|3}}") == "8"
	assert client("Result: {add|{add|1|2}|{sub|10|5}}") == "Result: 8"


def test_comment_resolver_suppresses_resolution_and_side_effects():
	SideEffectResolver.executed = False

	client = Client(Comment, SideEffectResolver)
	# Comment resolver must NOT call .resolve() on child nodes
	result = client("{comment|hello world {side_effect}}")

	assert result == ""  # noqa: PLC1901
	assert not SideEffectResolver.executed


def test_comment_resolver_pure_nested_comment():
	SideEffectResolver.executed = False

	client = Client(Comment, SideEffectResolver)
	result = client("{comment|{comment|{side_effect}}}")

	assert result == ""  # noqa: PLC1901
	assert not SideEffectResolver.executed


def test_dynamic_resolver_name():
	client = Client()
	# The name is itself an expression "{concat|a|dd}" -> "add"
	assert client("{{concat|a|dd}|5|5}") == "10"


def test_conditional_if_resolver_lazy_evaluation():
	SideEffectResolver.executed = False

	client = Client(IfResolver, SideEffectResolver, Concat)

	# Condition is "true", so only then branch should resolve
	assert client("{if|true|resolved_then|{side_effect}}") == "resolved_then"
	assert not SideEffectResolver.executed

	# Condition is "false", so only else branch should resolve
	assert client("{if|false|{side_effect}|resolved_else}") == "resolved_else"
	assert not SideEffectResolver.executed


def test_unknown_resolver_error():
	client = Client()
	with pytest.raises(UnknownResolverError) as exc_info:
		client("{non_existent_resolver|arg}")

	assert exc_info.value.name == "non_existent_resolver"


def test_client_custom_resolvers():
	client = Client(resolvers_list=[Add, Sub])
	assert client("{add|3|4}") == "7"

	with pytest.raises(UnknownResolverError):
		client("{comment|ignored}")
