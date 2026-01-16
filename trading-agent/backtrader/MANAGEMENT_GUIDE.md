# 🚀 Alpaca Trader Management Guide

**Managing your paper trader like a pro!**

---

## 📋 Three New Tools

You now have **3 powerful tools** to manage your trader:

1. **analyze_performance.py** - Review trading results
2. **optimize_fees.py** - Optimize position sizing
3. **trader_daemon.sh** - Run trader as background service

---

## 🎯 TOOL 1: Performance Analyzer

### What It Does:
- Loads all your trade logs
- Calculates win rate, P&L
- Compares to backtest targets
- Analyzes fee impact
- Recommends optimizations

### Run It:

```bash
cd ~/trading-agent/backtrader
python analyze_performance.py
```

### Example Output:

```
📊 TRADE ANALYSIS
========================================
Total Actions: 4
  Buy Orders: 2
  Sell Orders: 2

💰 COMPLETED TRADES
========================================

✅ WIN - ETH/USD
  P&L: $4,250.00 (+18.5%)
  
❌ LOSS - BTC/USD
  P&L: $-1,850.00 (-4.2%)

📈 PERFORMANCE SUMMARY
========================================
Win Rate: 50.0%
Total P&L: $2,400.00
Average per Trade: $1,200.00

📊 BACKTEST COMPARISON
                    Backtest    Your Paper    Status
Win Rate:           83.3%       50.0%         ⚠️
```

### When to Use:
- **Daily:** Quick check on progress
- **Weekly:** Full performance review
- **Monthly:** Compare to backtest targets

---

## 💸 TOOL 2: Fee Optimizer

### What It Does:
- Calculates fee impact on profits
- Finds optimal position size
- Compares different scenarios
- Recommends adjustments

### Run It:

```bash
cd ~/trading-agent/backtrader
python optimize_fees.py
```

### Example Output:

```
💸 FEE IMPACT ANALYSIS
========================================

📊 FEE IMPACT BY POSITION SIZE
Position    Value       Round-Trip   Break-Even
45%        $45,000      $90.00       0.20%
55%        $55,000      $110.00      0.20%
65%        $65,000      $130.00      0.20%

🎯 OPTIMAL POSITION SIZE CALCULATION
========================================
Kelly Criterion: 69.1% of capital
Half Kelly (safer): 34.6% of capital

💡 RECOMMENDATIONS
Current: 45% ($45,000)
Fees: $90.00 (0.20%)
Fee Impact: 1.0% of average win

✅ OPTIMAL - Fees are minimal
Recommended: 55% ($55,000 per trade)
```

### When to Use:
- **Before going live:** Optimize setup
- **After 5-10 trades:** Verify fee efficiency
- **When changing capital:** Recalculate sizes

---

## 🔄 TOOL 3: Trader Daemon

### What It Does:
- Runs trader in background
- Auto-restarts if crashed
- Auto-starts on laptop reboot
- Logs everything to file
- Easy start/stop/status

### Basic Commands:

```bash
cd ~/trading-agent/backtrader

# Make script executable (first time only)
chmod +x trader_daemon.sh

# Start trader
./trader_daemon.sh start

# Check status
./trader_daemon.sh status

# View logs
./trader_daemon.sh logs

# Stop trader
./trader_daemon.sh stop

# Restart trader
./trader_daemon.sh restart
```

### Example Output:

```bash
$ ./trader_daemon.sh start
🚀 Starting Alpaca Crypto Trader...
✅ Trader started!
PID: 12345
Logs: ./logs/trader_20260109.log

$ ./trader_daemon.sh status
========================================
📊 Alpaca Crypto Trader Status
========================================
Status: RUNNING ✅
PID: 12345
Uptime: 02:34:15
```

### Install as System Service:

**For auto-start on boot:**

```bash
# macOS
./trader_daemon.sh install-service

# Linux
./trader_daemon.sh install-service
```

**This makes it:**
- Start when laptop boots
- Restart if crashes
- Run even after sleep/wake
- Survive laptop battery drain

---

## 📊 Complete Workflow

### Day 1: Setup

```bash
# 1. Run fee optimizer
python optimize_fees.py

# 2. Note recommended position size
# Output: "Recommended: 55%"

# 3. Update trader (if needed)
# Edit alpaca_crypto_paper_trader.py
# Change: self.position_size_pct = 0.55

# 4. Start daemon
./trader_daemon.sh start

# 5. Check it's running
./trader_daemon.sh status
```

### Daily: Quick Check

```bash
# Check if trader is still running
./trader_daemon.sh status

# View recent activity
./trader_daemon.sh logs
# Press Ctrl+C to exit
```

### Weekly: Performance Review

