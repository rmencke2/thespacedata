#!/bin/bash

# Installation script for trading-agent

echo "======================================"
echo "Installing Trading Agent System"
echo "======================================"
echo ""

# Install in development mode
echo "📦 Installing package in development mode..."
pip install -e .

echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "  1. Copy .env.example to .env and add your Alpaca keys"
echo "  2. Run: python test_system.py"
echo "  3. Run: python run_backtest.py"
echo ""
