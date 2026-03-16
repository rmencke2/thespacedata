# 🔥 vs 🛡️  Dual-Strategy Trading System

## A/B Test: Aggressive vs Conservative

Run TWO trading strategies simultaneously with $30K each to see which performs better!

---

## 🎯 Strategy Comparison

| Aspect | 🔥 **AGGRESSIVE** | 🛡️  **CONSERVATIVE** |
|--------|------------------|---------------------|
| **Capital** | $30,000 | $30,000 |
| **Risk per Trade** | 3% | 1.5% |
| **Max Positions** | 6 | 4 |
| **Stop Loss** | 4% | 2% |
| **Daily Loss Limit** | 8% | 4% |
| **Stocks** | High volatility (RIVN, LCID, COIN, MARA) | Stable large caps (MSFT, AAPL, NVDA) |
| **Mean Reversion** | 1.2 std dev (very sensitive) | 1.8 std dev (selective) |
| **Momentum** | Fast (8/21 MA) | Standard (10/30 MA) |
| **RSI Thresholds** | 45/55 (sensitive) | 35/65 (conservative) |
| **Expected Trades** | Many small wins + bigger losses | Fewer high-quality trades |
| **Goal** | High returns, accepts volatility | Steady growth, capital preservation |

---

## 🚀 Quick Start

### Test Both Strategies (1 cycle each)
```bash
# Test aggressive
python run_aggressive.py --mode once

# Test conservative  
python run_conservative.py --mode once

# Compare results
python compare_strategies.py
```

### Run Both for 1 Week
```bash
# Make scripts executable
chmod +x start_both.sh stop_both.sh

# Start both
./start_both.sh

# Monitor
tail -f logs_aggressive.log
tail -f logs_conservative.log

# Compare performance anytime
python compare_strategies.py

# Stop both
./stop_both.sh
```

---

## 📊 Monitoring

### Real-Time Monitoring
```bash
# Watch aggressive
tail -f logs_aggressive.log | grep -E "Trade|Signal|P&L"

# Watch conservative
tail -f logs_conservative.log | grep -E "Trade|Signal|P&L"

# Side-by-side comparison
watch -n 300 'python compare_strategies.py'  # Updates every 5 min
```

### Check Status
```bash
# Are they running?
ps aux | grep "run_aggressive\|run_conservative"

# Quick stats
python compare_strategies.py
```

---

## 📈 What to Expect

### Week 1 Predictions:

**🔥 Aggressive:**
- **More trades**: 10-30 trades
- **Higher volatility**: Bigger wins AND losses
- **Potential**: +5% to -5% (wide range)
- **Activity**: Lots of small trades

**🛡️  Conservative:**
- **Fewer trades**: 3-10 trades
- **Lower volatility**: Smaller wins and losses
- **Potential**: +1% to -2% (tighter range)
- **Activity**: Only high-quality setups

---

## 🎓 Learning Objectives

After 1 week, you'll know:
1. **Which approach fits your style** - Do you prefer action or patience?
2. **Risk/reward tradeoff** - Is higher risk worth higher potential returns?
3. **Win rate vs profit** - Which matters more: many small wins or few big wins?
4. **Market conditions** - Which strategy works better in current market?

---

## 📁 File Structure

```
trading-agent/
├── config_aggressive.py        # Aggressive config
├── config_conservative.py      # Conservative config
├── run_aggressive.py           # Aggressive runner
├── run_conservative.py         # Conservative runner
├── compare_strategies.py       # Comparison dashboard
├── start_both.sh               # Start both strategies
├── stop_both.sh                # Stop both strategies
├── logs_aggressive.log         # Aggressive logs
├── logs_conservative.log       # Conservative logs
├── trades_aggressive.db        # Aggressive trades database
└── trades_conservative.db      # Conservative trades database
```

---

## 🔧 Customization

Want to adjust? Edit the config files:

### Make Aggressive MORE Aggressive:
```python
# In config_aggressive.py
MEAN_REVERSION_STD = 1.0  # Even more sensitive
MAX_POSITIONS = 8          # More positions
STOCK_UNIVERSE = ['MARA', 'RIOT', 'COIN', ...]  # Ultra volatile
```

### Make Conservative LESS Aggressive:
```python
# In config_conservative.py
MEAN_REVERSION_STD = 2.0  # More selective
MAX_POSITIONS = 3          # Fewer positions
STOCK_UNIVERSE = ['MSFT', 'AAPL', 'GOOGL']  # Mega caps only
```

---

## 🏆 Competition Rules

At the end of 1 week, **declare a winner based on:**

1. **Total Return %** (primary metric)
2. **Risk-Adjusted Return** (Sharpe ratio)
3. **Max Drawdown** (worst loss)
4. **Win Rate**
5. **Consistency** (standard deviation of returns)

---

## 📊 Example Comparison Output

```
================================================================================
📊 STRATEGY COMPARISON DASHBOARD
================================================================================
Generated: 2026-01-14 16:00:00
Starting Capital: $30,000 each
================================================================================

METRIC                         🔥 AGGRESSIVE               🛡️  CONSERVATIVE        
--------------------------------------------------------------------------------
Total Trades                   24                          8                          
Win Rate                       58.3%                       75.0%                      
Total P&L                      $1,245.50                   $612.30                    
Return %                       4.15%                       2.04%                      
Average Win                    $89.20                      $145.60                    
Average Loss                   -$52.30                     -$68.40                    
Best Trade                     $245.80                     $289.50                    
Worst Trade                    -$156.20                    -$98.70                    
Open Positions                 3                           1                          
Total Exposure                 $18,450.00                  $4,200.00                  
--------------------------------------------------------------------------------

🏆 PERFORMANCE SUMMARY:
   🔥 Aggressive is WINNING by $633.20 (4.15% vs 2.04%)

📈 TRADING ACTIVITY:
   Aggressive: 24 trades (14 wins, 10 losses)
   Conservative: 8 trades (6 wins, 2 losses)

⚖️  RISK METRICS:
   Aggressive Profit Factor: 1.71
   Conservative Profit Factor: 2.13
```

---

## 💡 Tips for Success

1. **Let them run for at least 1 week** - Don't judge after 1 day
2. **Markets matter** - Sideways = fewer trades, volatile = more trades
3. **Compare risk-adjusted returns** - $1000 return with $10K risk vs $500 return with $2K risk
4. **Learn from both** - Even if one loses, you learn what NOT to do
5. **Paper money = perfect testing** - Try extreme setups you'd never risk real money on

---

## 🚨 Troubleshooting

**"No trades happening"**
→ Markets are sideways, both strategies being patient (GOOD!)
→ Or lower thresholds in config files

**"One strategy crashing"**
→ Check logs: `tail -100 logs_aggressive.log`
→ Database issue: Delete and restart: `rm trades_aggressive.db`

**"Can't compare strategies"**
→ Make sure both have run at least once
→ Check databases exist: `ls -la *.db`

---

## 🎯 Next Steps After 1 Week

1. **Analyze results** with `compare_strategies.py`
2. **Pick winner** or blend both approaches
3. **Refine parameters** based on what worked
4. **Scale up** (if profitable) or adjust (if not)
5. **Consider live trading** with small amounts

---

**Remember:** This is an experiment! The goal is LEARNING, not just profit. Even losses teach valuable lessons about risk, strategy, and market behavior.

Good luck! 🚀
