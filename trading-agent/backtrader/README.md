# LangGraph Stock Trading Agent System

A multi-agent trading system built with LangGraph for algorithmic trading with Alpaca.

## Features

- 🤖 Multi-agent architecture with LangGraph
- 📊 Multiple trading strategies (mean reversion, momentum, pairs trading)
- 🎯 Risk management and position sizing
- 📈 Backtesting framework
- 📄 Paper trading with Alpaca (FREE)
- 💾 SQLite for trade logging
- 🔄 Can run 24/7 locally

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Alpaca API Keys (FREE)

1. Sign up at https://alpaca.markets/
2. Go to Paper Trading
3. Generate API keys
4. Add to `.env` file

### 3. Configure

Create a `.env` file:

```
ALPACA_API_KEY=your_paper_trading_key
ALPACA_SECRET_KEY=your_paper_trading_secret
ALPACA_BASE_URL=https://paper-api.alpaca.markets
```

### 4. Run Backtest

```bash
python run_backtest.py
```

### 5. Run Live Paper Trading

```bash
python run_live.py
```

## Architecture

```
┌─────────────────────────────────────────────┐
│         LangGraph Orchestrator              │
└─────────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
┌─────────────┐ ┌──────────┐ ┌──────────────┐
│   Market    │ │ Strategy │ │     Risk     │
│   Analyzer  │ │  Agent   │ │   Manager    │
└─────────────┘ └──────────┘ └──────────────┘
        │           │           │
        └───────────┼───────────┘
                    ▼
            ┌──────────────┐
            │  Execution   │
            │    Agent     │
            └──────────────┘
                    │
                    ▼
            ┌──────────────┐
            │    Alpaca    │
            │   API (Paper)│
            └──────────────┘
```

## Strategies Included

1. **Mean Reversion**: Buy dips, sell rallies
2. **Momentum**: Ride trends
3. **Pairs Trading**: Market-neutral long/short

## Risk Management

- Max 2% risk per trade
- Position sizing based on volatility
- Stop-loss on every position
- Max 5 concurrent positions
- Daily loss limit

## Files Structure

```
trading-agent/
├── agents/
│   ├── market_analyzer.py    # Market analysis agent
│   ├── strategy_agent.py     # Strategy signal generation
│   ├── risk_manager.py       # Risk management
│   └── execution_agent.py    # Order execution
├── strategies/
│   ├── mean_reversion.py
│   ├── momentum.py
│   └── pairs_trading.py
├── utils/
│   ├── data_fetcher.py       # Get market data
│   ├── database.py           # Trade logging
│   └── config.py             # Configuration
├── graph_builder.py          # LangGraph setup
├── run_backtest.py           # Backtest runner
├── run_live.py               # Live trading runner
└── requirements.txt
```

## Monitoring

- Trades logged to `trades.db` (SQLite)
- Daily performance reports
- Position tracking

## Safety Features

- Paper trading only (no real money)
- Automatic stop-loss
- Position limits
- Daily loss limits
- Manual kill switch (Ctrl+C)

## Next Steps After 1 Week

1. Review performance metrics
2. Optimize strategy parameters
3. Add more strategies
4. Consider moving to real trading (small amounts)
