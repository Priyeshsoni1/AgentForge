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

TIME_TOOL = {
    "type": "function",
    "function": {
        "name": "get_time",
        "description": "Get the current time for a supported city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City name, such as Delhi, London, Tokyo, or New York."
                }
            },
            "required": ["city"]
        }
    }
}