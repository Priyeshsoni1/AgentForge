
import json

from langchain_core.tools import tool

from agentforge.tools.calculator import calculate
from agentforge.tools.file_reader import read_file
from agentforge.tools.python_executor import execute_python
from agentforge.tools.rest_client import call_rest_api
from agentforge.tools.web_search import web_search


def _to_json(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, default=str)


@tool
def calculator(expression: str) -> str:
    """Evaluate a basic arithmetic expression such as '(25 * 4) / 2'."""
    try:
        return _to_json(calculate(expression))
    except (ValueError, ArithmeticError) as exc:
        return _to_json({"error": str(exc)})


@tool
def file_reader(relative_path: str) -> str:
    """Read a UTF-8 text file located inside the approved workspace."""
    try:
        return _to_json(read_file(relative_path))
    except (ValueError, OSError) as exc:
        return _to_json({"error": str(exc)})


@tool
async def web_search_tool(query: str) -> str:
    """Search the web for current information using Tavily."""
    try:
        return _to_json(await web_search(query))
    except (ValueError, RuntimeError) as exc:
        return _to_json({"error": str(exc)})


@tool
async def python_executor(code: str) -> str:
    """Run Python code in the restricted Docker sandbox."""
    try:
        return _to_json(await execute_python(code))
    except (ValueError, RuntimeError) as exc:
        return _to_json({"error": str(exc)})


@tool
async def rest_api_caller(
    method: str,
    url: str,
    params: dict | None = None,
    json_body: dict | None = None,
) -> str:
    """Call an approved HTTPS API using GET or POST."""
    try:
        return _to_json(
            await call_rest_api(
                method=method,
                url=url,
                params=params,
                json_body=json_body,
            )
        )
    except (ValueError, RuntimeError) as exc:
        return _to_json({"error": str(exc)})


AGENT_TOOLS = [
    web_search_tool,
    calculator,
    python_executor,
    file_reader,
    rest_api_caller,
]
