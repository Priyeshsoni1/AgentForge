import json
import os
import time
from dotenv import load_dotenv
from openai import OpenAI

from agentforge.tools.calculator import calculate
from agentforge.tools.get_time import get_time
from agentforge.tools.schemas import CALCULATOR_TOOL, TIME_TOOL

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
        tools=[CALCULATOR_TOOL,TIME_TOOL],
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
            tools=[CALCULATOR_TOOL,TIME_TOOL],
        )

        print(final_response.choices[0].message.content)

    else:
        print("Model response:", message.content)


if __name__ == "__main__":
    start=time.time()
    
    main()
    end=time.time()
    print("time",end-start)