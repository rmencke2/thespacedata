"""Tool for searching competitor news and announcements."""

import httpx
from langchain_core.tools import tool
from datetime import datetime, timedelta

from ..config import settings
from ..competitors import COMPETITORS, get_competitor


@tool
def competitor_news(
    competitor_name: str,
    days_back: int = 7,
    focus: str = "all",
) -> str:
    """
    Search for recent news and announcements about a competitor.

    Use this tool to find news articles, press releases, product announcements,
    and feature updates from competitors.

    Args:
        competitor_name: Name of the competitor (e.g., "Wix", "Duda", "GoDaddy")
        days_back: How many days back to search (default 7)
        focus: Focus area - "all", "features", "pricing", "partnerships", "funding"

    Returns:
        Recent news and announcements about the competitor
    """
    competitor = get_competitor(competitor_name)
    if not competitor:
        available = ", ".join([c.name for c in COMPETITORS])
        return f"Unknown competitor '{competitor_name}'. Available: {available}"

    # Build search query based on focus
    base_query = f"{competitor.name} website builder"
    focus_terms = {
        "features": "new feature OR product update OR launch OR release OR announcement",
        "pricing": "pricing OR price change OR new plan OR subscription",
        "partnerships": "partnership OR integration OR acquisition",
        "funding": "funding OR investment OR valuation",
        "all": "news OR announcement OR update OR launch",
    }
    focus_term = focus_terms.get(focus, focus_terms["all"])
    query = f"{base_query} ({focus_term})"

    # Calculate date range
    date_from = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")

    # If no search API, provide guidance
    if not settings.SEARCH_API_KEY:
        return f"""[Competitor News Search - No SEARCH_API_KEY configured]

To search for {competitor.name} news, I would search for:
Query: "{query}"
Date range: Last {days_back} days (from {date_from})

Suggested manual sources to check:
- {competitor.blog_url or f'https://{competitor.domain}/blog'}
- Google News: https://news.google.com/search?q={competitor.name}+website+builder
- TechCrunch: https://techcrunch.com/search/{competitor.name}
- Product Hunt: https://www.producthunt.com/search?q={competitor.name}

To enable automatic search, set SEARCH_API_KEY in your .env file (Tavily recommended)."""

    # Use Tavily API for search
    try:
        response = httpx.post(
            "https://api.tavily.com/search",
            json={
                "api_key": settings.SEARCH_API_KEY,
                "query": query,
                "max_results": 10,
                "search_depth": "advanced",
                "include_domains": [
                    "techcrunch.com",
                    "venturebeat.com",
                    "theverge.com",
                    "producthunt.com",
                    "businesswire.com",
                    "prnewswire.com",
                    competitor.domain,
                ],
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()

        results = []
        for r in data.get("results", []):
            results.append(
                f"**{r.get('title', 'No title')}**\n"
                f"URL: {r.get('url', 'N/A')}\n"
                f"Published: {r.get('published_date', 'Unknown')}\n"
                f"{r.get('content', '')}\n"
            )

        if not results:
            return f"No recent news found for {competitor.name} in the last {days_back} days."

        return f"## Recent News: {competitor.name}\n\n" + "\n---\n".join(results)

    except Exception as e:
        return f"News search failed: {str(e)}"


@tool
def competitor_features(competitor_name: str) -> str:
    """
    Search for recent feature announcements and product updates from a competitor.

    Use this tool specifically to find new features, product launches, and
    capability updates from competitors.

    Args:
        competitor_name: Name of the competitor (e.g., "Wix", "Duda", "GoDaddy")

    Returns:
        Recent feature announcements and product updates
    """
    competitor = get_competitor(competitor_name)
    if not competitor:
        available = ", ".join([c.name for c in COMPETITORS])
        return f"Unknown competitor '{competitor_name}'. Available: {available}"

    query = f'"{competitor.name}" (new feature OR product update OR "now available" OR launched OR release notes) website builder 2024 2025'

    if not settings.SEARCH_API_KEY:
        blog_url = competitor.blog_url or f"https://{competitor.domain}/blog"
        return f"""[Feature Search - No SEARCH_API_KEY configured]

To find {competitor.name} feature updates, check:
- Official blog: {blog_url}
- Release notes: https://{competitor.domain}/release-notes (if available)
- Help center/changelog
- Twitter/X: @{competitor.name.lower()}

Query I would search: "{query}"

To enable automatic search, set SEARCH_API_KEY in your .env file."""

    try:
        response = httpx.post(
            "https://api.tavily.com/search",
            json={
                "api_key": settings.SEARCH_API_KEY,
                "query": query,
                "max_results": 8,
                "search_depth": "advanced",
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()

        results = []
        for r in data.get("results", []):
            results.append(
                f"**{r.get('title', 'No title')}**\n"
                f"URL: {r.get('url', 'N/A')}\n"
                f"{r.get('content', '')}\n"
            )

        if not results:
            return f"No recent feature announcements found for {competitor.name}."

        return f"## Feature Updates: {competitor.name}\n\n" + "\n---\n".join(results)

    except Exception as e:
        return f"Feature search failed: {str(e)}"


@tool
def list_competitors() -> str:
    """
    List all monitored competitors and their details.

    Use this tool to see which competitors are being tracked.

    Returns:
        List of competitors with their domains and key URLs
    """
    lines = ["## Monitored Competitors (Webnode)\n"]
    for c in COMPETITORS:
        lines.append(f"### {c.name}")
        lines.append(f"- Domain: {c.domain}")
        if c.pricing_url:
            lines.append(f"- Pricing: {c.pricing_url}")
        if c.blog_url:
            lines.append(f"- Blog: {c.blog_url}")
        lines.append("")

    return "\n".join(lines)
