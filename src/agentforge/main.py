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
from agentforge.tools.schemas import CALCULATOR_TOOL, DATABASE_TOOL, TIME_TOOL, WEATHER_TOOL, WEB_SEARCH_TOOL

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)



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


def main():
    question = input("Enter Your Problem ?.......... ")

    messages = [
        {
            "role": "user",
            "content": question,
        }
    ]
    response = client.chat.completions.create(
        model="poolside/laguna-xs-2.1:free",
        messages=messages,
        TOOLS = [
            CALCULATOR_TOOL,
            TIME_TOOL,
            WEB_SEARCH_TOOL,
            WEATHER_TOOL,
            DATABASE_TOOL,
        ]
    )

    message = response.choices[0].message
    print(message)

    if message.tool_calls:
        tool_call = message.tool_calls[0]

        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        print("Tool selected:", tool_name)
        print("Arguments:", arguments)

        result = execute_tool(tool_name, arguments)
        print(result)
        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result),
            }
        )
        final_response = client.chat.completions.create(
            model="poolside/laguna-xs-2.1:free",
            messages=messages,
            TOOLS = [
                CALCULATOR_TOOL,
                TIME_TOOL,
                WEB_SEARCH_TOOL,
                WEATHER_TOOL,
                DATABASE_TOOL,
            ]
        )

        print(final_response.choices[0].message.content)

    else:
        print("Model response:", message.content)


if __name__ == "__main__":
    start=time.time()
    
    main()
    end=time.time()
    print("time",end-start)