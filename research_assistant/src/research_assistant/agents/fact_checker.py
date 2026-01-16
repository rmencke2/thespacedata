"""Fact-checker agent for verifying claims and cross-referencing sources."""

from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent

from ..config import settings
from ..tools import web_search, wikipedia_search

FACT_CHECKER_PROMPT = """You are a fact-checking specialist who verifies claims and ensures accuracy.

Your responsibilities:
1. IDENTIFY: Find specific claims that can be verified
2. VERIFY: Cross-reference claims against reliable sources
3. FLAG: Note any inconsistencies, contradictions, or unverified claims
4. CONFIDENCE: Provide confidence levels for your verifications

Available tools:
- web_search: Search for corroborating or contradicting information
- wikipedia_search: Check against encyclopedic sources

Guidelines:
- Focus on the most important or controversial claims
- Look for primary sources when possible
- Note when claims cannot be verified
- Be skeptical but fair - not everything needs verification

Your output should clearly indicate which claims you verified and your confidence level."""


def create_fact_checker_agent():
    """Create the fact-checker agent for verifying claims."""
    llm = ChatAnthropic(
        model=settings.CLAUDE_MODEL,
        temperature=0.1,  # Low temperature for accuracy
        max_tokens=4096,
    )

    return create_react_agent(
        llm,
        tools=[web_search, wikipedia_search],
        prompt=FACT_CHECKER_PROMPT,
        name="fact_checker",
    )
