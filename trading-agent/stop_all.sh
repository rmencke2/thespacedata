#!/bin/bash

# Stop All 3 Trading Strategies

echo "======================================"
echo "🛑 Stopping ALL Trading Strategies"
echo "======================================"
echo ""

# Stop aggressive
if pgrep -f "run_aggressive.py" > /dev/null; then
    echo "Stopping AGGRESSIVE strategy..."
    pkill -f "run_aggressive.py"
    echo "✅ Stopped"
    sleep 1
else
    echo "Aggressive not running"
fi

# Stop conservative
if pgrep -f "run_conservative.py" > /dev/null; then
    echo "Stopping CONSERVATIVE strategy..."
    pkill -f "run_conservative.py"
    echo "✅ Stopped"
    sleep 1
else
    echo "Conservative not running"
fi

# Stop crypto
if pgrep -f "run_crypto.py" > /dev/null; then
    echo "Stopping CRYPTO strategy..."
    pkill -f "run_crypto.py"
    echo "✅ Stopped"
    sleep 1
else
    echo "Crypto not running"
fi

echo ""
echo "✅ All strategies stopped!"
echo ""
echo "📊 View final results:"
echo "   python compare_strategies.py"
echo ""
echo "💾 Databases saved:"
echo "   - trades_aggressive.db"
echo "   - trades_conservative.db"
echo "   - trades_crypto.db"
echo ""
