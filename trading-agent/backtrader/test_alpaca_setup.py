"""
Quick Alpaca Crypto Setup Test
Verifies everything is working before running the trader
"""
import os
from alpaca.trading.client import TradingClient
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timedelta


def test_api_keys():
    """Test 1: Check API keys are set"""
    print("\n" + "="*70)
    print("TEST 1: API Keys")
    print("="*70)
    
    api_key = os.getenv('ALPACA_API_KEY')
    secret_key = os.getenv('ALPACA_SECRET_KEY')
    
    if not api_key:
        print("❌ ALPACA_API_KEY not found")
        print("\nSet it with:")
        print("  export ALPACA_API_KEY='your_key'")
        return False
    
    if not secret_key:
        print("❌ ALPACA_SECRET_KEY not found")
        print("\nSet it with:")
        print("  export ALPACA_SECRET_KEY='your_secret'")
        return False
    
    print(f"✅ ALPACA_API_KEY: {api_key[:10]}...")
    print(f"✅ ALPACA_SECRET_KEY: {secret_key[:10]}...")
    return True


def test_connection():
    """Test 2: Check connection to Alpaca"""
    print("\n" + "="*70)
    print("TEST 2: Connection")
    print("="*70)
    
    try:
        client = TradingClient(
            api_key=os.getenv('ALPACA_API_KEY'),
            secret_key=os.getenv('ALPACA_SECRET_KEY'),
            paper=True
        )
        
        account = client.get_account()
        print(f"✅ Connected to Alpaca!")
        print(f"   Account #: {account.account_number}")
        return True, client
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False, None


def test_account_status(client):
    """Test 3: Check account status"""
    print("\n" + "="*70)
    print("TEST 3: Account Status")
    print("="*70)
    
    try:
        account = client.get_account()
        
        print(f"Account Status: {account.status}")
        print(f"Cash: ${float(account.cash):,.2f}")
        print(f"Portfolio Value: ${float(account.portfolio_value):,.2f}")
        print(f"Buying Power: ${float(account.buying_power):,.2f}")
        
        if account.status != 'ACTIVE':
            print(f"❌ Account not active (status: {account.status})")
            return False
        
        print("✅ Account is active!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_crypto_enabled(client):
    """Test 4: Check if crypto is enabled"""
    print("\n" + "="*70)
    print("TEST 4: Crypto Trading")
    print("="*70)
    
    try:
        account = client.get_account()
        print(f"Crypto Status: {account.crypto_status}")
        
        if account.crypto_status != 'ACTIVE':
            print("❌ Crypto trading not enabled!")
            print("\nTo enable:")
            print("1. Go to: https://app.alpaca.markets/paper/dashboard/overview")
            print("2. Settings → Trading Configuration")
            print("3. Enable crypto trading")
            print("4. Wait 5 minutes and try again")
            return False
        
        print("✅ Crypto trading is enabled!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_crypto_data():
    """Test 5: Check if we can get crypto data"""
    print("\n" + "="*70)
    print("TEST 5: Crypto Market Data")
    print("="*70)
    
    try:
        data_client = CryptoHistoricalDataClient()
        
        # Request BTC data (Alpaca wants BTC/USD format with slash!)
        request_params = CryptoBarsRequest(
            symbol_or_symbols=['BTC/USD'],
            timeframe=TimeFrame.Day,
            start=datetime.now() - timedelta(days=7)
        )
        
        bars = data_client.get_crypto_bars(request_params)
        df = bars.df
        
        if df.empty:
            print("❌ No data received")
            return False
        
        # Reset index and filter
        df = df.reset_index()
        df = df[df['symbol'] == 'BTC/USD']
        
        latest = df.iloc[-1]
        print(f"✅ Market data working!")
        print(f"   BTC Latest: ${latest['close']:.2f}")
        print(f"   Data points: {len(df)}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_order_simulation(client):
    """Test 6: Simulate an order (don't actually submit)"""
    print("\n" + "="*70)
    print("TEST 6: Order Simulation")
    print("="*70)
    
    try:
        account = client.get_account()
        buying_power = float(account.buying_power)
        
        # Calculate what we would buy
        position_size = buying_power * 0.45
        
        print(f"Available: ${buying_power:,.2f}")
        print(f"Would buy: ${position_size:,.2f} of BTC")
        print(f"That's ~{position_size / 90000:.6f} BTC")
        print("✅ Order calculation works!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("🚀 ALPACA CRYPTO SETUP VERIFICATION")
    print("="*70)
    print("\nTesting your Alpaca setup before running the trader...")
    
    results = []
    
    # Test 1: API Keys
    results.append(("API Keys", test_api_keys()))
    
    if not results[-1][1]:
        print("\n❌ Setup incomplete. Fix API keys first.")
        return
    
    # Test 2: Connection
    success, client = test_connection()
    results.append(("Connection", success))
    
    if not success:
        print("\n❌ Can't connect. Check your API keys.")
        return
    
    # Test 3: Account Status
    results.append(("Account Status", test_account_status(client)))
    
    # Test 4: Crypto Enabled
    results.append(("Crypto Trading", test_crypto_enabled(client)))
    
    # Test 5: Market Data
    results.append(("Market Data", test_crypto_data()))
    
    # Test 6: Order Simulation
    results.append(("Order Simulation", test_order_simulation(client)))
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:<20} {status}")
        if not passed:
            all_passed = False
    
    print("="*70)
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nYou're ready to run the trader:")
        print("  python alpaca_crypto_paper_trader.py")
        print("\nStart with option 1 (test mode) first!")
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("\nFix the issues above before running the trader.")
        print("Re-run this test after fixes: python test_alpaca_setup.py")
    
    print()


if __name__ == '__main__':
    run_all_tests()
