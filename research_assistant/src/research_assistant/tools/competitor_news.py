"""Tool for searching competitor news and announcements."""

import httpx
from langchain_core.tools import tool
from datetime import datetime, timedelta
import re

from ..config import settings
from ..competitors import COMPETITORS, get_competitor
from .rss_utils import fetch_recent_feed_entries, format_feed_entries


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

    # If no search API, fall back to official blog RSS/Atom when possible
    if not settings.SEARCH_API_KEY:
        entries = fetch_recent_feed_entries(
            competitor.blog_url or f"https://{competitor.domain}/blog",
            days_back=days_back,
            max_items=10,
            timeout_s=settings.TIMEOUT,
        )
        if entries:
            return format_feed_entries(entries, f"## Recent Official Updates (feed): {competitor.name}")

        return f"""[Competitor News Search - No SEARCH_API_KEY configured]

To search for {competitor.name} news, I would search for:
Query: "{query}"
Date range: Last {days_back} days (from {date_from})

Suggested manual sources to check:
- {competitor.blog_url or f'https://{competitor.domain}/blog'}
- Google News: https://news.google.com/search?q={competitor.name}+website+builder
- TechCrunch: https://techcrunch.com/search/{competitor.name}
- Product Hunt: https://www.producthunt.com/search?q={competitor.name}

To enable automatic search, set SEARCH_API_KEY in your .env file (Tavily recommended; or set SEARCH_PROVIDER=serper)."""

    # Use Tavily API for search
    try:
        if (settings.SEARCH_PROVIDER or "tavily").strip().lower() == "serper":
            # Serper doesn't support include_domains filtering like Tavily; keep query focused.
            response = httpx.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": settings.SEARCH_API_KEY},
                json={"q": f"{query} since:{date_from}", "num": 10},
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            results = []
            for r in data.get("organic", [])[:10]:
                results.append(
                    f"**{r.get('title', 'No title')}**\n"
                    f"URL: {r.get('link', 'N/A')}\n"
                    f"Published: {r.get('date', 'Unknown')}\n"
                    f"{r.get('snippet', '')}\n"
                )

            if not results:
                return f"No recent news found for {competitor.name} in the last {days_back} days."

            return f"## Recent News: {competitor.name}\n\n" + "\n---\n".join(results)

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
        entries = fetch_recent_feed_entries(
            blog_url,
            days_back=14,
            max_items=10,
            timeout_s=settings.TIMEOUT,
        )
        if entries:
            # Light heuristic filter: feature-ish titles first
            feature_terms = ("release", "launch", "introduc", "new", "update", "announc", "ai", "editor", "commerce", "ecommerce")
            featured = [e for e in entries if any(t in (e.title or "").lower() for t in feature_terms)]
            chosen = featured[:8] or entries[:8]
            return format_feed_entries(chosen, f"## Recent Official Feature/Update Posts (feed): {competitor.name}")

        return f"""[Feature Search - No SEARCH_API_KEY configured]

To find {competitor.name} feature updates, check:
- Official blog: {blog_url}
- Release notes: https://{competitor.domain}/release-notes (if available)
- Help center/changelog
- Twitter/X: @{competitor.name.lower()}

Query I would search: "{query}"

To enable automatic search, set SEARCH_API_KEY in your .env file (or set SEARCH_PROVIDER=serper)."""

    try:
        if (settings.SEARCH_PROVIDER or "tavily").strip().lower() == "serper":
            response = httpx.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": settings.SEARCH_API_KEY},
                json={"q": query, "num": 8},
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            results = []
            for r in data.get("organic", [])[:8]:
                results.append(
                    f"**{r.get('title', 'No title')}**\n"
                    f"URL: {r.get('link', 'N/A')}\n"
                    f"{r.get('snippet', '')}\n"
                )

            if not results:
                return f"No recent feature announcements found for {competitor.name}."

            return f"## Feature Updates: {competitor.name}\n\n" + "\n---\n".join(results)

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


