
import pytest

from agentforge.core.config import settings
from agentforge.tools.calculator import calculate
from agentforge.tools.file_reader import read_file
from agentforge.tools.rest_client import call_rest_api


def test_calculator_addition():
    assert calculate("25 * 4")["result"] == 100


def test_calculator_nested_expression():
    assert calculate("(100 - 20) / 4")["result"] == 20


def test_calculator_rejects_code():
    with pytest.raises(ValueError):
        calculate("__import__('os').getcwd()")


def test_calculator_rejects_division_by_zero():
    with pytest.raises(ValueError):
        calculate("1 / 0")


def test_file_reader_reads_workspace_file(tmp_path, monkeypatch):
    (tmp_path / "example.txt").write_text(
        "Hello AgentForge",
        encoding="utf-8",
    )
    monkeypatch.setattr(settings, "file_reader_root", str(tmp_path))

    result = read_file("example.txt")

    assert result["content"] == "Hello AgentForge"


def test_file_reader_rejects_path_traversal(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "file_reader_root", str(tmp_path))

    with pytest.raises(ValueError):
        read_file("../secret.txt")


@pytest.mark.asyncio
async def test_rest_client_rejects_unapproved_host():
    with pytest.raises(ValueError, match="allowlist"):
        await call_rest_api(
            "GET",
            "https://example.com/data",
        )


@pytest.mark.asyncio
async def test_rest_client_rejects_http():
    with pytest.raises(ValueError):
        await call_rest_api(
            "GET",
            "http://jsonplaceholder.typicode.com/posts/1",
        )
