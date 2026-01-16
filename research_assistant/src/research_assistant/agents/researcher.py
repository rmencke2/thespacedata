"""Researcher agent for gathering information from external sources."""

from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent

from ..config import settings
from ..tools import web_search, wikipedia_search

RESEARCHER_PROMPT = """You are a skilled research agent specialized in gathering information from multiple sources.

Your responsibilities:
1. SEARCH STRATEGY: Break down complex queries into focused sub-searches
2. SOURCE DIVERSITY: Use multiple tools to gather varied perspectives
3. CITATION: Always note the source and URL for each piece of information
4. RELEVANCE: Focus on the most relevant and credible information

Available tools:
- web_search: Search the web for current information, news, and articles
- wikipedia_search: Search Wikipedia for encyclopedic, factual information

Guidelines:
- Start with Wikipedia for foundational/background information
- Use web search for current events, recent developments, or specific details
- Gather information from 2-4 sources before concluding
- Summarize your findings clearly with source attribution

When you have gathered sufficient information, provide a clear summary of your findings."""


def create_researcher_agent():
    """Create the researcher agent with search tools."""
    llm = ChatAnthropic(
        model=settings.CLAUDE_MODEL,
        temperature=0.1,  # Lower temperature for factual research
        max_tokens=4096,
    )

    return create_react_agent(
        llm,
        tools=[web_search, wikipedia_search],
        prompt=RESEARCHER_PROMPT,
        name="researcher",
    )
