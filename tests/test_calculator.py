import pytest

from agentforge.tools.calculator import calculate


def test_add():
    assert calculate(10, 5, "add") == 15


def test_subtract():
    assert calculate(10, 5, "subtract") == 5


def test_multiply():
    assert calculate(10, 5, "multiply") == 50


def test_divide():
    assert calculate(10, 5, "divide") == 2


def test_division_by_zero():
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        calculate(10, 0, "divide")


def test_invalid_operation():
    with pytest.raises(ValueError, match="Unsupported operation"):
        calculate(10, 5, "power")