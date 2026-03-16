"""Competitor configuration for Webnode competitive intelligence."""

from dataclasses import dataclass


@dataclass
class Competitor:
    """A competitor to monitor."""

    name: str
    domain: str
    pricing_url: str | None = None
    blog_url: str | None = None
    keywords: list[str] | None = None
    ticker: str | None = None  # Stock ticker symbol for public companies (e.g., "WIX", "GDDY")


# Webnode's competitors
COMPETITORS = [
    Competitor(
        name="Wix",
        domain="wix.com",
        pricing_url="https://www.wix.com/upgrade/website",
        blog_url="https://www.wix.com/blog",
        keywords=["wix", "wix.com", "wix website builder"],
        ticker="WIX",
    ),
    Competitor(
        name="Duda",
        domain="duda.co",
        pricing_url="https://www.duda.co/pricing",
        blog_url="https://blog.duda.co",
        keywords=["duda", "duda.co", "duda website builder"],
    ),
    Competitor(
        name="GoDaddy",
        domain="godaddy.com",
        pricing_url="https://www.godaddy.com/websites/website-builder",
        blog_url="https://www.godaddy.com/resources",
        keywords=["godaddy", "godaddy website builder", "godaddy websites"],
        ticker="GDDY",
    ),
    Competitor(
        name="Hostinger",
        domain="hostinger.com",
        pricing_url="https://www.hostinger.com/website-builder",
        blog_url="https://www.hostinger.com/blog",
        keywords=["hostinger", "hostinger website builder"],
    ),
    Competitor(
        name="One.com",
        domain="one.com",
        pricing_url="https://www.one.com/en/website-builder",
        blog_url="https://www.one.com/en/blog",
        keywords=["one.com", "one.com website builder"],
    ),
    Competitor(
        name="Basekit",
        domain="basekit.com",
        pricing_url="https://www.basekit.com",
        blog_url="https://www.basekit.com/blog",
        keywords=["basekit", "basekit website builder"],
    ),
    Competitor(
        name="Squarespace",
        domain="squarespace.com",
        pricing_url="https://www.squarespace.com/pricing",
        blog_url="https://www.squarespace.com/blog",
        keywords=["squarespace", "squarespace website builder"],
        ticker="SQSP",
    ),
    Competitor(
        name="Weebly",
        domain="weebly.com",
        pricing_url="https://www.weebly.com/pricing",
        blog_url="https://www.weebly.com/blog",
        keywords=["weebly", "weebly website builder"],
    ),
]


def get_competitor(name: str) -> Competitor | None:
    """Get a competitor by name (case-insensitive)."""
    name_lower = name.lower()
    for c in COMPETITORS:
        if c.name.lower() == name_lower or c.domain.lower() == name_lower:
            return c
    return None


def get_all_competitor_names() -> list[str]:
    """Get list of all competitor names."""
    return [c.name for c in COMPETITORS]