def _strip_html(text: str) -> str:
    """Very small HTML-to-text helper (no external deps)."""
    text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _tavily_search(query: str, max_results: int = 8) -> list[dict]:
    response = httpx.post(
        "https://api.tavily.com/search",
        json={
            "api_key": settings.SEARCH_API_KEY,
            "query": query,
            "max_results": max_results,
            "search_depth": "advanced",
            "include_answer": False,
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json().get("results", []) or []


def _serper_search(query: str, max_results: int = 8) -> list[dict]:
    response = httpx.post(
        "https://google.serper.dev/search",
        headers={"X-API-KEY": settings.SEARCH_API_KEY},
        json={"q": query, "num": max_results},
        timeout=30,
    )
    response.raise_for_status()
    return response.json().get("organic", []) or []


@tool
def competitor_install_base(competitor_name: str) -> str:
    """
    Find install-base / usage metrics for a competitor (e.g., users, sites, market share).

    This is useful for sizing migration campaigns (e.g., targeting Weebly users).

    Args:
        competitor_name: Name of the competitor (e.g., "Weebly", "Wix")

    Returns:
        Evidence-focused results (with source URLs) about install base / usage.
    """
    competitor = get_competitor(competitor_name)
    if not competitor:
        available = ", ".join([c.name for c in COMPETITORS])
        return f"Unknown competitor '{competitor_name}'. Available: {available}"

    if not settings.SEARCH_API_KEY:
        return (
            f"[Install-base research - No SEARCH_API_KEY configured]\n\n"
            f"Set SEARCH_API_KEY (and optionally SEARCH_PROVIDER=tavily|serper) to enable automated sizing for {competitor.name}.\n"
            "Suggested queries:\n"
            f'- "{competitor.name} number of users"\n'
            f'- "{competitor.name} number of websites"\n'
            f'- "how many sites use {competitor.name}"\n'
            f'- "{competitor.name} market share website builder"\n'
        )

    # Prefer evidence from primary/credible sources (Square filings/blog, Wikipedia, BuiltWith/W3Techs, etc.)
    queries = [
        f'{competitor.name} "number of users"',
        f'{competitor.name} "millions of users"',
        f'{competitor.name} "number of websites"',
        f'how many sites use {competitor.name}',
        f'{competitor.name} market share "website builder"',
        f'{competitor.name} Square acquisition users',
    ]

    provider = (settings.SEARCH_PROVIDER or "tavily").strip().lower()
    results_lines: list[str] = [f"## Install Base / Usage Signals: {competitor.name}", ""]

    try:
        seen_urls: set[str] = set()
        hits: list[tuple[str, str, str]] = []

        for q in queries:
            if provider == "serper":
                organic = _serper_search(q, max_results=6)
                for r in organic:
                    url = (r.get("link") or "").strip()
                    if not url or url in seen_urls:
                        continue
                    seen_urls.add(url)
                    hits.append((r.get("title", "No title"), url, r.get("snippet", "")))
            else:
                tav = _tavily_search(q, max_results=6)
                for r in tav:
                    url = (r.get("url") or "").strip()
                    if not url or url in seen_urls:
                        continue
                    seen_urls.add(url)
                    hits.append((r.get("title", "No title"), url, r.get("content", "")))

            if len(hits) >= 12:
                break

        if not hits:
            return f"No install-base/usage results found for {competitor.name}."

        results_lines.append("**Top sources to review (evidence + citations):**")
        for title, url, snippet in hits[:12]:
            snippet = _strip_html(snippet)[:400]
            results_lines.append(f"- **{title}**")
            results_lines.append(f"  - URL: {url}")
            if snippet:
                results_lines.append(f"  - Snippet: {snippet}")

        results_lines.append("")
        results_lines.append(
            "If you want, I can also produce a **migration TAM estimate** by triangulating these sources (and explicitly flagging confidence/assumptions)."
        )
        return "\n".join(results_lines)

    except Exception as e:
        return f"Install-base search failed: {str(e)}"


@tool
def competitor_service_snapshot(competitor_name: str) -> str:
    """
    Snapshot a competitor's official product/pricing messaging from their own pages.

    This is designed for campaign positioning (e.g., what Weebly emphasizes today).
    """
    competitor = get_competitor(competitor_name)
    if not competitor:
        available = ", ".join([c.name for c in COMPETITORS])
        return f"Unknown competitor '{competitor_name}'. Available: {available}"

    urls = [
        f"https://{competitor.domain}/",
        competitor.pricing_url,
        competitor.blog_url,
    ]
    urls = [u for u in urls if u]

    sections: list[str] = [f"## Official Service Snapshot: {competitor.name}", ""]
    with httpx.Client(follow_redirects=True, timeout=settings.TIMEOUT) as client:
        for url in urls:
            try:
                r = client.get(url, headers={"User-Agent": "research-assistant/0.1 (+snapshot)"})
                if r.status_code >= 400 or not r.text:
                    sections.append(f"### {url}\n- Status: HTTP {r.status_code}\n")
                    continue

                text = _strip_html(r.text)
                excerpt = text[:1200]
                sections.append(f"### {url}")
                sections.append(f"- Status: HTTP {r.status_code}")
                sections.append(f"- Excerpt: {excerpt}")
                sections.append("")
            except Exception as e:
                sections.append(f"### {url}\n- Error: {str(e)}\n")

    return "\n".join(sections)
