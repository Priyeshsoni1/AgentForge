
import httpx

from agentforge.core.config import settings


TAVILY_URL = "https://api.tavily.com/search"


async def web_search(query: str) -> dict:
    """Search the web and return relevant results."""

    query = query.strip()
    if not query or len(query) > 500:
        raise ValueError("Query must contain 1–500 characters.")

    if not settings.tavily_api_key:
        raise RuntimeError("Tavily API key is not configured.")

    headers = {
        "Authorization": (
            f"Bearer {settings.tavily_api_key.get_secret_value()}"
        )
    }
    payload = {
        "query": query,
        "search_depth": "basic",
        "max_results": 5,
        "include_answer": True,
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                TAVILY_URL,
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        return {
            "query": query,
            "answer": data.get("answer"),
            "results": [
                {
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "content": item.get("content", "")[:2000],
                }
                for item in data.get("results", [])[:5]
            ],
        }

    except httpx.HTTPStatusError as exc:
        raise RuntimeError(
            f"Tavily returned HTTP {exc.response.status_code}."
        ) from exc
    except (httpx.RequestError, ValueError) as exc:
        raise RuntimeError("Tavily search failed.") from exc
