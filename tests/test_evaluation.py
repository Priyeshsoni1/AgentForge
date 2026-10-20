
from agentforge.evaluation import extract_tool_names, score_case


def test_extract_tool_names():
    calls = [
        {"name": "calculator"},
        {"tool_name": "web_search"},
        {"tool": "file_reader"},
    ]

    assert extract_tool_names(calls) == {
        "calculator",
        "web_search",
        "file_reader",
    }


def test_score_case_passes_when_all_criteria_match():
    case = {
        "id": "calculator",
        "expected_keywords": ["1000"],
        "required_tools": ["calculator"],
    }
    result = {
        "answer": "The result is 1000.",
        "tool_calls": [{"name": "calculator"}],
    }

    scored = score_case(case, result)

    assert scored["passed"] is True
    assert scored["missing_keywords"] == []
    assert scored["missing_tools"] == []


def test_score_case_fails_when_keyword_is_missing():
    case = {
        "id": "api",
        "expected_keywords": ["request", "response"],
        "required_tools": [],
    }
    result = {
        "answer": "An API connects software systems.",
        "tool_calls": [],
    }

    scored = score_case(case, result)

    assert scored["passed"] is False
    assert "request" in scored["missing_keywords"]
    assert "response" in scored["missing_keywords"]


def test_score_case_fails_when_required_tool_was_not_used():
    case = {
        "id": "calculator",
        "expected_keywords": ["1000"],
        "required_tools": ["calculator"],
    }
    result = {
        "answer": "The result is 1000.",
        "tool_calls": [],
    }

    scored = score_case(case, result)

    assert scored["passed"] is False
    assert scored["missing_tools"] == ["calculator"]


def test_score_case_fails_for_empty_answer():
    case = {
        "id": "empty",
        "expected_keywords": [],
        "required_tools": [],
    }
    result = {"answer": " ", "tool_calls": []}

    assert score_case(case, result)["passed"] is False
