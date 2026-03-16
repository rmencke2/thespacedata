"""
Backtest Trading Strategies - FIXED VERSION
Tests strategies on historical data with safe key handling
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from utils.data_fetcher import DataFetcher
from utils.config import Config
from strategies.mean_reversion import MeanReversionStrategy
from strategies.momentum import MomentumStrategy

def get_value(d, *keys, default=0):
    """Safely get value from dict with multiple possible keys"""
    for key in keys:
        if key in d:
            return d[key]
    return default

def print_results(results, symbol):
    """Print backtest results - safe version"""
    print("\n" + "="*70)
    strategy_name = get_value(results, 'strategy', 'name', default='UNKNOWN')
    print(f"BACKTEST RESULTS: {symbol} - {strategy_name.upper()}")
    print("="*70)
    print(f"Total Trades: {get_value(results, 'total_trades')}")
    print(f"Winning Trades: {get_value(results, 'winning_trades')}")
    print(f"Losing Trades: {get_value(results, 'losing_trades')}")
    print(f"Win Rate: {get_value(results, 'win_rate'):.2f}%")
    print()
    print(f"Total Return: ${get_value(results, 'total_return'):.2f}")
    
    # Handle both key names for return percentage
    pct = get_value(results, 'total_return_pct', 'total_return_percent')
    print(f"Total Return %: {pct:.2f}%")
    print()
    print(f"Average Win: ${get_value(results, 'avg_win'):.2f}")
    print(f"Average Loss: ${get_value(results, 'avg_loss'):.2f}")
    print(f"Profit Factor: {get_value(results, 'profit_factor'):.2f}")
    print("="*70)

def run_strategy_backtest(strategy, symbol, data):
    """Run backtest for a single symbol"""
    if symbol not in data:
        print(f"⚠️  No data for {symbol}")
        return None
    
    df = data[symbol]
    results = strategy.backtest(df, initial_capital=10000)
    
    print(f"\n🔄 Backtesting {strategy.name} on {symbol}...")
    print_results(results, symbol)
    
    # Print sample trades if available
    trades = results.get('trades', [])
    if trades:
        print("\nSample Trades:")
        print("-"*70)
        sample_trades = trades[:5]  # First 5 trades
        for i, trade in enumerate(sample_trades, 1):
            direction = get_value(trade, 'type', 'direction', default='UNKNOWN')
            entry = get_value(trade, 'entry_price', default=0)
            exit_price = get_value(trade, 'exit_price', default=0)
            pnl = get_value(trade, 'pnl', default=0)
            
            # Handle pnl_pct (stored as decimal, e.g., 0.05 = 5%)
            pnl_pct = get_value(trade, 'pnl_pct', 'pnl_percent', default=0)
            
            print(f"{i}. {direction}: ${entry:.2f} → ${exit_price:.2f} | "
                  f"P&L: ${pnl:.2f} ({pnl_pct*100:+.2f}%)")
        print("-"*70)
    
    return results

def run_full_backtest():
    """Run comprehensive backtest on all strategies"""
    
    print("\n" + "="*70)
    print("STARTING COMPREHENSIVE BACKTEST")
    print("="*70)
    
    # Print config
    Config.print_config()
    
    # Fetch historical data
    print("\n📊 Fetching historical data...")
    start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')
    print(f"Period: {start_date} to {end_date}")
    print(f"Symbols: {', '.join(Config.STOCK_UNIVERSE)}")
    print()
    
    fetcher = DataFetcher()
    data = fetcher.get_historical_data(
        Config.STOCK_UNIVERSE,
        start_date,
        end_date,
        interval='1d'
    )
    
    # Initialize strategies
    strategies = [
        MeanReversionStrategy(
            Config.MEAN_REVERSION_PERIOD,
            Config.MEAN_REVERSION_STD
        ),
        MomentumStrategy(
            getattr(Config, 'MOMENTUM_FAST', 10),
            getattr(Config, 'MOMENTUM_SLOW', 30)
        )
    ]
    
    # Run backtests
    all_results = {}
    
    for strategy in strategies:
        print("\n" + "="*70)
        print(f"TESTING STRATEGY: {strategy.name.upper()}")
        print("="*70)
        
        strategy_results = {}
        
        for symbol in Config.STOCK_UNIVERSE:
            results = run_strategy_backtest(strategy, symbol, data)
            if results:
                strategy_results[symbol] = results
        
        all_results[strategy.name] = strategy_results
    
    # Print summary
    print("\n" + "="*70)
    print("BACKTEST SUMMARY")
    print("="*70)
    
    for strategy_name, results in all_results.items():
        if not results:
            continue
            
        print(f"\n{strategy_name.upper()}:")
        print("-"*70)
        
        total_return = sum(get_value(r, 'total_return') for r in results.values())
        total_trades = sum(get_value(r, 'total_trades') for r in results.values())
        
        # Calculate overall win rate
        total_wins = sum(get_value(r, 'winning_trades') for r in results.values())
        win_rate = (total_wins / total_trades * 100) if total_trades > 0 else 0
        
        print(f"  Total Return: ${total_return:.2f}")
        print(f"  Total Trades: {total_trades}")
        print(f"  Win Rate: {win_rate:.2f}%")
        
        # Top performers
        print("\n  Best Performing:")
        
        # Safe sorting with fallback
        sorted_results = sorted(
            results.items(),
            key=lambda x: get_value(x[1], 'total_return_pct', 'total_return_percent'),
            reverse=True
        )[:3]
        
        for symbol, r in sorted_results:
            pct = get_value(r, 'total_return_pct', 'total_return_percent')
            trades = get_value(r, 'total_trades')
            print(f"    {symbol}: {pct:+.2f}% ({trades} trades)")
    
    print("\n" + "="*70)
    print("\n✅ Backtest complete!")
    print("\n💡 Next steps:")
    print("  1. Review the results above")
    print("  2. Adjust strategy parameters in utils/config.py if needed")
    print("  3. Run live paper trading: python run_live.py")
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    run_full_backtest()
