"""
Crypto Strategy Backtest
Tests crypto-optimized mean reversion on historical crypto data
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from utils.data_fetcher_crypto import DataFetcher
from strategies.crypto_mean_reversion import CryptoMeanReversionStrategy
import config_crypto as Config

def get_value(d, *keys, default=0):
    """Safely get value from dict with multiple possible keys"""
    for key in keys:
        if key in d:
            return d[key]
    return default

def print_results(results, symbol):
    """Print backtest results for crypto"""
    print("\n" + "="*70)
    print(f"🪙 CRYPTO BACKTEST: {symbol}")
    print("="*70)
    print(f"Total Trades: {get_value(results, 'total_trades')}")
    print(f"Winning Trades: {get_value(results, 'winning_trades')}")
    print(f"Losing Trades: {get_value(results, 'losing_trades')}")
    print(f"Win Rate: {get_value(results, 'win_rate'):.2f}%")
    print()
    print(f"Total Return: ${get_value(results, 'total_return'):.2f}")
    print(f"Total Return %: {get_value(results, 'total_return_pct', 'total_return_percent'):.2f}%")
    print()
    print(f"Average Win: ${get_value(results, 'avg_win'):.2f}")
    print(f"Average Loss: ${get_value(results, 'avg_loss'):.2f}")
    print(f"Profit Factor: {get_value(results, 'profit_factor'):.2f}")
    print("="*70)
    
    # Show sample trades
    trades = results.get('trades', [])
    if trades:
        print("\nSample Trades (First 5):")
        print("-"*70)
        
        # Show flash crash trades if any
        flash_crash_trades = [t for t in trades if 'flash' in t.get('exit_reason', '').lower()]
        if flash_crash_trades:
            print("\n🚨 FLASH CRASH TRADES:")
            for i, trade in enumerate(flash_crash_trades[:3], 1):
                direction = get_value(trade, 'type', 'direction', default='UNKNOWN')
                entry = get_value(trade, 'entry_price', default=0)
                exit_price = get_value(trade, 'exit_price', default=0)
                pnl = get_value(trade, 'pnl', default=0)
                pnl_pct = get_value(trade, 'pnl_pct', 'pnl_percent', default=0)
                conf = get_value(trade, 'confidence', default=0)
                
                print(f"{i}. {direction}: ${entry:,.2f} → ${exit_price:,.2f} | "
                      f"P&L: ${pnl:.2f} ({pnl_pct*100:+.2f}%) | Conf: {conf:.0%}")
        
        print("\n📊 REGULAR TRADES:")
        sample_trades = trades[:5]
        for i, trade in enumerate(sample_trades, 1):
            direction = get_value(trade, 'type', 'direction', default='UNKNOWN')
            entry = get_value(trade, 'entry_price', default=0)
            exit_price = get_value(trade, 'exit_price', default=0)
            pnl = get_value(trade, 'pnl', default=0)
            pnl_pct = get_value(trade, 'pnl_pct', 'pnl_percent', default=0)
            conf = get_value(trade, 'confidence', default=0)
            
            print(f"{i}. {direction}: ${entry:,.2f} → ${exit_price:,.2f} | "
                  f"P&L: ${pnl:.2f} ({pnl_pct*100:+.2f}%) | Conf: {conf:.0%}")
        print("-"*70)

def run_crypto_backtest():
    """Run backtest on crypto pairs"""
    
    print("\n" + "="*70)
    print("🪙 CRYPTO STRATEGY BACKTEST")
    print("="*70)
    
    print("\n📊 Configuration:")
    print(f"  Initial Capital: ${Config.Config.INITIAL_CAPITAL:,}")
    print(f"  Crypto Pairs: {', '.join(Config.Config.STOCK_UNIVERSE)}")
    print(f"  Mean Reversion Std: {Config.Config.MEAN_REVERSION_STD}")
    print(f"  Stop Loss: {Config.Config.STOP_LOSS_PERCENT*100:.1f}%")
    print(f"  Daily Loss Limit: {Config.Config.DAILY_LOSS_LIMIT*100:.1f}%")
    
    # Fetch crypto data
    print("\n📊 Fetching crypto historical data...")
    print("⚠️  Note: Using last 365 days (crypto trades 24/7)")
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    print(f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print()
    
    fetcher = DataFetcher()
    
    # Get crypto data
    crypto_pairs = Config.Config.STOCK_UNIVERSE
    data = {}
    
    for symbol in crypto_pairs:
        print(f"Fetching {symbol}...")
        try:
            df_dict = fetcher.get_historical_data(
                [symbol],
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d'),
                '1d'
            )
            if symbol in df_dict and not df_dict[symbol].empty:
                data[symbol] = df_dict[symbol]
                print(f"✅ {symbol}: {len(df_dict[symbol])} bars")
            else:
                print(f"⚠️  {symbol}: No data")
        except Exception as e:
            print(f"❌ {symbol}: Error - {e}")
    
    if not data:
        print("\n❌ No crypto data available!")
        print("Make sure your Alpaca account has crypto access enabled.")
        return
    
    # Initialize crypto strategy
    strategy = CryptoMeanReversionStrategy(
        period=Config.Config.MEAN_REVERSION_PERIOD,
        std_dev=Config.Config.MEAN_REVERSION_STD
    )
    
    # Run backtest on each pair
    print("\n" + "="*70)
    print("RUNNING BACKTESTS")
    print("="*70)
    
    all_results = {}
    
    for symbol, df in data.items():
        print(f"\n🔄 Backtesting {symbol}...")
        results = strategy.backtest(df, initial_capital=10000)
        print_results(results, symbol)
        all_results[symbol] = results
    
    # Print summary
    print("\n" + "="*70)
    print("📊 CRYPTO BACKTEST SUMMARY")
    print("="*70)
    
    total_return = sum(get_value(r, 'total_return') for r in all_results.values())
    total_trades = sum(get_value(r, 'total_trades') for r in all_results.values())
    total_wins = sum(get_value(r, 'winning_trades') for r in all_results.values())
    
    win_rate = (total_wins / total_trades * 100) if total_trades > 0 else 0
    
    print(f"\n💰 Combined Performance:")
    print(f"  Total Return: ${total_return:.2f}")
    print(f"  Total Trades: {total_trades}")
    print(f"  Win Rate: {win_rate:.2f}%")
    
    if total_trades > 0:
        avg_per_trade = total_return / total_trades
        print(f"  Avg Per Trade: ${avg_per_trade:.2f}")
        
        # Calculate annualized return
        days = 365
        annual_return = (total_return / (10000 * len(all_results))) * (365 / days) * 100
        print(f"  Annualized Return: {annual_return:.1f}%")
    
    # Best performers
    print("\n🏆 Best Performing Pairs:")
    sorted_results = sorted(
        all_results.items(),
        key=lambda x: get_value(x[1], 'total_return_pct', 'total_return_percent'),
        reverse=True
    )
    
    for i, (symbol, results) in enumerate(sorted_results, 1):
        pct = get_value(results, 'total_return_pct', 'total_return_percent')
        trades = get_value(results, 'total_trades')
        win_rate = get_value(results, 'win_rate')
        
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
        print(f"  {medal} {symbol}: {pct:+.2f}% ({trades} trades, {win_rate:.1f}% win rate)")
    
    print("\n" + "="*70)
    print("\n💡 Crypto Strategy Features Used:")
    print("  🚨 Flash crash detection (15%+ drops)")
    print("  📊 Extreme RSI levels (25-75)")
    print("  📈 Volume spike detection")
    print("  ⚡ Fast exits (0.3 std dev)")
    print("  💪 Wider bands (1.5 std dev)")
    
    print("\n🎯 Next Steps:")
    print("  1. If results are good → Deploy with: ./start_all.sh")
    print("  2. If results need work → Adjust config_crypto.py parameters")
    print("  3. Compare to stock strategies → python compare_strategies.py")
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    run_crypto_backtest()
