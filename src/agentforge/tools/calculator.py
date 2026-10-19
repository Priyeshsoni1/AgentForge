
import ast
import math
import operator


MAX_EXPRESSION_LENGTH = 200
MAX_ABS_VALUE = 1e100
MAX_EXPONENT = 1000

BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

UNARY_OPERATORS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _evaluate(node: ast.AST) -> int | float:
    if isinstance(node, ast.Constant):
        if type(node.value) not in (int, float):
            raise ValueError("Only numeric constants are allowed.")
        return node.value

    if isinstance(node, ast.BinOp):
        operator_type = type(node.op)

        if operator_type not in BINARY_OPERATORS:
            raise ValueError("Unsupported arithmetic operator.")

        left = _evaluate(node.left)
        right = _evaluate(node.right)

        if operator_type is ast.Pow:
            if abs(right) > MAX_EXPONENT:
                raise ValueError("Exponent is too large.")

        result = BINARY_OPERATORS[operator_type](left, right)
        return _validate_result(result)

    if isinstance(node, ast.UnaryOp):
        operator_type = type(node.op)

        if operator_type not in UNARY_OPERATORS:
            raise ValueError("Unsupported unary operator.")

        return _validate_result(
            UNARY_OPERATORS[operator_type](_evaluate(node.operand))
        )

    raise ValueError("Only basic arithmetic expressions are allowed.")


def _validate_result(value: int | float) -> int | float:
    if isinstance(value, complex):
        raise ValueError("Complex results are not supported.")

    if not math.isfinite(value) or abs(value) > MAX_ABS_VALUE:
        raise ValueError("Result is outside the permitted range.")

    return value


def calculate(expression: str) -> dict:
    """Evaluate a restricted arithmetic expression."""

    expression = expression.strip()

    if not expression or len(expression) > MAX_EXPRESSION_LENGTH:
        raise ValueError("Expression must contain 1–200 characters.")

    try:
        tree = ast.parse(expression, mode="eval")
        result = _evaluate(tree.body)
    except (SyntaxError, ZeroDivisionError, OverflowError) as exc:
        raise ValueError("Invalid arithmetic expression.") from exc

    return {
        "expression": expression,
        "result": result,
    }
