"""Tool definitions for external API access."""

from .web_search import web_search
from .wikipedia import wikipedia_search
from .competitor_news import (
    competitor_news,
    competitor_features,
    competitor_install_base,
    competitor_service_snapshot,
    list_competitors,
)
from .financial_data import (
    competitor_financial_overview,
    competitor_stock_price,
)

__all__ = [
    "web_search",
    "wikipedia_search",
    "competitor_news",
    "competitor_features",
    "competitor_install_base",
    "competitor_service_snapshot",
    "list_competitors",
    "competitor_financial_overview",
    "competitor_stock_price",
]
