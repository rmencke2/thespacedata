"""Command-line interface for the research assistant."""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from typing import Optional
from datetime import datetime
from pathlib import Path

from . import __version__
from .config import validate_config, ConfigError
from .graph.workflow import run_research
from .graph.competitor_workflow import run_competitor_report
from .competitors import COMPETITORS, get_all_competitor_names
from .email_sender import send_report_email, EmailConfig

app = typer.Typer(
    name="research-assistant",
    help="Multi-agent research assistant powered by Claude and LangGraph",
    add_completion=True,
)
console = Console()


def print_error(message: str) -> None:
    """Print error message in red."""
    console.print(f"[bold red]Error:[/] {message}")


def print_success(message: str) -> None:
    """Print success message in green."""
    console.print(f"[bold green]Success:[/] {message}")


@app.callback()
def main_callback() -> None:
    """Validate configuration on startup."""
    try:
        validate_config()
    except ConfigError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command()
def research(
    query: str = typer.Argument(..., help="The research question or topic"),
    max_iterations: int = typer.Option(
        10, "--max-iter", "-m", help="Maximum agent iterations"
    ),
    output_file: Optional[str] = typer.Option(
        None, "--output", "-o", help="Save results to markdown file"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show detailed agent activity"
    ),
) -> None:
    """
    Research a topic using multiple AI agents.

    The research assistant will:
    1. Search multiple sources for relevant information
    2. Synthesize findings into a coherent summary
    3. Optionally fact-check key claims

    Example:
        research-assistant research "What are the latest developments in quantum computing?"
    """
    console.print(Panel(f"[bold]Researching:[/] {query}", style="blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task(description="Agents working...", total=None)

        try:
            result = run_research(query, max_iterations)
        except Exception as e:
            print_error(f"Research failed: {e}")
            if verbose:
                console.print_exception()
            raise typer.Exit(1)

    # Display results
    synthesis = result.get("synthesis")
    if synthesis:
        console.print(Panel(Markdown(synthesis), title="Research Results", border_style="green"))
    else:
        # Fall back to showing research findings
        findings = result.get("research_findings", [])
        if findings:
            content = "\n\n---\n\n".join([f["content"] for f in findings])
            console.print(Panel(Markdown(content), title="Research Findings", border_style="yellow"))
        else:
            console.print("[yellow]No results generated.[/]")

    # Show statistics
    findings_count = len(result.get("research_findings", []))
    fact_checks = len(result.get("fact_check_results", []))
    console.print(f"\n[dim]Sources consulted: {findings_count} | Fact checks: {fact_checks}[/]")

    # Save to file if requested
    if output_file:
        output_content = synthesis or "No synthesis generated."
        with open(output_file, "w") as f:
            f.write(f"# Research: {query}\n\n{output_content}")
        print_success(f"Results saved to {output_file}")


@app.command()
def interactive() -> None:
    """Start an interactive research session (REPL mode)."""
    console.print(
        Panel(
            "[bold]Interactive Research Session[/]\n\nType your research questions.\nType 'quit' or 'exit' to end.",
            style="bold blue",
        )
    )

    while True:
        try:
            query = console.input("\n[bold cyan]Research> [/]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Session ended.[/]")
            break

        if query.lower().strip() in ("quit", "exit", "q"):
            console.print("[dim]Session ended.[/]")
            break

        if not query.strip():
            continue

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            progress.add_task(description="Researching...", total=None)
            try:
                result = run_research(query)
            except Exception as e:
                print_error(f"Research failed: {e}")
                continue

        synthesis = result.get("synthesis")
        if synthesis:
            console.print(Panel(Markdown(synthesis), title="Results"))
        else:
            findings = result.get("research_findings", [])
            if findings:
                content = findings[-1]["content"] if findings else "No findings"
                console.print(Panel(Markdown(content), title="Findings"))


@app.command()
def competitors(
    competitor: Optional[str] = typer.Argument(
        None, help="Specific competitor to analyze (or 'all' for full report)"
    ),
    output_file: Optional[str] = typer.Option(
        None, "--output", "-o", help="Save report to markdown file"
    ),
    focus: Optional[str] = typer.Option(
        None, "--focus", "-f", help="Focus area: features, pricing, news, or all"
    ),
) -> None:
    """
    Generate competitive intelligence report for Webnode.

    Monitors: Wix, Duda, GoDaddy, Hostinger, One.com, Basekit, Squarespace, Weebly

    Examples:
        research-assistant competitors              # Quick report on all
        research-assistant competitors Wix          # Focus on Wix only
        research-assistant competitors --focus pricing  # Focus on pricing changes
        research-assistant competitors -o report.md # Save to file
    """
    # Determine which competitors to analyze
    if competitor and competitor.lower() != "all":
        competitor_list = [competitor]
        title = f"Competitor Intelligence: {competitor}"
    else:
        competitor_list = get_all_competitor_names()
        title = "Weekly Competitor Intelligence Report"

    # Determine focus areas
    if focus:
        focus_areas = [focus] if focus != "all" else ["features", "pricing", "news"]
    else:
        focus_areas = ["features", "pricing", "news"]

    console.print(Panel(f"[bold]{title}[/]\n\nAnalyzing: {', '.join(competitor_list)}\nFocus: {', '.join(focus_areas)}", style="blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task(description="Gathering competitive intelligence...", total=None)

        try:
            result = run_competitor_report(
                competitors=competitor_list,
                focus_areas=focus_areas,
            )
        except Exception as e:
            print_error(f"Report generation failed: {e}")
            console.print_exception()
            raise typer.Exit(1)

    # Display report
    report = result.get("report")
    if report:
        console.print(Panel(Markdown(report), title=title, border_style="green"))
    else:
        # Show raw findings if no synthesis
        findings = result.get("findings", {})
        for comp, finding in findings.items():
            console.print(Panel(Markdown(finding), title=comp, border_style="yellow"))

    # Show statistics
    findings_count = len(result.get("findings", {}))
    console.print(f"\n[dim]Competitors analyzed: {findings_count}[/]")

    # Save to file if requested
    if output_file:
        today = datetime.now().strftime("%Y-%m-%d")
        output_content = report or "No report generated."

        # Add metadata header
        full_report = f"""# Webnode Competitive Intelligence Report
Generated: {today}
Competitors: {', '.join(competitor_list)}
Focus Areas: {', '.join(focus_areas)}

---

{output_content}
"""
        with open(output_file, "w") as f:
            f.write(full_report)
        print_success(f"Report saved to {output_file}")


@app.command(name="list-competitors")
def list_competitors_cmd() -> None:
    """List all monitored competitors."""
    table = Table(title="Monitored Competitors (Webnode)")
    table.add_column("Name", style="cyan")
    table.add_column("Domain", style="green")
    table.add_column("Pricing URL")
    table.add_column("Blog URL")

    for c in COMPETITORS:
        table.add_row(
            c.name,
            c.domain,
            c.pricing_url or "-",
            c.blog_url or "-",
        )

    console.print(table)


@app.command()
def weekly_report(
    output_dir: str = typer.Option(
        "./reports", "--output-dir", "-d", help="Directory to save reports"
    ),
    send_email: bool = typer.Option(
        True, "--email/--no-email", help="Send report via email"
    ),
    email_to: Optional[str] = typer.Option(
        None, "--to", help="Override recipient email address"
    ),
) -> None:
    """
    Generate the full weekly competitive intelligence report.

    This is designed to be run weekly (e.g., via cron) to generate
    comprehensive competitive intelligence for Webnode leadership.

    Example cron entry (every Tuesday at 8am Milan time):
        0 8 * * 2 cd /path/to/project && research-assistant weekly-report
    """
    today = datetime.now().strftime("%Y-%m-%d")
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    filename = output_path / f"competitor-report-{today}.md"

    console.print(Panel(
        f"[bold]Generating Weekly Competitive Intelligence Report[/]\n\n"
        f"Date: {today}\n"
        f"Output: {filename}\n"
        f"Email: {'Yes' if send_email else 'No'}",
        style="blue"
    ))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(description="Analyzing all competitors...", total=len(COMPETITORS))

        try:
            result = run_competitor_report()
        except Exception as e:
            print_error(f"Report generation failed: {e}")
            raise typer.Exit(1)

    report = result.get("report", "No report generated.")

    # Create comprehensive report
    full_report = f"""# Webnode Weekly Competitive Intelligence Report

**Generated:** {today}
**Prepared for:** Webnode Leadership Team

---

{report}

---

## Competitors Monitored

{chr(10).join([f"- {c.name} ({c.domain})" for c in COMPETITORS])}

---

*This report was automatically generated by the Webnode Competitive Intelligence System.*
"""

    # Save to file
    with open(filename, "w") as f:
        f.write(full_report)
    print_success(f"Weekly report saved to {filename}")

    # Send email if requested
    if send_email:
        try:
            email_config = EmailConfig.from_env()
            if not email_config.is_configured():
                console.print("[yellow]Email not configured. Set SMTP_HOST, SMTP_USER, SMTP_PASSWORD, EMAIL_FROM, EMAIL_TO in .env[/]")
            else:
                console.print("[dim]Sending email...[/]")
                send_report_email(report, to_email=email_to)
                recipient = email_to or email_config.to_email
                print_success(f"Report emailed to {recipient}")
        except Exception as e:
            print_error(f"Failed to send email: {e}")

    console.print(Panel(Markdown(report), title="Report Preview", border_style="green"))


@app.command()
def version() -> None:
    """Show version information."""
    console.print(f"research-assistant v{__version__}")
    console.print("[dim]Powered by Claude and LangGraph[/]")
    console.print("[dim]Configured for Webnode competitive intelligence[/]")


if __name__ == "__main__":
    app()
