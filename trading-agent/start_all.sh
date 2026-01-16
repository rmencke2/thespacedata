#!/bin/bash

# Start All 3 Trading Strategies
# Runs Aggressive, Conservative, and Crypto in parallel

echo "======================================"
echo "🚀 Starting ALL Trading Strategies"
echo "======================================"
echo "Total Capital: $80,000"
echo "  - Aggressive: $30K"
echo "  - Conservative: $30K"
echo "  - Crypto: $20K"
echo "======================================"
echo ""

# Check if already running
if pgrep -f "run_aggressive.py" > /dev/null; then
    echo "⚠️  Aggressive strategy already running"
else
    echo "🔥 Starting AGGRESSIVE strategy..."
    nohup python run_aggressive.py --mode continuous > logs_aggressive.log 2>&1 &
    echo "   PID: $!"
    sleep 1
fi

if pgrep -f "run_conservative.py" > /dev/null; then
    echo "⚠️  Conservative strategy already running"
else
    echo "🛡️  Starting CONSERVATIVE strategy..."
    nohup python run_conservative.py --mode continuous > logs_conservative.log 2>&1 &
    echo "   PID: $!"
    sleep 1
fi

if pgrep -f "run_crypto.py" > /dev/null; then
    echo "⚠️  Crypto strategy already running"
else
    echo "🪙 Starting CRYPTO strategy (24/7)..."
    nohup python run_crypto.py --mode continuous > logs_crypto.log 2>&1 &
    echo "   PID: $!"
    sleep 1
fi

sleep 2

echo ""
echo "✅ All 3 strategies started!"
echo ""
echo "📊 Monitor with:"
echo "   tail -f logs_aggressive.log"
echo "   tail -f logs_conservative.log"
echo "   tail -f logs_crypto.log"
echo ""
echo "📈 Compare performance:"
echo "   python compare_strategies.py"
echo ""
echo "🛑 Stop all:"
echo "   ./stop_all.sh"
echo ""
echo "💡 Crypto trades 24/7 - check it on weekends!"
echo ""