```bash
# Run full analysis
python analyze_performance.py

# Check:
# - How many trades?
# - Win rate?
# - P&L?
# - On track with backtest?
```

### Monthly: Deep Dive

```bash
# 1. Performance analysis
python analyze_performance.py

# 2. Fee optimization check
python optimize_fees.py

# 3. Adjust if needed
# - Position size
# - Stop loss
# - Take profit

# 4. Restart with new settings
./trader_daemon.sh restart
```

---

## 🔧 Solving Your 3 Problems

### Problem 1: "Make it a background process"

**Solution: Trader Daemon** ✅

```bash
# Start in background
./trader_daemon.sh start

# Close terminal - trader keeps running!
```

**Features:**
- Runs in background
- Logs to file
- Doesn't stop when you close terminal
- Auto-restarts if crashes

### Problem 2: "Auto-start/stop with laptop"

**Solution: Install as Service** ✅

```bash
# Install (one-time setup)
./trader_daemon.sh install-service

# Now it will:
# - Start when laptop boots
# - Restart if crashes  
# - Survive sleep/wake
# - Survive battery drain
```

**How it handles battery:**
- macOS: LaunchAgent persists through sleep
- Linux: systemd service restarts on wake
- If battery dies → auto-starts on reboot

### Problem 3: "Optimize for fees"

**Solution: Fee Optimizer + Bigger Positions** ✅

```bash
# Run optimizer
python optimize_fees.py

# It will tell you:
# - Current fee impact
# - Optimal position size
# - Expected improvement

# Example:
# Current: 45% positions = $90 fees
# Optimal: 55% positions = $110 fees
# But fee % goes from 0.20% to 0.20%
# Impact: Same %, but bigger absolute wins!
```

**The Math:**
- Small position: $45k trade, +20% = $9k win, $90 fees = 1.0% fee impact
- Large position: $55k trade, +20% = $11k win, $110 fees = 1.0% fee impact
- **Same fee %, but $2k more profit!**

---

## 📁 File Organization

```
trading-agent/backtrader/
├── alpaca_crypto_paper_trader.py    ← Main trader
├── trader_daemon.sh                  ← Daemon manager
├── analyze_performance.py            ← Performance analyzer
├── optimize_fees.py                  ← Fee optimizer
├── logs/                             ← Log files
│   ├── trader_20260109.log
│   ├── trader_20260110.log
│   └── ...
└── alpaca_trades_20260109.json      ← Trade logs
```

---

## 🎯 Quick Reference

### Daily Commands:

```bash
# Morning check
./trader_daemon.sh status

# View live activity
./trader_daemon.sh logs
```

### Weekly Commands:

```bash
# Performance review
python analyze_performance.py

# If making changes:
./trader_daemon.sh restart
```

### Monthly Commands:

```bash
# Full analysis
python analyze_performance.py
python optimize_fees.py

# Adjust and restart
nano alpaca_crypto_paper_trader.py  # Edit settings
./trader_daemon.sh restart
```

---

## ⚠️ Important Notes

### Logs Location:

All logs stored in `logs/` directory:
- `trader_YYYYMMDD.log` - Daily trader logs
- `system.log` - System service logs (if installed)

### Disk Space:

Logs can grow! Clean old logs:

```bash
# Delete logs older than 30 days
find logs/ -name "*.log" -mtime +30 -delete
```

### API Keys:

Daemon needs API keys set:

```bash
# Add to ~/.bashrc or ~/.zshrc:
export ALPACA_API_KEY='your_key'
export ALPACA_SECRET_KEY='your_secret'

# Reload:
source ~/.zshrc
```

---

## 🚨 Troubleshooting

### "Daemon won't start"

```bash
# Check API keys
echo $ALPACA_API_KEY

# If empty, set them:
export ALPACA_API_KEY='your_key'
export ALPACA_SECRET_KEY='your_secret'
```

### "No trade logs found"

```bash
# Logs are in current directory
ls -la alpaca_trades_*.json

# If empty, trader hasn't made trades yet
# This is normal - strategy is selective!
```

### "Service won't auto-start"

```bash
# macOS: Check if loaded
launchctl list | grep alpaca

# Linux: Check service status
sudo systemctl status alpaca-crypto-trader
```

---

## 🎉 You're All Set!

**You now have:**
1. ✅ Background trading daemon
2. ✅ Auto-restart on crash/reboot
3. ✅ Performance analyzer
4. ✅ Fee optimizer
5. ✅ Complete logging

**Start with:**

```bash
./trader_daemon.sh start
```

**Then monitor daily with:**

```bash
./trader_daemon.sh status
```

**Good luck with your paper trading!** 🚀💰
