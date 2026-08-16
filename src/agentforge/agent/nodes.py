import os

from dotenv import load_dotenv
from openai import OpenAI
from langgraph.prebuilt import ToolNode

from agentforge.agent.state import AgentState

from agentforge.tools.schemas import (
    CALCULATOR_TOOL,
    DATABASE_TOOL,
    TIME_TOOL,
    WEATHER_TOOL,
    WEB_SEARCH_TOOL,
)


# ---------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------

load_dotenv()


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

MODEL = "poolside/laguna-xs-2.1:free"


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
# For now, these are OpenAI-compatible tool schemas.
# We are NOT converting the Python functions into
# LangGraph tools yet.
# ---------------------------------------------------------

TOOLS = [
    CALCULATOR_TOOL,
    TIME_TOOL,
    WEB_SEARCH_TOOL,
    WEATHER_TOOL,
    DATABASE_TOOL,
]


# ---------------------------------------------------------
# Agent Node
# ---------------------------------------------------------

def agent_node(state: AgentState):
    """
    Agent node:
    Sends the current conversation state to the LLM
    and returns the LLM response.
    """

    response = client.chat.completions.create(
        model=MODEL,
        messages=state["messages"],
        tools=TOOLS,
    )

    return {
        "messages": [
            response.choices[0].message
        ]
    }


# ---------------------------------------------------------
# Tool Node
# ---------------------------------------------------------
#
# LangGraph's ToolNode expects LangChain-compatible tools.
#
# Our existing tools are currently ordinary Python
# functions, so we intentionally leave this empty today.
#
# We will integrate the five tools properly later.
# ---------------------------------------------------------

tool_node = ToolNode([])