from langgraph.graph import StateGraph, START, END

from agentforge.agent.state import AgentState
from agentforge.agent.nodes import agent_node


builder = StateGraph(AgentState)

builder.add_node("agent", agent_node)

builder.add_edge(START, "agent")
builder.add_edge("agent", END)

graph = builder.compile()