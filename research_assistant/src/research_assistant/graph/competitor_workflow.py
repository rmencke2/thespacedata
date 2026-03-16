"""LangGraph workflow for competitor intelligence gathering."""

from datetime import datetime
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage
from typing import Annotated, TypedDict

from langgraph.graph import add_messages

from ..config import settings
from ..agents.competitor_analyst import create_competitor_analyst_agent
from ..agents.synthesizer import create_synthesizer_agent
from ..competitors import COMPETITORS, get_all_competitor_names


class CompetitorReportState(TypedDict):
    """State for competitor intelligence workflow."""

    messages: Annotated[list, add_messages]
    competitors_to_check: list[str]
    current_competitor: str | None
    findings: dict[str, str]  # competitor -> findings
    report: str | None
    focus_areas: list[str]  # features, pricing, partnerships, etc.


def build_competitor_workflow(checkpointer=None):
    """Build the competitor intelligence workflow.

    This workflow:
    1. Iterates through each competitor
    2. Gathers intelligence on features, pricing, news
    3. Synthesizes findings into an executive report
    """
    analyst = create_competitor_analyst_agent()
    synthesizer_llm = ChatAnthropic(model=settings.CLAUDE_MODEL, temperature=0.2, max_tokens=8192)

    workflow = StateGraph(CompetitorReportState)

    def init_node(state: CompetitorReportState) -> dict:
        """Initialize the workflow with competitors to check."""
        competitors = state.get("competitors_to_check", get_all_competitor_names())
        return {
            "competitors_to_check": competitors,
            "current_competitor": competitors[0] if competitors else None,
            "findings": {},
        }

    def analyst_node(state: CompetitorReportState) -> dict:
        """Run the analyst for the current competitor."""
        competitor = state.get("current_competitor")
        if not competitor:
            return {}

        focus_areas = state.get("focus_areas", ["features", "pricing", "news"])
        focus_str = ", ".join(focus_areas)

        query = f"""Research {competitor} for the following areas: {focus_str}

For each area, find:
- New feature announcements or product updates (last 7-14 days)
- Any pricing changes or new plans
- Major news, partnerships, or strategic moves

If focus includes install_base:
- Find install-base / usage signals (e.g., number of users/sites, market share)
- Prefer credible sources (company filings, reputable market datasets) and cite URLs

If focus includes service:
- Pull current official messaging from {competitor}'s website (home/pricing/blog)
- Summarize positioning relevant to a migration campaign

If {competitor} is a public company (has a stock ticker):
- Use competitor_financial_overview to get comprehensive financial data including:
  * Current stock price and recent price movement
  * Cash balance and cash flow
  * Profit margins (gross, operating, net)
  * Recent stock-related news that may have affected the stock price
- Include a financial overview section in your findings

Be thorough and cite your sources."""

        result = analyst.invoke({"messages": [HumanMessage(content=query)]})

        # Extract findings
        last_message = result["messages"][-1] if result.get("messages") else None
        finding = last_message.content if last_message else f"No findings for {competitor}"

        # Update findings dict
        findings = state.get("findings", {}).copy()
        findings[competitor] = finding

        # Move to next competitor
        competitors = state.get("competitors_to_check", [])
        current_idx = competitors.index(competitor) if competitor in competitors else -1
        next_competitor = competitors[current_idx + 1] if current_idx + 1 < len(competitors) else None

        return {
            "findings": findings,
            "current_competitor": next_competitor,
            "messages": result.get("messages", []),
        }

    def should_continue(state: CompetitorReportState) -> str:
        """Decide whether to continue analyzing or synthesize."""
        if state.get("current_competitor"):
            return "analyst"
        return "synthesize"

    def synthesize_node(state: CompetitorReportState) -> dict:
        """Synthesize all findings into an executive report."""
        findings = state.get("findings", {})

        # Build report prompt
        findings_text = ""
        for competitor, finding in findings.items():
            findings_text += f"\n\n## {competitor}\n{finding}"

        today = datetime.now().strftime("%Y-%m-%d")

        prompt = f"""Create an executive competitive intelligence report for Webnode leadership.

Date: {today}

## Raw Intelligence Gathered:
{findings_text}

## Report Format:

Create a concise, actionable report with:

1. **Executive Summary** (2-3 bullet points of the most important findings)

2. **Key Competitor Moves** - Organized by competitor, highlighting:
   - New features launched
   - Pricing changes
   - Strategic moves (partnerships, acquisitions, etc.)

3. **Financial Overview** - For public competitors (Wix, GoDaddy, Squarespace), include:
   - Current stock price and recent performance
   - Key financial metrics (cash balance, cash flow, profit margins)
   - Recent stock-related news and its potential impact
   - Financial health indicators

4. **Competitive Implications for Webnode** - What should Webnode consider in response?

5. **Items to Watch** - Developments that need continued monitoring

Keep the report concise but actionable. Focus on intelligence that matters for strategic decisions."""

        response = synthesizer_llm.invoke([HumanMessage(content=prompt)])

        return {
            "report": response.content,
            "messages": [AIMessage(content=response.content)],
        }

    # Add nodes
    workflow.add_node("init", init_node)
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("synthesize", synthesize_node)

    # Add edges
    workflow.add_edge(START, "init")
    workflow.add_edge("init", "analyst")
    workflow.add_conditional_edges("analyst", should_continue)
    workflow.add_edge("synthesize", END)

    if checkpointer is None:
        checkpointer = MemorySaver()

    return workflow.compile(checkpointer=checkpointer)


def run_competitor_report(
    competitors: list[str] | None = None,
    focus_areas: list[str] | None = None,
) -> dict:
    """Generate a competitor intelligence report.

    Args:
        competitors: List of competitor names to analyze. Defaults to all.
        focus_areas: Areas to focus on. Defaults to ["features", "pricing", "news"]

    Returns:
        Report state with findings and synthesized report
    """
    workflow = build_competitor_workflow()

    if competitors is None:
        competitors = get_all_competitor_names()

    if focus_areas is None:
        focus_areas = ["features", "pricing", "news"]

    config = {"configurable": {"thread_id": "competitor-report"}, "recursion_limit": 50}

    initial_state: CompetitorReportState = {
        "messages": [],
        "competitors_to_check": competitors,
        "current_competitor": None,
        "findings": {},
        "report": None,
        "focus_areas": focus_areas,
    }

    result = workflow.invoke(initial_state, config=config)
    return result
