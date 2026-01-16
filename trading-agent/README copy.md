# 🚀 Professional Backtrader Trading System

**200 SMA Trend Following Strategy on 4-Hour Candles**

A professional algorithmic trading system built with Backtrader, designed for paper trading on Alpaca before deploying real money.

---

## 📊 What This System Does

**Strategy**: 200 SMA Trend Following
- **BUY** when price crosses ABOVE 200 SMA (uptrend confirmed)
- **SELL** when price crosses BELOW 200 SMA (trend reversal)
- **Stop Loss**: 2% below entry
- **Take Profit**: 6% above entry (3:1 reward/risk)
- **Timeframe**: 4-hour candles (perfect for swing trading)

**Why This Strategy Works**:
- Used by institutional traders
- Clear, objective signals
- Works in trending markets
- Lower false signals than short-term strategies

---

## 🔧 Installation

### Step 1: Install Dependencies

```bash
# Make script executable
chmod +x install_backtrader.sh

# Run installation
./install_backtrader.sh
```

This installs:
- Backtrader (professional backtesting framework)
- Alpaca SDK (for data and paper trading)
- Required dependencies (pandas, numpy, matplotlib)

### Step 2: Set Up API Keys

Create a `.env` file in the `backtrader_system` directory:

```bash
# .env file
ALPACA_API_KEY=your_paper_trading_key_here
ALPACA_SECRET_KEY=your_paper_trading_secret_here
```

**Get your keys**: https://alpaca.markets/ → Paper Trading → API Keys

---

## 🧪 Testing

### Quick Test (Recommended First Step)

```bash
# Test the data connection
python data/alpaca_feed.py

# Run a quick backtest on SPY (6 months)
python backtest_runner.py
```

**Expected output**:
- Strategy performance metrics
- Win rate, Sharpe ratio, max drawdown
- Total P&L and return %

### Full Backtest (1 Year)

```bash
# Test on SPY with 1 year of data
python backtest_runner.py --symbol SPY --days 365

# Test on other symbols
python backtest_runner.py --symbol AAPL --days 365
python backtest_runner.py --symbol TSLA --days 180

# Compare strategies
python backtest_runner.py --compare
```

### With Chart

```bash
# Show visual chart (requires GUI)
python backtest_runner.py --symbol SPY --plot
```

---

## 📈 Understanding Results

### Good Results:
- ✅ **Sharpe Ratio > 1.0** (good risk-adjusted returns)
- ✅ **Max Drawdown < 20%** (manageable losses)
- ✅ **Win Rate > 40%** (with profit factor > 1.5)
- ✅ **Positive annualized return**

### Red Flags:
- ❌ Sharpe Ratio < 0.5
- ❌ Max Drawdown > 30%
- ❌ Win Rate < 35%
- ❌ Negative returns

---

## 🎯 Strategy Comparison

The system includes TWO strategies:

### 1. **200 SMA Trend Following** (Main Strategy)
- Simplest and most reliable
- Buy when price > 200 SMA
- Best for long-term trends

### 2. **50/200 SMA Crossover** (Alternative)
- More aggressive
- Buy on "golden cross" (50 SMA crosses above 200 SMA)
- More trades but potentially more whipsaws

**Compare them**:
```bash
python backtest_runner.py --compare
```

---

## 💰 Paper Trading (Next Step)

Once backtests look good, you can paper trade:

```bash
# Coming in next update - live_trader.py
# This will connect to Alpaca paper trading and execute real orders (with fake money)
```

---

## 🎛️ Customization

### Change Strategy Parameters

Edit `strategies/sma_200_strategy.py`:

```python
params = dict(
    sma_period=200,           # Try 150 or 250
    risk_per_trade=0.02,      # 2% risk per trade
    stop_loss_pct=0.02,       # 2% stop loss
    take_profit_pct=0.06,     # 6% take profit
    position_size=0.95,       # Use 95% of capital
)
```

### Test Different Timeframes

```python
# In backtest_runner.py, change timeframe:
run_backtest(
    strategy_class=SMA200Strategy,
    symbol='SPY',
    timeframe='1H',  # Try: '1H', '4H', '1D'
)
```

### Add More Symbols

```python
# Test multiple symbols
symbols = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'TSLA']

for symbol in symbols:
    run_backtest(
        strategy_class=SMA200Strategy,
        symbol=symbol,
        timeframe='4H'
    )
```

---

## 📊 Backtrader Advantages Over Custom System

### What Backtrader Gives You:

1. **✅ No Lookahead Bias**
   - Events processed in correct order
   - Can't "peek" into future data
   - Realistic trade timing

2. **✅ Realistic Costs**
   - Commission per trade
   - Slippage modeling
   - Bid/ask spreads

3. **✅ Professional Analytics**
   - Sharpe Ratio
   - Max Drawdown
   - Sortino Ratio
   - Trade analysis

4. **✅ Battle-Tested**
   - Used by professionals
   - Well-documented
   - Active community

---

## 🎯 Roadmap

### Phase 1: Backtest (Current) ✅
- [x] Install Backtrader
- [x] Implement 200 SMA strategy
- [x] Connect to Alpaca data
- [x] Run backtests

### Phase 2: Optimize (Next)
- [ ] Parameter optimization
- [ ] Walk-forward analysis
- [ ] Multiple timeframe testing
- [ ] Portfolio testing (multiple symbols)

### Phase 3: Paper Trade
- [ ] Live data feed
- [ ] Real-time signal generation
- [ ] Paper trade execution
- [ ] Performance monitoring

### Phase 4: Real Money (When Ready)
- [ ] Switch to live API keys
- [ ] Start with small capital
- [ ] Monitor and adjust
- [ ] Scale up gradually

---

## 🐛 Troubleshooting

### "No module named backtrader"
```bash
pip install backtrader --break-system-packages
```

### "Alpaca API keys not found"
- Check your `.env` file exists
- Make sure keys are PAPER TRADING keys
- Verify no extra spaces in keys

### "No data returned"
- Check symbol is valid (try 'SPY')
- Verify date range (use recent dates)
- Check Alpaca account is active

### Import errors
```bash
# Make sure you're in the right directory
cd backtrader_system

# Run from there
python backtest_runner.py
```

---

## 💡 Pro Tips

1. **Start with SPY** - Most liquid, reliable data
2. **Test multiple timeframes** - 4H is good, but try 1D too
3. **Compare to buy-and-hold** - Your strategy should beat it
4. **Watch the Sharpe ratio** - Best indicator of risk-adjusted returns
5. **Don't overtrade** - Fewer, better signals > many mediocre ones

---

## 📚 Resources

- **Backtrader Docs**: https://www.backtrader.com/docu/
- **Alpaca Docs**: https://alpaca.markets/docs/
- **200 SMA Strategy**: Classic institutional trend-following

---

## 🚀 Quick Start Commands

```bash
# 1. Install
./install_backtrader.sh

# 2. Test data
python data/alpaca_feed.py

# 3. Run backtest
python backtest_runner.py

# 4. Compare strategies
python backtest_runner.py --compare

# 5. Test different symbols
python backtest_runner.py --symbol AAPL
python backtest_runner.py --symbol TSLA
```

---

## ✅ Success Criteria

Before paper trading, make sure:
- ✅ Backtests are profitable (>10% annual return)
- ✅ Sharpe ratio > 1.0
- ✅ Max drawdown < 20%
- ✅ Strategy beats buy-and-hold
- ✅ Works on multiple symbols
- ✅ Consistent across timeframes

Once all boxes are checked → Start paper trading!

---

**Built for serious traders who want to validate before risking real money.** 💰

