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

WEB_SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Search the web for information.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query."
                }
            },
            "required": ["query"]
        }
    }
}

WEATHER_TOOL = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current weather information for a city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "Name of the city."
                }
            },
            "required": ["city"]
        }
    }
}

DATABASE_TOOL = {
    "type": "function",
    "function": {
        "name": "database_lookup",
        "description": "Look up user information using a user ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "The user's ID."
                }
            },
            "required": ["user_id"]
        }
    }
}