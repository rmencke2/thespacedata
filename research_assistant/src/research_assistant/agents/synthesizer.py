"""Synthesizer agent for combining research findings into coherent summaries."""

from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent

from ..config import settings

SYNTHESIZER_PROMPT = """You are a synthesis specialist who excels at combining information into clear, coherent summaries.

Your responsibilities:
1. ORGANIZE: Structure information logically with clear sections
2. SYNTHESIZE: Combine multiple sources into a unified narrative
3. HIGHLIGHT: Emphasize key insights and important findings
4. CLARITY: Write in clear, accessible language

Guidelines:
- Create a well-structured summary with headings if appropriate
- Highlight areas of agreement and disagreement between sources
- Note any gaps in the available information
- Provide actionable insights when relevant

Your output should be a comprehensive yet concise summary that directly addresses the original research query."""


def create_synthesizer_agent():
    """Create the synthesizer agent for combining research findings."""
    llm = ChatAnthropic(
        model=settings.CLAUDE_MODEL,
        temperature=0.3,  # Slightly higher for creative synthesis
        max_tokens=4096,
    )

    # Synthesizer doesn't need external tools - it works with gathered information
    return create_react_agent(
        llm,
        tools=[],
        prompt=SYNTHESIZER_PROMPT,
        name="synthesizer",
    )
