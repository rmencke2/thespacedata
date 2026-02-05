"""Tool for fetching financial data for public competitors."""

from datetime import datetime, timedelta
from langchain_core.tools import tool
from typing import Optional

from ..competitors import COMPETITORS, get_competitor


@tool
def competitor_financial_overview(competitor_name: str) -> str:
    """
    Get comprehensive financial overview for a public competitor.

    Fetches:
    - Current stock price and recent price movement
    - Cash and cash equivalents balance
    - Cash flow (operating, investing, financing)
    - Profit margins (gross, operating, net)
    - Recent stock-related news that may have affected price

    Args:
        competitor_name: Name of the competitor (e.g., "Wix", "GoDaddy", "Squarespace")

    Returns:
        Financial overview including stock price, financial metrics, and relevant news
    """
    competitor = get_competitor(competitor_name)
    if not competitor:
        available = ", ".join([c.name for c in COMPETITORS])
        return f"Unknown competitor '{competitor_name}'. Available: {available}"

    if not competitor.ticker:
        return f"{competitor.name} is not a public company (no ticker symbol available)."

    try:
        import yfinance as yf
    except ImportError:
        return (
            f"[Financial Data - yfinance not installed]\n\n"
            f"To fetch financial data for {competitor.name} ({competitor.ticker}), install yfinance:\n"
            f"  pip install yfinance\n\n"
            f"Then rerun the financial overview tool."
        )

    try:
        ticker = yf.Ticker(competitor.ticker)
        info = ticker.info

        # Get current stock price and recent data
        hist = ticker.history(period="1mo")
        current_price = info.get("currentPrice") or info.get("regularMarketPrice")
        previous_close = info.get("previousClose")
        day_change = None
        day_change_pct = None
        if current_price and previous_close:
            day_change = current_price - previous_close
            day_change_pct = (day_change / previous_close) * 100

        # Get 52-week range
        week_52_high = info.get("fiftyTwoWeekHigh")
        week_52_low = info.get("fiftyTwoWeekLow")

        # Get financial statements
        financials = ticker.financials
        balance_sheet = ticker.balance_sheet
        cashflow = ticker.cashflow

        # Extract key metrics
        # Cash and cash equivalents (most recent quarter)
        # Try info dict first, then balance sheet
        cash_balance = info.get("totalCash") or info.get("cashAndCashEquivalents")
        if cash_balance is None and balance_sheet is not None and not balance_sheet.empty:
            cash_row = balance_sheet.index[
                balance_sheet.index.str.contains("Cash", case=False, na=False)
            ]
            if len(cash_row) > 0:
                cash_balance = balance_sheet.loc[cash_row[0]].iloc[0] if len(cash_row) > 0 else None

        # Operating cash flow (most recent quarter)
        # Try info dict first, then cashflow statement
        operating_cashflow = info.get("operatingCashflow")
        if operating_cashflow is None and cashflow is not None and not cashflow.empty:
            # Try multiple possible row names
            ocf_patterns = [
                "Operating Cash Flow",
                "Operating Activities",
                "Total Cash From Operating Activities",
                "Cash From Operating Activities",
            ]
            for pattern in ocf_patterns:
                ocf_row = cashflow.index[
                    cashflow.index.str.contains(pattern, case=False, na=False)
                ]
                if len(ocf_row) > 0:
                    operating_cashflow = cashflow.loc[ocf_row[0]].iloc[0]
                    break

        # Profit margins (most recent quarter)
        gross_margin = info.get("grossMargins")
        operating_margin = info.get("operatingMargins")
        profit_margin = info.get("profitMargins")

        # Revenue and earnings
        revenue = info.get("totalRevenue")
        net_income = info.get("netIncomeToCommon")

        # Market cap
        market_cap = info.get("marketCap")

        # Get recent news
        news_items = ticker.news[:5]  # Last 5 news items

        # Build report
        lines = [f"# Financial Overview: {competitor.name} ({competitor.ticker})", ""]

        # Stock Price Section
        lines.append("## Stock Price")
        if current_price:
            lines.append(f"- **Current Price:** ${current_price:.2f}")
            if previous_close:
                lines.append(f"- **Previous Close:** ${previous_close:.2f}")
            if day_change is not None:
                sign = "+" if day_change >= 0 else ""
                color_indicator = "📈" if day_change >= 0 else "📉"
                lines.append(
                    f"- **Day Change:** {sign}${day_change:.2f} ({sign}{day_change_pct:.2f}%) {color_indicator}"
                )
        if week_52_high and week_52_low:
            lines.append(f"- **52-Week Range:** ${week_52_low:.2f} - ${week_52_high:.2f}")
        if market_cap:
            market_cap_b = market_cap / 1e9
            lines.append(f"- **Market Cap:** ${market_cap_b:.2f}B")
        lines.append("")

        # Financial Metrics Section
        lines.append("## Financial Metrics")
        if revenue:
            revenue_b = revenue / 1e9
            lines.append(f"- **Revenue (TTM):** ${revenue_b:.2f}B")
        if net_income:
            net_income_m = net_income / 1e6
            sign = "" if net_income >= 0 else "-"
            lines.append(f"- **Net Income (TTM):** {sign}${abs(net_income_m):.2f}M")
        if cash_balance:
            cash_balance_m = cash_balance / 1e6
            lines.append(f"- **Cash & Cash Equivalents:** ${cash_balance_m:.2f}M")
        if operating_cashflow:
            ocf_m = operating_cashflow / 1e6
            sign = "" if operating_cashflow >= 0 else "-"
            lines.append(f"- **Operating Cash Flow (Latest Quarter):** {sign}${abs(ocf_m):.2f}M")
        lines.append("")

        # Profit Margins Section
        lines.append("## Profit Margins")
        if gross_margin is not None:
            lines.append(f"- **Gross Margin:** {gross_margin * 100:.2f}%")
        if operating_margin is not None:
            lines.append(f"- **Operating Margin:** {operating_margin * 100:.2f}%")
        if profit_margin is not None:
            lines.append(f"- **Net Profit Margin:** {profit_margin * 100:.2f}%")
        if not any([gross_margin, operating_margin, profit_margin]):
            lines.append("- Margin data not available")
        lines.append("")

        # Recent Stock-Related News
        if news_items:
            lines.append("## Recent Stock-Related News")
            lines.append("")
            for news in news_items:
                title = news.get("title", "No title")
                link = news.get("link", "")
                pub_date = news.get("providerPublishTime", 0)
                if pub_date:
                    pub_date_str = datetime.fromtimestamp(pub_date).strftime("%Y-%m-%d")
                else:
                    pub_date_str = "Unknown date"
                publisher = news.get("publisher", "Unknown")
                lines.append(f"### {title}")
                lines.append(f"- **Published:** {pub_date_str} ({publisher})")
                lines.append(f"- **Link:** {link}")
                lines.append("")
        else:
            lines.append("## Recent Stock-Related News")
            lines.append("- No recent news available")
            lines.append("")

        # Add data freshness note
        lines.append("---")
        lines.append(f"*Data as of {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC*")
        lines.append("*Financial data sourced from Yahoo Finance*")

        return "\n".join(lines)

    except Exception as e:
        return (
            f"Error fetching financial data for {competitor.name} ({competitor.ticker}): {str(e)}\n\n"
            f"This could be due to:\n"
            f"- Invalid ticker symbol\n"
            f"- Network issues\n"
            f"- Yahoo Finance API limitations\n"
        )


