"""LangGraph workflow for the multi-agent research assistant."""

from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage

from ..config import settings
from ..agents import (
    create_researcher_agent,
    create_synthesizer_agent,
    create_fact_checker_agent,
)
from .state import ResearchState

SUPERVISOR_PROMPT = """You are a research supervisor coordinating a team of specialized agents.

Your team:
- researcher: Gathers information from web searches and Wikipedia
- synthesizer: Combines findings into coherent summaries
- fact_checker: Verifies important claims

Your job is to:
1. Analyze the user's research query
2. Delegate to the appropriate agent
3. Decide when the research is complete

Workflow guidance:
- ALWAYS start with the researcher to gather information
- Use the synthesizer after sufficient information is gathered
- Use fact_checker for controversial or critical claims (optional)
- Complete when a good synthesis has been produced

Respond with the name of the next agent to call, or "FINISH" if research is complete."""


def build_research_workflow(checkpointer=None):
    """Build the complete research workflow graph.

    Args:
        checkpointer: Optional checkpointer for conversation memory.
                     Defaults to MemorySaver for in-memory persistence.

    Returns:
        Compiled LangGraph workflow
    """
    # Create the agents
    researcher = create_researcher_agent()
    synthesizer = create_synthesizer_agent()
    fact_checker = create_fact_checker_agent()

    # Create supervisor LLM
    supervisor_llm = ChatAnthropic(
        model=settings.CLAUDE_MODEL,
        temperature=0.2,
    )

    # Build the graph
    workflow = StateGraph(ResearchState)

    # Define node functions
    def supervisor_node(state: ResearchState) -> dict:
        """Supervisor decides which agent to call next."""
        messages = state["messages"]

        # Build context for supervisor
        context = f"Original query: {state.get('query', 'Unknown')}\n"
        if state.get("research_findings"):
            context += f"Research findings gathered: {len(state['research_findings'])}\n"
        if state.get("synthesis"):
            context += "Synthesis: Complete\n"
        if state.get("fact_check_results"):
            context += f"Fact checks: {len(state['fact_check_results'])}\n"

        response = supervisor_llm.invoke(
            [
                {"role": "system", "content": SUPERVISOR_PROMPT},
                {"role": "user", "content": f"{context}\n\nConversation so far:\n{messages[-1].content if messages else 'No messages yet'}\n\nWhich agent should handle this next? (researcher/synthesizer/fact_checker/FINISH)"},
            ]
        )

        return {"next_agent": response.content.strip().lower()}

    def researcher_node(state: ResearchState) -> dict:
        """Run the researcher agent."""
        query = state.get("query", "")
        result = researcher.invoke({"messages": [HumanMessage(content=f"Research this topic: {query}")]})

        # Extract the last message as the research summary
        last_message = result["messages"][-1] if result.get("messages") else None
        content = last_message.content if last_message else "No findings"

        findings = state.get("research_findings", [])
        findings.append({"source": "researcher", "url": None, "content": content})

        return {
            "messages": result.get("messages", []),
            "research_findings": findings,
        }

    def synthesizer_node(state: ResearchState) -> dict:
        """Run the synthesizer agent."""
        query = state.get("query", "")
        findings = state.get("research_findings", [])

        # Format findings for synthesis
        findings_text = "\n\n".join([f"Source: {f['source']}\n{f['content']}" for f in findings])

        result = synthesizer.invoke(
            {
                "messages": [
                    HumanMessage(
                        content=f"Original query: {query}\n\nResearch findings:\n{findings_text}\n\nPlease synthesize these findings into a comprehensive summary."
                    )
                ]
            }
        )

        last_message = result["messages"][-1] if result.get("messages") else None
        synthesis = last_message.content if last_message else None

        return {
            "messages": result.get("messages", []),
            "synthesis": synthesis,
        }

    def fact_checker_node(state: ResearchState) -> dict:
        """Run the fact-checker agent."""
        synthesis = state.get("synthesis", "")

        result = fact_checker.invoke(
            {"messages": [HumanMessage(content=f"Please fact-check the key claims in this summary:\n\n{synthesis}")]}
        )

        last_message = result["messages"][-1] if result.get("messages") else None
        fact_check = last_message.content if last_message else ""

        results = state.get("fact_check_results", [])
        results.append({"claim": "summary", "verified": True, "confidence": 0.8, "sources": [fact_check]})

        return {
            "messages": result.get("messages", []),
            "fact_check_results": results,
        }

    # Add nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("synthesizer", synthesizer_node)
    workflow.add_node("fact_checker", fact_checker_node)

    # Define routing logic
    def route_supervisor(state: dict) -> str:
        """Route based on supervisor decision."""
        next_agent = state.get("next_agent", "").lower()
        if "finish" in next_agent:
            return END
        elif "researcher" in next_agent:
            return "researcher"
        elif "synthesizer" in next_agent:
            return "synthesizer"
        elif "fact_checker" in next_agent or "fact" in next_agent:
            return "fact_checker"
        else:
            # Default to researcher if unclear
            return "researcher"

    # Add edges
    workflow.add_edge(START, "supervisor")
    workflow.add_conditional_edges("supervisor", route_supervisor)
    workflow.add_edge("researcher", "supervisor")
    workflow.add_edge("synthesizer", "supervisor")
    workflow.add_edge("fact_checker", "supervisor")

    # Compile with checkpointer
    if checkpointer is None:
        checkpointer = MemorySaver()

    return workflow.compile(checkpointer=checkpointer)


def run_research(query: str, max_iterations: int = 10) -> dict:
    """Execute a research query and return results.

    Args:
        query: The research question or topic
        max_iterations: Maximum number of agent iterations

    Returns:
        Final state with research findings and synthesis
    """
    workflow = build_research_workflow()

    config = {"configurable": {"thread_id": "research-session"}, "recursion_limit": max_iterations * 3}

    initial_state: ResearchState = {
        "messages": [HumanMessage(content=query)],
        "query": query,
        "research_findings": [],
        "synthesis": None,
        "fact_check_results": [],
    }

    result = workflow.invoke(initial_state, config=config)

    return result
