from langchain_core.tools import tool

from agentforge.tools.calculator import calculate
from agentforge.tools.get_time import get_time
from agentforge.tools.web_search import web_search
from agentforge.tools.weather import get_weather
from agentforge.tools.database_lookup import database_lookup


@tool
def calculator_tool(expression: str):
    """Calculate a mathematical expression."""
    return calculate(expression)


@tool
def time_tool(city: str):
    """Get the current time for a city."""
    return get_time(city)


@tool
def web_search_tool(query: str):
    """Search the web for information."""
    return web_search(query)


@tool
def weather_tool(city: str):
    """Get weather information for a city."""
    return get_weather(city)


@tool
def database_lookup_tool(user_id: str):
    """Look up information about a user by ID."""
    return database_lookup(user_id)


TOOLS = [
    calculator_tool,
    time_tool,
    web_search_tool,
    weather_tool,
    database_lookup_tool,
]