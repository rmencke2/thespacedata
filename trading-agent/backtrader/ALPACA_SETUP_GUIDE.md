# 🦙 Alpaca Crypto Paper Trading Setup

**Get your Momentum strategy running on Alpaca in 10 minutes!**

---

## 📋 Prerequisites

✅ Alpaca account (you already have this!)
✅ Python 3.8+
✅ Your existing backtrader setup

---

## 🚀 Quick Setup (5 Steps)

### Step 1: Install Alpaca SDK

```bash
pip install alpaca-py
```

### Step 2: Get Your Paper Trading API Keys

1. Go to: https://app.alpaca.markets/paper/dashboard/overview
2. Click **"View"** next to "Your API Keys"
3. Copy **API Key** and **Secret Key**
4. Keep these safe!

**Note:** These are your PAPER keys (different from live!)

### Step 3: Set Environment Variables

**On Mac/Linux:**
```bash
export ALPACA_API_KEY='your_paper_key_here'
export ALPACA_SECRET_KEY='your_paper_secret_here'
```

**On Windows:**
```powershell
set ALPACA_API_KEY=your_paper_key_here
set ALPACA_SECRET_KEY=your_paper_secret_here
```

**Or add to your ~/.bashrc or ~/.zshrc** (permanent):
```bash
echo 'export ALPACA_API_KEY="your_key"' >> ~/.zshrc
echo 'export ALPACA_SECRET_KEY="your_secret"' >> ~/.zshrc
source ~/.zshrc
```

### Step 4: Verify Crypto is Enabled

```python
from alpaca.trading.client import TradingClient
import os

client = TradingClient(
    api_key=os.getenv('ALPACA_API_KEY'),
    secret_key=os.getenv('ALPACA_SECRET_KEY'),
    paper=True
)

account = client.get_account()
print(f"Crypto Status: {account.crypto_status}")
# Should show: "ACTIVE"
```

If not active:
1. Go to https://app.alpaca.markets/paper/dashboard/overview
2. Enable crypto trading in settings

### Step 5: Run Your First Test

```bash
cd ~/trading-agent/backtrader
python alpaca_crypto_paper_trader.py
```

Choose option **1** (run one check) to test!

---

## 📊 How It Works

### The Script Does:

1. **Checks every hour** (or on-demand)
2. **Analyzes BTC/ETH** for buy signals
3. **Executes trades** automatically
4. **Tracks positions** and P&L
5. **Logs everything** to JSON file

### Buy Signal Requirements (ALL must be true):

- ✅ Price breaks above 20-day high
- ✅ Volume > 2x average
- ✅ RSI between 60-80
- ✅ 3-day momentum positive

### Sell Signal (ANY triggers):

- 💎 +20% profit (take profit)
- 🛑 -8% loss (stop loss)
- 📈 RSI > 85 (exhaustion)
- 📉 Volume < 0.5x (momentum dying)

---

## 🎯 Usage Examples

### Test Mode (Recommended First)

```bash
python alpaca_crypto_paper_trader.py
# Choose option 1: Run ONE strategy check
```

**This will:**
- Check your account balance
- Analyze BTC and ETH
- Show if there's a signal
- Execute trade if conditions met
- Exit after one check

**Perfect for:** Testing, debugging, learning

### Live Mode (Runs Continuously)

```bash
python alpaca_crypto_paper_trader.py
# Choose option 2: Run LIVE
```

**This will:**
- Check every 60 minutes
- Monitor positions
- Execute trades automatically
- Run until you press Ctrl+C

**Perfect for:** Paper trading for weeks/months

### Manual Control

```python
from alpaca_crypto_paper_trader import AlpacaCryptoMomentumTrader

# Initialize
trader = AlpacaCryptoMomentumTrader(paper=True)

# Check account
trader.get_account_info()

# Run one check
trader.run_strategy_check()

# Check specific symbol
should_buy, reason = trader.check_buy_signal('BTC/USD')
print(f"BTC Signal: {reason}")
```

---

## 📈 What You'll See

### First Run Output:

```
======================================================================
🚀 ALPACA CRYPTO PAPER TRADER
======================================================================

Momentum Breakout Strategy
Based on your +95% backtest on ETH!

======================================================================

🚀 Alpaca Crypto Paper Trader Initialized
   Mode: PAPER
   Symbols: BTC/USD, ETH/USD
   Strategy: Momentum Breakout

💰 Account Status:
   Cash: $100,000.00
   Portfolio: $100,000.00
   Buying Power: $100,000.00
   Crypto Status: ACTIVE

======================================================================
⏰ Strategy Check - 2026-01-09 10:30:00
======================================================================

======================================================================
Checking BTC/USD...
======================================================================

📊 BTC/USD Analysis:
   Price: $92,450.00
   20-day High: $91,200.00
   Volume: 2.3x avg
   RSI: 65.2
   Momentum: 1250.50

Signal Status: 🚀 BUY SIGNAL - All conditions met!

💰 Executing BUY for BTC/USD
   Buying Power: $100,000.00
   Position Size: $45,000.00
   ✅ Order submitted: abc-123-def
   ✅ FILLED: 0.486842 @ $92,450.00

======================================================================
Checking ETH/USD...
======================================================================

📊 ETH/USD Analysis:
   Price: $3,250.00
   20-day High: $3,180.00
   Volume: 1.8x avg
   RSI: 58.5
   Momentum: 85.20

Signal Status: Low volume (1.8x < 2.0x)
```

