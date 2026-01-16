"""
Test Crypto Data Connection
Verify Alpaca crypto data works
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.data_fetcher_crypto import DataFetcher
from utils.config import Config

print("\n" + "="*60)
print("🪙 TESTING CRYPTO DATA CONNECTION")
print("="*60)
print("")

# Check API keys
if not Config.ALPACA_API_KEY or not Config.ALPACA_SECRET_KEY:
    print("❌ ERROR: Alpaca API keys not configured!")
    print("Please set up your .env file with:")
    print("  ALPACA_API_KEY=...")
    print("  ALPACA_SECRET_KEY=...")
    sys.exit(1)

print("✅ API keys configured")
print("")

# Create fetcher
fetcher = DataFetcher()
print("")

# Test fetching Bitcoin and Ethereum
print("📊 Testing crypto data fetch...")
print("Fetching BTC/USD and ETH/USD (last 5 days)...")
print("")

try:
    data = fetcher.get_latest_bars(['BTC/USD', 'ETH/USD'], days=5)
    
    if not data:
        print("❌ No data returned!")
        print("")
        print("This might mean:")
        print("  1. Your Alpaca account doesn't have crypto access")
        print("  2. API keys are for live trading (use paper trading keys)")
        print("  3. Network/API issue")
        print("")
        print("💡 Solution: Get PAPER TRADING keys from:")
        print("   https://alpaca.markets/ → Paper Trading → API Keys")
        sys.exit(1)
    
    print("="*60)
    print("✅ SUCCESS! Crypto data is working!")
    print("="*60)
    print("")
    
    for symbol, df in data.items():
        if not df.empty:
            latest = df.iloc[-1]
            print(f"{symbol}:")
            print(f"  Latest Price: ${latest['close']:,.2f}")
            print(f"  Volume: ${latest['volume']:,.0f}")
            print(f"  Data Points: {len(df)}")
            print("")
        else:
            print(f"{symbol}: No data")
            print("")
    
    print("="*60)
    print("🚀 Ready to trade crypto!")
    print("="*60)
    print("")
    print("Next steps:")
    print("  1. Run: python run_crypto.py --mode once")
    print("  2. Start: python run_crypto.py --mode continuous")
    print("")

except Exception as e:
    print(f"❌ ERROR: {e}")
    print("")
    print("Common issues:")
    print("  - Wrong API keys (use PAPER TRADING keys)")
    print("  - No crypto access on account")
    print("  - Network/firewall blocking Alpaca")
    print("")
    import traceback
    traceback.print_exc()
