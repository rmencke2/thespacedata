"""Web search tool for gathering information from the internet."""

import httpx
from langchain_core.tools import tool

from ..config import settings


@tool
def web_search(query: str, num_results: int = 5) -> str:
    """
    Search the web for information on a topic.

    Use this tool to find current information, news, articles, and general
    web content about any topic.

    Args:
        query: The search query - be specific for better results
        num_results: Number of results to return (default 5, max 10)

    Returns:
        Formatted search results with titles, URLs, and snippets
    """
    num_results = min(num_results, 10)

    # If no search API key, return a helpful message
    if not settings.SEARCH_API_KEY:
        return (
            f"[Web search for '{query}' - No SEARCH_API_KEY configured]\n\n"
            "To enable web search, set SEARCH_API_KEY in your .env file.\n"
            "Supported providers: Tavily (tavily.com), Serper (serper.dev)\n\n"
            "For now, please use the wikipedia_search tool or provide information directly."
        )

    # Try Tavily API format first (most common for LangChain projects)
    try:
        response = httpx.post(
            "https://api.tavily.com/search",
            json={
                "api_key": settings.SEARCH_API_KEY,
                "query": query,
                "max_results": num_results,
                "include_answer": False,
            },
            timeout=settings.TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()

        results = []
        for r in data.get("results", []):
            results.append(f"**{r.get('title', 'No title')}**\nURL: {r.get('url', 'N/A')}\n{r.get('content', '')}\n")

        if not results:
            return f"No results found for '{query}'"

        return f"Search results for '{query}':\n\n" + "\n---\n".join(results)

    except httpx.HTTPStatusError as e:
        return f"Search API error: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Search failed: {str(e)}"
