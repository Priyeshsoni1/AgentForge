import json
import os
import time

from dotenv import load_dotenv
from openai import OpenAI

from agentforge.tools.calculator import calculate
from agentforge.tools.get_time import get_time
from agentforge.tools.web_search import web_search
from agentforge.tools.weather import get_weather
from agentforge.tools.database_lookup import database_lookup

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

MAX_ITERATIONS = 5


# ---------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------

load_dotenv()


# ---------------------------------------------------------
# OpenRouter client
# ---------------------------------------------------------

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)


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

    tools = [
        CALCULATOR_TOOL,
        TIME_TOOL,
        WEB_SEARCH_TOOL,
        WEATHER_TOOL,
        DATABASE_TOOL,
    ]

    # -----------------------------------------------------
    # Agent Loop
    # -----------------------------------------------------

    for iteration in range(MAX_ITERATIONS):

        print(f"\n--- Agent Iteration {iteration + 1}/{MAX_ITERATIONS} ---")

        # Ask the LLM
        response = client.chat.completions.create(
            model="poolside/laguna-xs-2.1:free",
            messages=messages,
            tools=tools,
        )

        message = response.choices[0].message

        # -------------------------------------------------
        # No tool call = final answer
        # -------------------------------------------------

        if not message.tool_calls:

            print("\nFinal Answer:")
            print(message.content)

            return

        # -------------------------------------------------
        # Add assistant tool-call message
        # -------------------------------------------------

        messages.append(
            {
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments,
                        },
                    }
                    for tool_call in message.tool_calls
                ],
            }
        )

        # -------------------------------------------------
        # Execute ALL tool calls
        # -------------------------------------------------

        for tool_call in message.tool_calls:

            tool_name = tool_call.function.name

            arguments = json.loads(
                tool_call.function.arguments
            )

            print("\nTool selected:", tool_name)
            print("Arguments:", arguments)

            try:
                result = execute_tool(
                    tool_name,
                    arguments
                )

                print("Tool result:", result)

            except Exception as e:

                result = f"Tool execution failed: {str(e)}"

                print("Tool error:", result)

            # -------------------------------------------------
            # Send tool result back to the LLM
            # -------------------------------------------------

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result),
                }
            )

    # -----------------------------------------------------
    # Maximum iterations reached
    # -----------------------------------------------------

    print("\nAgent stopped: maximum iterations reached.")


# ---------------------------------------------------------
# Entry Point
# ---------------------------------------------------------

if __name__ == "__main__":

    start = time.time()

    main()

    end = time.time()

    print(f"\nTime: {end - start:.2f} seconds")