"""
System Test Script
Verify that all components are working correctly
"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from utils.config import Config
        from utils.data_fetcher import DataFetcher
        from utils.database import TradingDatabase
        from strategies.mean_reversion import MeanReversionStrategy
        from strategies.momentum import MomentumStrategy
        from agents.market_analyzer import MarketAnalyzerAgent
        from agents.strategy_agent import StrategyAgent
        from agents.risk_manager import RiskManagerAgent
        from agents.execution_agent import ExecutionAgent
        from graph_orchestrator import TradingOrchestrator
        print("✅ All imports successful!\n")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}\n")
        return False

def test_configuration():
    """Test configuration"""
    print("🧪 Testing configuration...")
    
    from utils.config import Config
    
    Config.print_config()
    
    if Config.validate():
        print("✅ Configuration valid!\n")
        return True
    else:
        print("⚠️  Alpaca keys not configured (this is OK for testing)\n")
        return True  # Still pass, just warn

def test_data_fetcher():
    """Test data fetching"""
    print("🧪 Testing data fetcher...")
    
    from utils.data_fetcher import DataFetcher
    
    fetcher = DataFetcher()
    
    # Try to fetch recent data for one symbol
    data = fetcher.get_latest_bars(['TSLA'], days=5)
    
    if 'TSLA' in data and not data['TSLA'].empty:
        print(f"✅ Data fetcher working! Got {len(data['TSLA'])} bars for TSLA\n")
        return True
    else:
        print("❌ Data fetcher failed\n")
        return False

def test_database():
    """Test database operations"""
    print("🧪 Testing database...")
    
    from utils.database import TradingDatabase
    import os
    
    # Use a test database
    test_db = "test_system.db"
    db = TradingDatabase(test_db)
    
    # Log a test trade
    trade = {
        'symbol': 'TEST',
        'side': 'buy',
        'quantity': 10,
        'entry_price': 100.00,
        'stop_loss': 98.00,
        'strategy': 'test'
    }
    
    trade_id = db.log_trade(trade)
    
    # Close the trade
    db.close_trade(trade_id, 102.00)
    
    # Get summary
    summary = db.get_performance_summary()
    
    # Clean up
    os.remove(test_db)
    
    if summary['total_trades'] == 1 and summary['total_pnl'] > 0:
        print("✅ Database working!\n")
        return True
    else:
        print("❌ Database test failed\n")
        return False

def test_strategies():
    """Test strategy signal generation"""
    print("🧪 Testing strategies...")
    
    from utils.data_fetcher import DataFetcher
    from strategies.mean_reversion import MeanReversionStrategy
    from strategies.momentum import MomentumStrategy
    
    # Get data
    fetcher = DataFetcher()
    data = fetcher.get_latest_bars(['TSLA'], days=60)
    
    if 'TSLA' not in data:
        print("⚠️  Could not get data for strategy test\n")
        return False
    
    # Test mean reversion
    mr_strategy = MeanReversionStrategy()
    mr_signal = mr_strategy.generate_signal(data['TSLA'])
    
    # Test momentum
    mom_strategy = MomentumStrategy()
    mom_signal = mom_strategy.generate_signal(data['TSLA'])
    
    if mr_signal and mom_signal:
        print(f"✅ Strategies working!")
        print(f"   Mean Reversion: {mr_signal['action']}")
        print(f"   Momentum: {mom_signal['action']}\n")
        return True
    else:
        print("❌ Strategy test failed\n")
        return False

def test_agents():
    """Test agent initialization"""
    print("🧪 Testing agents...")
    
    from agents.market_analyzer import MarketAnalyzerAgent
    from agents.strategy_agent import StrategyAgent
    from agents.risk_manager import RiskManagerAgent
    from agents.execution_agent import ExecutionAgent
    
    try:
        analyzer = MarketAnalyzerAgent()
        strategy_agent = StrategyAgent()
        risk_manager = RiskManagerAgent()
        executor = ExecutionAgent()
        
        print("✅ All agents initialized successfully!\n")
        return True
    except Exception as e:
        print(f"❌ Agent initialization failed: {e}\n")
        return False

def test_orchestrator():
    """Test the orchestrator"""
    print("🧪 Testing orchestrator...")
    
    from graph_orchestrator import TradingOrchestrator
    
    try:
        orchestrator = TradingOrchestrator(portfolio_value=10000)
        print("✅ Orchestrator initialized successfully!\n")
        return True
    except Exception as e:
        print(f"❌ Orchestrator initialization failed: {e}\n")
        return False

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("RUNNING SYSTEM TESTS")
    print("="*70 + "\n")
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_configuration),
        ("Data Fetcher", test_data_fetcher),
        ("Database", test_database),
        ("Strategies", test_strategies),
        ("Agents", test_agents),
        ("Orchestrator", test_orchestrator)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}\n")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n" + "-"*70)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready to use.")
        print("\nNext steps:")
        print("  1. Run a backtest: python run_backtest.py")
        print("  2. Test live trading: python run_live.py --mode once")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("\nCommon issues:")
        print("  - Missing dependencies: pip install -r requirements.txt")
        print("  - No internet: Check your connection")
        print("  - Alpaca keys: Set up .env file (optional for testing)")
    
    print("="*70 + "\n")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