---

## 📁 Output Files

### Trade Log: `alpaca_trades_YYYYMMDD.json`

```json
{
  "positions": {
    "BTC/USD": {
      "entry_price": 92450.0,
      "quantity": 0.486842,
      "entry_time": "2026-01-09T10:30:15",
      "order_id": "abc-123-def"
    }
  },
  "trades": [
    {
      "timestamp": "2026-01-09T10:30:15",
      "symbol": "BTC/USD",
      "action": "BUY",
      "price": 92450.0,
      "quantity": 0.486842,
      "value": 45000.0
    }
  ]
}
```

---

## ⚙️ Configuration

### Change Check Interval:

```python
# In alpaca_crypto_paper_trader.py, line ~450:
trader.run_live(check_interval_minutes=30)  # Check every 30 min
```

### Change Position Size:

```python
# In __init__ method:
self.position_size_pct = 0.30  # 30% instead of 45%
```

### Add More Symbols:

```python
# In __init__ method:
self.symbols = ['BTC/USD', 'ETH/USD', 'LTC/USD']
```

### Adjust Risk Parameters:

```python
# In __init__ method:
self.stop_loss_pct = 0.10  # 10% stop
self.take_profit_pct = 0.25  # 25% target
```

---

## 🐛 Troubleshooting

### "Alpaca API credentials not found"

**Solution:**
```bash
# Set environment variables
export ALPACA_API_KEY='your_key'
export ALPACA_SECRET_KEY='your_secret'

# Verify
echo $ALPACA_API_KEY
```

### "Crypto Status: NOT_ACTIVE"

**Solution:**
1. Go to Alpaca dashboard
2. Settings → Trading Configuration
3. Enable crypto trading
4. Wait 5 minutes

### "Insufficient buying power"

**Solution:**
- Check: `trader.get_account_info()`
- You might have existing positions
- Or change position size to 30%

### "No data for BTC/USD"

**Solution:**
- Alpaca crypto data can be spotty
- Try again in 5 minutes
- Or check Alpaca status page

### Module not found errors

**Solution:**
```bash
pip install alpaca-py yfinance pandas
```

---

## 📊 Monitoring Your Trading

### Check Performance Daily:

```python
from alpaca_crypto_paper_trader import AlpacaCryptoMomentumTrader

trader = AlpacaCryptoMomentumTrader(paper=True)
trader.print_summary()
```

### View Trade Log:

```bash
cat alpaca_trades_*.json | jq
```

### Compare to Backtest:

**Backtest (ETH):** +95.13% over 3 years
**Your Target:** ~+30% per year

After 1 month, check if you're on track:
- Month 1: Should be around +2-3%
- Month 3: Should be around +7-8%
- Month 12: Should be around +30%

---

## ⚠️ Important Notes

### This is PAPER TRADING:

- ✅ No real money at risk
- ✅ Perfect for learning
- ✅ Real market data
- ✅ Real execution (but fake money)

### Before Going Live:

1. Paper trade for 2-3 months
2. Verify returns match backtest (~30%/year)
3. Verify win rate similar (~60%)
4. Make sure you understand every trade
5. Start small ($500-1000)

### Limitations:

- Alpaca crypto data can lag slightly
- Paper fills might be better than real
- Slippage not perfectly modeled
- But MUCH better than no testing!

---

## 🎯 Expected Results

**Based on your backtest:**

| Metric | Backtest | Expected Paper |
|--------|----------|----------------|
| Annual Return | +95% (ETH) | +30-50% |
| Sharpe Ratio | 1.21 | 0.8-1.2 |
| Win Rate | 83% | 60-80% |
| Max Drawdown | 8.91% | 10-15% |
| Trades/Year | 2 | 6-12 |

**Why lower?** Paper trading includes more realistic conditions

---

## 🚀 Next Steps

1. **Run test mode** (1-2 times)
2. **Run live mode** (let it run for a week)
3. **Check results** (compare to backtest)
4. **Adjust if needed** (tune parameters)
5. **Scale up** (after 2-3 months success)

---

## 📝 Checklist

Before running:
- [ ] Alpaca account created
- [ ] Paper trading enabled
- [ ] Crypto trading activated
- [ ] API keys set in environment
- [ ] Script downloaded
- [ ] Dependencies installed

First run:
- [ ] Test mode works
- [ ] Account info shows
- [ ] No errors
- [ ] Trade log created

After 1 week:
- [ ] Check trade log
- [ ] Review performance
- [ ] Compare to backtest
- [ ] Adjust if needed

After 1 month:
- [ ] Should have 1-3 trades
- [ ] Check win rate
- [ ] Check returns
- [ ] Decide: continue or adjust

---

## 💡 Tips

1. **Start with test mode** - Run option 1 multiple times before option 2
2. **Check during market hours** - Crypto trades 24/7 but volume is higher during US hours
3. **Be patient** - Strategy only trades 2-6 times per year
4. **Don't overtrade** - If no signals, that's OK!
5. **Trust the backtest** - You got 83% win rate for a reason

---

## 🎉 You're Ready!

```bash
cd ~/trading-agent/backtrader
python alpaca_crypto_paper_trader.py
```

**Choose option 1** to test it right now! 🚀

Questions? Issues? Let me know!
