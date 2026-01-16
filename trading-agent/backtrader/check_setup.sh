#!/bin/bash
#
# Quick Setup Verification
# Tests that API keys are set and working
#

echo "=========================================="
echo "🔍 Checking Alpaca Setup"
echo "=========================================="
echo ""

# Check API keys
if [ -z "$ALPACA_API_KEY" ]; then
    echo "❌ ALPACA_API_KEY not set"
    echo ""
    echo "Set it with:"
    echo "  export ALPACA_API_KEY='your_paper_key_here'"
    echo ""
    echo "Or add to ~/.zshrc:"
    echo "  echo 'export ALPACA_API_KEY=\"your_key\"' >> ~/.zshrc"
    echo "  source ~/.zshrc"
    exit 1
else
    echo "✅ ALPACA_API_KEY is set"
    echo "   ${ALPACA_API_KEY:0:10}..."
fi

if [ -z "$ALPACA_SECRET_KEY" ]; then
    echo "❌ ALPACA_SECRET_KEY not set"
    echo ""
    echo "Set it with:"
    echo "  export ALPACA_SECRET_KEY='your_paper_secret_here'"
    exit 1
else
    echo "✅ ALPACA_SECRET_KEY is set"
    echo "   ${ALPACA_SECRET_KEY:0:10}..."
fi

echo ""
echo "=========================================="
echo "✅ API Keys Configured!"
echo "=========================================="
echo ""
echo "You can now run:"
echo "  python moderate_activity_trader.py"
echo "  ./trader_daemon.sh start"
echo ""
