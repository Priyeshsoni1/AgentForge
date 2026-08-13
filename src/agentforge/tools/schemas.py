CALCULATOR_TOOL = {
    "type": "function",
    "function": {
        "name": "calculate",
        "description": (
            "Perform arithmetic on two numbers. "
            "Use this tool for addition, subtraction, "
            "multiplication, or division."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "a": {
                    "type": "number",
                    "description": "The first number.",
                },
                "b": {
                    "type": "number",
                    "description": "The second number.",
                },
                "operation": {
                    "type": "string",
                    "enum": [
                        "add",
                        "subtract",
                        "multiply",
                        "divide",
                    ],
                    "description": "The arithmetic operation to perform.",
                },
            },
            "required": ["a", "b", "operation"],
            "additionalProperties": False,
        },
    },
}