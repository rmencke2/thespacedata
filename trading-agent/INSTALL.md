# Installation Instructions

## Quick Install (Recommended)

### Option 1: Development Install (Best)
```bash
cd trading-agent
pip install -e .
```

This installs the package in "editable" mode so Python can find all modules.

### Option 2: Bash Script
```bash
cd trading-agent
chmod +x install.sh
./install.sh
```

### Option 3: Manual Install
```bash
cd trading-agent
pip install -r requirements.txt
python setup.py develop
```

## Verify Installation

```bash
python test_system.py
```

If you see "✅ All tests passed!" - you're ready to go!

## Troubleshooting

### "No module named 'utils'" Error

This means Python can't find the local packages. Solutions:

1. **Use development install** (recommended):
   ```bash
   pip install -e .
   ```

2. **Run from the correct directory**:
   ```bash
   cd trading-agent  # Make sure you're IN the trading-agent directory
   python test_system.py
   ```

3. **Set PYTHONPATH** (temporary):
   ```bash
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   python test_system.py
   ```

### Missing Dependencies

```bash
pip install -r requirements.txt
```

### Permission Denied on install.sh

```bash
chmod +x install.sh
./install.sh
```

## What Gets Installed

- **LangGraph & LangChain**: Multi-agent orchestration
- **Alpaca API**: Paper trading interface (FREE)
- **yfinance**: Historical market data (FREE)
- **pandas/numpy**: Data processing
- **ta**: Technical analysis indicators
- **SQLite**: Trade logging (built-in to Python)

## Next Steps

After successful installation:

1. **Setup Alpaca** (optional for backtesting):
   ```bash
   cp .env.example .env
   # Edit .env and add your Alpaca paper trading keys
   ```

2. **Run backtest**:
   ```bash
   python run_backtest.py
   ```

3. **Test live trading**:
   ```bash
   python run_live.py --mode once
   ```

## System Requirements

- Python 3.8 or higher
- Internet connection (for data fetching)
- 100MB disk space
- Works on: macOS, Linux, Windows
