#!/bin/bash
#
# Backtrader Professional Trading System - Installation Script
# Sets up everything needed for professional algorithmic trading
#

echo "=============================================="
echo "🚀 Installing Backtrader Trading System"
echo "=============================================="
echo ""

# Check Python version
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"
echo ""

# Install Backtrader
echo "📦 Installing Backtrader..."
pip install backtrader --break-system-packages

# Install Alpaca integration
echo "📦 Installing Alpaca SDK..."
pip install alpaca-trade-api --break-system-packages

# Install additional dependencies
echo "📦 Installing additional dependencies..."
pip install pandas numpy matplotlib --break-system-packages
pip install python-dotenv --break-system-packages

# Create directory structure
echo ""
echo "📁 Creating directory structure..."
mkdir -p backtrader_system
mkdir -p backtrader_system/strategies
mkdir -p backtrader_system/data
mkdir -p backtrader_system/results
mkdir -p backtrader_system/logs

echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "  1. Create your .env file with Alpaca API keys"
echo "  2. Run the strategy backtester"
echo "  3. Test paper trading"
echo "  4. Go live when ready!"
echo ""
echo "=============================================="
