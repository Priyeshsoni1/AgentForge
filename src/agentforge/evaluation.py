
from typing import Any


def extract_tool_names(tool_calls: list[Any]) -> set[str]:
    """Extract tool names from the agent's recorded tool-call metadata."""
    names: set[str] = set()

    for item in tool_calls:
        if isinstance(item, str):
            names.add(item.lower())
            continue

        if not isinstance(item, dict):
            continue

        # Support common metadata shapes.
        name = (
            item.get("name")
            or item.get("tool_name")
            or item.get("tool")
        )

        if isinstance(name, str):
            names.add(name.lower())

    return names


def score_case(
    case: dict[str, Any],
    result: dict[str, Any],
) -> dict[str, Any]:
    """Score a single evaluation case against its expected criteria."""
    answer = str(result.get("answer", ""))
    answer_lower = answer.lower()

    expected_keywords = case.get("expected_keywords", [])
    missing_keywords = [
        keyword
        for keyword in expected_keywords
        if keyword.lower() not in answer_lower
    ]

    actual_tools = extract_tool_names(result.get("tool_calls", []))
    required_tools = {
        tool.lower() for tool in case.get("required_tools", [])
    }
    missing_tools = sorted(required_tools - actual_tools)

    passed = (
        bool(answer.strip())
        and not missing_keywords
        and not missing_tools
    )

    return {
        "id": case["id"],
        "passed": passed,
        "answer": answer,
        "missing_keywords": missing_keywords,
        "missing_tools": missing_tools,
        "actual_tools": sorted(actual_tools),
    }
