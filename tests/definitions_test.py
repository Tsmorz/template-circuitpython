"""Test the definitions file for an example."""

import pytest

from change_me.definitions import DUMMY_VARIABLE


@pytest.mark.parametrize(
    ("input_var", "expected_var"),
    [
        [0.0, 0.0],
        [1.0, 1.0],
    ],
)
def test_dummy_variable(input_var: float, expected_var: float) -> None:
    """Assert that the fake variable is correctly set.

    :param input_var: The input variable.
    :param expected_var: The expected variable.
    :return: None
    """
    assert DUMMY_VARIABLE == "dummy_variable"
    assert input_var == expected_var
