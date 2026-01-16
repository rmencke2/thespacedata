"""Competitor analyst agent for monitoring website builder competitors."""

from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent

from ..config import settings
from ..tools.competitor_news import competitor_news, competitor_features, list_competitors
from ..tools.web_search import web_search
from ..tools.wikipedia import wikipedia_search

COMPETITOR_ANALYST_PROMPT = """You are a competitive intelligence analyst for Webnode, a website builder company.

Your job is to monitor competitors and identify:
1. NEW FEATURES: Product launches, feature updates, capability improvements
2. PRICING CHANGES: New plans, price adjustments, promotional offers
3. STRATEGIC MOVES: Partnerships, acquisitions, market expansion
4. MARKET POSITIONING: How competitors are positioning themselves

Competitors you monitor:
- Wix (wix.com) - Major player, frequent feature releases
- Duda (duda.co) - Agency-focused, white-label solutions
- GoDaddy (godaddy.com) - Domain + hosting + builder
- Hostinger (hostinger.com) - Budget-friendly hosting + builder
- One.com (one.com) - European market focus
- Basekit (basekit.com) - White-label platform
- Squarespace (squarespace.com) - Design-focused
- Weebly (weebly.com) - Square-owned, e-commerce focus

Available tools:
- competitor_news: Search recent news for a specific competitor
- competitor_features: Find feature announcements for a competitor
- list_competitors: See all monitored competitors
- web_search: General web search
- wikipedia_search: Background information

Guidelines:
- Be thorough - check multiple competitors
- Focus on actionable intelligence
- Distinguish between confirmed news and rumors
- Note the source and date for each finding
- Prioritize recent developments (last 7 days for weekly reports)

Format your findings clearly with sections for each competitor."""


def create_competitor_analyst_agent():
    """Create the competitor analyst agent."""
    llm = ChatAnthropic(
        model=settings.CLAUDE_MODEL,
        temperature=0.1,
        max_tokens=8192,  # Larger for comprehensive reports
    )

    return create_react_agent(
        llm,
        tools=[
            competitor_news,
            competitor_features,
            list_competitors,
            web_search,
            wikipedia_search,
        ],
        prompt=COMPETITOR_ANALYST_PROMPT,
        name="competitor_analyst",
    )
