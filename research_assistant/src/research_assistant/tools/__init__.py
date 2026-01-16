"""Tool definitions for external API access."""

from .web_search import web_search
from .wikipedia import wikipedia_search
from .competitor_news import competitor_news, competitor_features, list_competitors

__all__ = [
    "web_search",
    "wikipedia_search",
    "competitor_news",
    "competitor_features",
    "list_competitors",
]