@tool
def competitor_stock_price(competitor_name: str) -> str:
    """
    Get current stock price and recent price movement for a public competitor.

    Args:
        competitor_name: Name of the competitor (e.g., "Wix", "GoDaddy", "Squarespace")

    Returns:
        Current stock price, change, and recent trend
    """
    competitor = get_competitor(competitor_name)
    if not competitor:
        available = ", ".join([c.name for c in COMPETITORS])
        return f"Unknown competitor '{competitor_name}'. Available: {available}"

    if not competitor.ticker:
        return f"{competitor.name} is not a public company (no ticker symbol available)."

    try:
        import yfinance as yf
    except ImportError:
        return (
            f"[Stock Price - yfinance not installed]\n\n"
            f"To fetch stock price for {competitor.name} ({competitor.ticker}), install yfinance:\n"
            f"  pip install yfinance\n"
        )

    try:
        ticker = yf.Ticker(competitor.ticker)
        info = ticker.info

        current_price = info.get("currentPrice") or info.get("regularMarketPrice")
        previous_close = info.get("previousClose")
        day_change = None
        day_change_pct = None
        if current_price and previous_close:
            day_change = current_price - previous_close
            day_change_pct = (day_change / previous_close) * 100

        # Get recent history for trend
        hist = ticker.history(period="5d")
        week_ago_price = None
        if not hist.empty and len(hist) > 1:
            week_ago_price = hist["Close"].iloc[0]

        lines = [f"# Stock Price: {competitor.name} ({competitor.ticker})", ""]

        if current_price:
            lines.append(f"**Current Price:** ${current_price:.2f}")
            if previous_close:
                lines.append(f"**Previous Close:** ${previous_close:.2f}")
            if day_change is not None:
                sign = "+" if day_change >= 0 else ""
                color_indicator = "📈" if day_change >= 0 else "📉"
                lines.append(
                    f"**Day Change:** {sign}${day_change:.2f} ({sign}{day_change_pct:.2f}%) {color_indicator}"
                )
            if week_ago_price:
                week_change = current_price - week_ago_price
                week_change_pct = (week_change / week_ago_price) * 100
                sign = "+" if week_change >= 0 else ""
                lines.append(
                    f"**5-Day Change:** {sign}${week_change:.2f} ({sign}{week_change_pct:.2f}%)"
                )

        week_52_high = info.get("fiftyTwoWeekHigh")
        week_52_low = info.get("fiftyTwoWeekLow")
        if week_52_high and week_52_low:
            lines.append(f"**52-Week Range:** ${week_52_low:.2f} - ${week_52_high:.2f}")

        return "\n".join(lines)

    except Exception as e:
        return f"Error fetching stock price for {competitor.name} ({competitor.ticker}): {str(e)}"
