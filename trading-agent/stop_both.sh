#!/bin/bash

# Stop Both Trading Strategies

echo "======================================"
echo "🛑 Stopping Both Trading Strategies"
echo "======================================"
echo ""

# Stop aggressive
if pgrep -f "run_aggressive.py" > /dev/null; then
    echo "Stopping AGGRESSIVE strategy..."
    pkill -f "run_aggressive.py"
    echo "✅ Stopped"
else
    echo "Aggressive not running"
fi

# Stop conservative
if pgrep -f "run_conservative.py" > /dev/null; then
    echo "Stopping CONSERVATIVE strategy..."
    pkill -f "run_conservative.py"
    echo "✅ Stopped"
else
    echo "Conservative not running"
fi

echo ""
echo "✅ All strategies stopped!"
echo ""
echo "📊 View final results:"
echo "   python compare_strategies.py"
echo ""
