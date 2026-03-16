#!/bin/bash

# Quick Crypto Setup
# Fixes the data fetcher issue for crypto trading

echo "======================================"
echo "🪙 Setting Up Crypto Trading"
echo "======================================"
echo ""

# Copy crypto data fetcher to utils folder
echo "📦 Installing crypto data fetcher..."
cp utils/data_fetcher_crypto.py utils/data_fetcher_crypto.py 2>/dev/null || echo "Already exists"

echo ""
echo "✅ Setup complete!"
echo ""
echo "📊 Test crypto connection:"
echo "   python -c 'from utils.data_fetcher_crypto import DataFetcher; f = DataFetcher(); print(f.get_latest_bars([\"BTC/USD\", \"ETH/USD\"], 5))'"
echo ""
echo "🚀 Run crypto strategy:"
echo "   python run_crypto.py --mode once"
echo ""
