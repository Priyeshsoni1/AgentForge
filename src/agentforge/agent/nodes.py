import os

from dotenv import load_dotenv
from openai import OpenAI
from agentforge.agent.state import AgentState
from agentforge.agent.tools import TOOLS




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



def agent_node(state: AgentState):

    response = client.chat.completions.create(
        model=MODEL,
        messages=state["messages"],
        tools=[tool.metadata for tool in TOOLS],
    )

    return {
        "messages": [response.choices[0].message]
    }