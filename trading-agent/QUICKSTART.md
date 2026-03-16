# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies

```bash
cd trading-agent
pip install -r requirements.txt
```

### Step 2: Get Alpaca API Keys (FREE)

1. Go to https://alpaca.markets/
2. Sign up for a free account
3. Navigate to "Paper Trading"
4. Generate API keys
5. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
6. Edit `.env` and paste your keys

### Step 3: Test Configuration

```bash
python -c "from utils.config import Config; Config.print_config(); Config.validate()"
```

### Step 4: Run a Backtest

```bash
python run_backtest.py
```

This will:
- Fetch 2 years of historical data
- Test mean reversion and momentum strategies
- Show you which strategies work best on which stocks

### Step 5: Run Live Paper Trading

**Single test cycle:**
```bash
python run_live.py --mode once
```

**Continuous trading (runs all week):**
```bash
python run_live.py --mode continuous
```

## 📊 What Happens When You Run?

### Backtest Mode
1. Downloads historical data from Yahoo Finance (free)
2. Simulates trades using your strategies
3. Shows win rate, returns, and best trades
4. Helps you tune strategy parameters

### Live Trading Mode
1. **Morning (9:30 AM ET)**: System starts, checks account
2. **Trading (9:35 AM ET)**: Analyzes market, finds opportunities, executes trades
3. **Throughout day**: Monitors positions, checks stop losses
4. **End of day (4:00 PM ET)**: Closes positions if needed, reports performance

## 🎯 Your Trading Strategies

The system uses 2 strategies that complement each other:

### 1. Mean Reversion
- **When**: Price drops 2 standard deviations below 20-day average
- **Action**: Buy (expecting bounce back)
- **Best for**: Range-bound markets, overreactions

### 2. Momentum
- **When**: Fast MA crosses above slow MA
- **Action**: Buy (ride the trend)
- **Best for**: Trending markets, breakouts

## 🛡️ Risk Management

The system is designed to protect your capital:
- **Max risk per trade**: 2% of portfolio
- **Max position size**: 20% of portfolio
- **Stop loss**: 2% below entry on every trade
- **Daily loss limit**: 5% of portfolio
- **Max positions**: 5 at once

## 📈 Monitor Your Performance

Check your trades database:
```bash
python -c "from utils.database import TradingDatabase; db = TradingDatabase(); db.print_summary()"
```

## ⚙️ Customize Your System

Edit `utils/config.py` to change:
- Stock universe (which stocks to trade)
- Risk parameters (position sizes, stop losses)
- Strategy parameters (MA periods, RSI levels)
- Trading schedule

## 🔧 Troubleshooting

**"No module named 'langgraph'"**
→ Run: `pip install -r requirements.txt`

**"Alpaca API keys not set"**
→ Create `.env` file with your keys (see Step 2)

**"No data fetched"**
→ Check your internet connection
→ Try different stock symbols

**Markets closed?**
→ Paper trading works 24/7, but real market hours are Mon-Fri 9:30-16:00 ET

## 📚 Learn More

- Edit strategies in `strategies/` folder
- View logs in `trades.db`
- Adjust risk in `agents/risk_manager.py`
- Change trading universe in `utils/config.py`

## 🎓 After 1 Week

Review your results:
1. Check win rate (target: >50%)
2. Look at best/worst trades
3. Analyze which stocks performed best
4. Adjust strategy parameters
5. Consider adding more strategies

## 💡 Tips for Success

1. **Start small**: Test with the default $10k paper account first
2. **Be patient**: Let strategies run for at least a week
3. **Review daily**: Check the end-of-day reports
4. **Iterate**: Adjust parameters based on results
5. **Stay disciplined**: Trust your risk management

## 🚨 Important Reminders

- This is PAPER TRADING - no real money at risk
- Past performance doesn't guarantee future results
- Always test thoroughly before using real money
- Start with tiny positions when you go live

## Need Help?

Check the README.md for detailed documentation.
