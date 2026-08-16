from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from agentforge.agent.state import AgentState
from agentforge.agent.nodes import agent_node


def should_continue(state: AgentState):

    last_message = state["messages"][-1]

    if isinstance(last_message, dict):

        if last_message.get("tool_calls"):
            return "tools"

    elif getattr(last_message, "tool_calls", None):

        return "tools"

    return END


builder = StateGraph(AgentState)


builder.add_node(
    "agent",
    agent_node,
)


tool_node = ToolNode([])

builder.add_node(
    "tools",
    tool_node,
)


builder.add_edge(
    START,
    "agent",
)


builder.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        END: END,
    },
)


builder.add_edge(
    "tools",
    "agent",
)


graph = builder.compile()