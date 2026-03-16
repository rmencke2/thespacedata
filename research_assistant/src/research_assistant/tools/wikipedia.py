"""Wikipedia search tool for encyclopedic information."""

import httpx
from langchain_core.tools import tool

from ..config import settings


@tool
def wikipedia_search(query: str, sentences: int = 5) -> str:
    """
    Search Wikipedia for encyclopedic information on a topic.

    Use this tool to find factual, well-sourced information about people,
    places, concepts, events, and other encyclopedic topics.

    Args:
        query: The topic to search for on Wikipedia
        sentences: Number of sentences to return from the article summary (default 5)

    Returns:
        Wikipedia article summary with title and URL
    """
    sentences = min(max(sentences, 1), 10)

    try:
        # Use Wikipedia's REST API for search
        search_response = httpx.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "list": "search",
                "srsearch": query,
                "srlimit": 3,
                "format": "json",
            },
            timeout=settings.TIMEOUT,
        )
        search_response.raise_for_status()
        search_data = search_response.json()

        search_results = search_data.get("query", {}).get("search", [])
        if not search_results:
            return f"No Wikipedia articles found for '{query}'"

        # Get the summary of the top result
        title = search_results[0]["title"]

        summary_response = httpx.get(
            "https://en.wikipedia.org/api/rest_v1/page/summary/" + title.replace(" ", "_"),
            timeout=settings.TIMEOUT,
        )
        summary_response.raise_for_status()
        summary_data = summary_response.json()

        extract = summary_data.get("extract", "No summary available.")
        url = summary_data.get("content_urls", {}).get("desktop", {}).get("page", f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}")

        # Truncate to requested number of sentences (approximate)
        sentences_list = extract.split(". ")
        if len(sentences_list) > sentences:
            extract = ". ".join(sentences_list[:sentences]) + "."

        # Show other search results if available
        other_results = ""
        if len(search_results) > 1:
            others = [r["title"] for r in search_results[1:]]
            other_results = f"\n\nRelated articles: {', '.join(others)}"

        return f"**{title}** (Wikipedia)\nURL: {url}\n\n{extract}{other_results}"

    except httpx.HTTPStatusError as e:
        return f"Wikipedia API error: {e.response.status_code}"
    except Exception as e:
        return f"Wikipedia search failed: {str(e)}"
