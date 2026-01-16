#!/bin/bash

# Start Both Trading Strategies
# Runs Aggressive and Conservative in parallel

echo "======================================"
echo "🚀 Starting Both Trading Strategies"
echo "======================================"
echo ""

# Check if already running
if pgrep -f "run_aggressive.py" > /dev/null; then
    echo "⚠️  Aggressive strategy already running"
else
    echo "🔥 Starting AGGRESSIVE strategy..."
    nohup python run_aggressive.py --mode continuous > logs_aggressive.log 2>&1 &
    echo "   PID: $!"
fi

if pgrep -f "run_conservative.py" > /dev/null; then
    echo "⚠️  Conservative strategy already running"
else
    echo "🛡️  Starting CONSERVATIVE strategy..."
    nohup python run_conservative.py --mode continuous > logs_conservative.log 2>&1 &
    echo "   PID: $!"
fi

sleep 3

echo ""
echo "✅ Both strategies started!"
echo ""
echo "📊 Monitor with:"
echo "   tail -f logs_aggressive.log"
echo "   tail -f logs_conservative.log"
echo "   python compare_strategies.py"
echo ""
echo "🛑 Stop with:"
echo "   ./stop_both.sh"
echo ""
