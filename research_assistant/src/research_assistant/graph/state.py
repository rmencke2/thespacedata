"""State schema definitions for the research workflow."""

from typing import Annotated, TypedDict
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage


class ResearchFinding(TypedDict):
    """Individual research finding from a source."""

    source: str
    url: str | None
    content: str


class FactCheckResult(TypedDict):
    """Result of fact-checking a claim."""

    claim: str
    verified: bool
    confidence: float
    sources: list[str]


class ResearchState(TypedDict):
    """Main state schema for the research workflow.

    This state is shared across all agents in the supervisor workflow.
    """

    # Message history - uses add_messages reducer to append new messages
    messages: Annotated[list[BaseMessage], add_messages]

    # Original user query
    query: str

    # Accumulated research findings from the researcher agent
    research_findings: list[ResearchFinding]

    # Synthesized summary from the synthesizer agent
    synthesis: str | None

    # Fact-check results from the fact-checker agent
    fact_check_results: list[FactCheckResult]
