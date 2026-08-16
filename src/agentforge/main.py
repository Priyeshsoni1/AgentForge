import json
import os
import time

from dotenv import load_dotenv
from openai import OpenAI

from agentforge.core.tool_executor import execute_tool_safely

from agentforge.tools.calculator import calculate
from agentforge.tools.get_time import get_time
from agentforge.tools.web_search import web_search
from agentforge.tools.weather import get_weather
from agentforge.tools.database_lookup import database_lookup
from agentforge.tools.search_fallback import search_fallback

from agentforge.tools.schemas import (
    CALCULATOR_TOOL,
    DATABASE_TOOL,
    TIME_TOOL,
    WEATHER_TOOL,
    WEB_SEARCH_TOOL,
)


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

MODEL = "poolside/laguna-xs-2.1:free"

MAX_ITERATIONS = 5

MAX_TOOL_RETRIES = 2


# ---------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------

load_dotenv()


# ---------------------------------------------------------
# OpenRouter Client
# ---------------------------------------------------------

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)


# ---------------------------------------------------------
# Tools
# ---------------------------------------------------------

TOOLS = [
    CALCULATOR_TOOL,
    TIME_TOOL,
    WEB_SEARCH_TOOL,
    WEATHER_TOOL,
    DATABASE_TOOL,
]


# ---------------------------------------------------------
# Tool Executor
# ---------------------------------------------------------

def execute_tool(tool_name: str, arguments: dict):

    if tool_name == "calculate":
        return calculate(**arguments)

    if tool_name == "get_time":
        return get_time(**arguments)

    if tool_name == "web_search":
        return web_search(**arguments)

    if tool_name == "get_weather":
        return get_weather(**arguments)

    if tool_name == "database_lookup":
        return database_lookup(**arguments)

    raise ValueError(f"Unknown tool: {tool_name}")


# ---------------------------------------------------------
# Main Agent
# ---------------------------------------------------------

def main():

    question = input("Enter Your Problem ?.......... ")

    messages = [
        {
            "role": "user",
            "content": question,
        }
    ]

    # -----------------------------------------------------
    # Agent Loop
    # -----------------------------------------------------

    for iteration in range(MAX_ITERATIONS):

        print(
            f"\n--- Agent Iteration {iteration + 1} ---"
        )

        # -------------------------------------------------
        # Ask LLM
        # -------------------------------------------------

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
        )

        message = response.choices[0].message

        # -------------------------------------------------
        # Final Answer
        # -------------------------------------------------

        if not message.tool_calls:

            print("\nFinal Answer:")
            print(message.content)

            break

        # -------------------------------------------------
        # Add assistant message containing tool calls
        # -------------------------------------------------

        messages.append(message)

        # -------------------------------------------------
        # Execute ALL requested tools
        # -------------------------------------------------

        for tool_call in message.tool_calls:

            tool_name = tool_call.function.name

            arguments = json.loads(
                tool_call.function.arguments
            )

            print(
                "\nTool selected:",
                tool_name
            )

            print(
                "Arguments:",
                arguments
            )

            # -------------------------------------------------
            # Retry tool execution
            # -------------------------------------------------

            attempt = 0

            while attempt < MAX_TOOL_RETRIES:

                result = execute_tool_safely(
                    tool_name,
                    arguments,
                    execute_tool,
                )

                # ---------------------------------------------
                # Tool succeeded
                # ---------------------------------------------

                if result["success"]:

                    tool_result = result["result"]

                    print(
                        "Tool result:",
                        tool_result
                    )

                    break

                # ---------------------------------------------
                # Tool failed
                # ---------------------------------------------

                attempt += 1

                print(
                    f"Tool failed. "
                    f"Retry {attempt}/{MAX_TOOL_RETRIES}"
                )

            # -------------------------------------------------
            # Retries exhausted
            # -------------------------------------------------

            if not result["success"]:

                print(
                    "Tool failed after retries:",
                    result["error"]
                )

                # -------------------------------------------------
                # Web Search Fallback
                # -------------------------------------------------

                if tool_name == "web_search":

                    print(
                        "Using web search fallback..."
                    )

                    tool_result = search_fallback(
                        arguments.get("query", "")
                    )

                else:

                    tool_result = (
                        f"Tool failed: {result['error']}"
                    )

            # -------------------------------------------------
            # Add tool result to conversation
            # -------------------------------------------------

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(tool_result),
                }
            )

    # ---------------------------------------------------------
    # Maximum iterations reached
    # ---------------------------------------------------------

    else:

        print(
            "\nAgent stopped: maximum iterations reached."
        )


# ---------------------------------------------------------
# Entry Point
# ---------------------------------------------------------

if __name__ == "__main__":

    start = time.time()

    main()

    end = time.time()

    print(
        f"\nTime: {end - start:.2f} seconds"
    )