from typing import Literal


Operation = Literal["add", "subtract", "multiply", "divide"]


def calculate(
    a: float,
    b: float,
    operation: Operation,
) -> float:
    """Perform arithmetic on two numbers."""

    if operation == "add":
        return a + b

    if operation == "subtract":
        return a - b

    if operation == "multiply":
        return a * b

    if operation == "divide":
        if b == 0:
            raise ValueError("Cannot divide by zero.")

        return a / b

    raise ValueError(f"Unsupported operation: {operation}")