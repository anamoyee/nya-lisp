import pytest

import nya_lisp as nl


@pytest.mark.parametrize(
	("source", "expected"),
	[
		# add
		("{add|1}", "1"),
		("{add|1|2}", "3"),
		("{+|1|2|3}", "6"),
		("{add|1|2|3|4}", "10"),
		("{add|1|2|3|4|5}", "15"),
		# sub
		("{-|5}", "-5"),
		("{sub|5|3}", "2"),
		("{sub|5|3|1}", "1"),
		("{sub|5|3|1|1}", "0"),
		("{sub|5|3|1|1|1}", "-1"),
		# mul
		("{mul|4|6}", "24"),
		("{*|4|6|2}", "48"),
		("{mul|4|6|2|3}", "144"),
		("{mul|4|6|2|3|5}", "720"),
		# div
		("{div|8|2}", "4"),
		("{/|9|2}", "4.5"),
		("{div|9|2|3}", "1.5"),
		("{div|9|2|3|1.5}", "1"),
		("{div|9|2|3|1.5|0.5}", "2"),
		# floor div
		("{//|8|2}", "4"),
		("{fdiv|9|2}", "4"),
		("{fdiv|9|2|3}", "1"),
		("{fdiv|9|2|3|1.5}", "0"),
		# pow
		("{pow|2|3}", "8"),
		("{**|2|3|2}", "64"),  # (2^3)^2 = 8^2 = 64
		("{pow|2|0.5}", f"{float(2**0.5):g}"),
		# sqrt
		("{sqrt|16}", "4"),
		("{√|2}", f"{float(2**0.5):g}"),
	],
)
def test_math_basic(source: str, expected: str) -> None:
	exe = nl.Executor(*nl.placeholders.math.__ALL_BASIC__)

	assert exe(nl.parse(source), ctx={}) == expected


def test_math_manual_neg():
	exe = nl.Executor(*nl.placeholders.math.__ALL_BASIC__)

	assert exe(nl.parse("{add|1|-{sub|5|3}}"), ctx={}) == "-1"
	assert exe(nl.parse("{add|1|-{sub|5|7}}"), ctx={}) == "3"
