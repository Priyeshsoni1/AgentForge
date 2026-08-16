def web_search(query: str) -> str:
    if not query.strip():
        raise ValueError("Search query cannot be empty")

    return f"Search results for: {query}"