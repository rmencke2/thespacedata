"""
Backtrader Backtest Runner
Professional backtesting with realistic commissions, slippage, and analytics
"""
import backtrader as bt
import sys
import os
from datetime import datetime, timedelta

# Add paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from strategies.sma_200_strategy import SMA200Strategy, SMA200CrossStrategy
from data.alpaca_feed import get_alpaca_data

def run_backtest(
    strategy_class,
    symbol='SPY',
    initial_cash=100000,
    commission=0.001,  # 0.1% per trade
    fromdate=None,
    todate=None,
    timeframe='4H',
    plot=False
):
    """
    Run a backtest with professional settings
    
    Args:
        strategy_class: Strategy class to test
        symbol: Stock/crypto symbol
        initial_cash: Starting capital
        commission: Commission rate (0.001 = 0.1%)
        fromdate: Start date
        todate: End date
        timeframe: '4H', '1H', '1D', etc.
        plot: Show chart (default False)
    
    Returns:
        dict with results
    """
    
    print("\n" + "="*70)
    print("🚀 BACKTRADER PROFESSIONAL BACKTESTING")
    print("="*70)
    
    # Create Cerebro engine
    cerebro = bt.Cerebro()
    
    # Add strategy
    cerebro.addstrategy(strategy_class, debug=True)
    
    # Set dates
    if not todate:
        todate = datetime.now()
    if not fromdate:
        fromdate = todate - timedelta(days=365)  # 1 year default
    
    print(f"\n📊 Configuration:")
    print(f"   Symbol: {symbol}")
    print(f"   Strategy: {strategy_class.__name__}")
    print(f"   Timeframe: {timeframe}")
    print(f"   Period: {fromdate.date()} to {todate.date()}")
    print(f"   Initial Capital: ${initial_cash:,.0f}")
    print(f"   Commission: {commission*100:.2f}%")
    
    # Add data feed
    print(f"\n📥 Fetching data from Alpaca...")
    
    try:
        data = get_alpaca_data(
            symbol=symbol,
            fromdate=fromdate,
            todate=todate,
            timeframe=timeframe,
            paper=True
        )
        
        cerebro.adddata(data)
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return None
    
    # Set initial cash
    cerebro.broker.setcash(initial_cash)
    
    # Set commission
    cerebro.broker.setcommission(commission=commission)
    
    # Add analyzers
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
    
    # Print starting value
    print(f"\n💰 Starting Portfolio Value: ${cerebro.broker.getvalue():,.2f}")
    
    # Run backtest
    print(f"\n⚡ Running backtest...")
    print("-"*70)
    
    results = cerebro.run()
    strat = results[0]
    
    print("-"*70)
    
    # Print final value
    final_value = cerebro.broker.getvalue()
    pnl = final_value - initial_cash
    return_pct = (pnl / initial_cash) * 100
    
    print(f"\n💰 Final Portfolio Value: ${final_value:,.2f}")
    print(f"📈 Total P&L: ${pnl:,.2f} ({return_pct:+.2f}%)")
    
    # Get analyzer results
    print("\n" + "="*70)
    print("📊 PERFORMANCE ANALYTICS")
    print("="*70)
    
    # Sharpe Ratio
    sharpe = strat.analyzers.sharpe.get_analysis()
    sharpe_ratio = sharpe.get('sharperatio', 0)
    if sharpe_ratio:
        print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
    else:
        print(f"Sharpe Ratio: N/A (insufficient data)")
    
    # Drawdown
    drawdown = strat.analyzers.drawdown.get_analysis()
    max_drawdown = drawdown.get('max', {}).get('drawdown', 0)
    print(f"Max Drawdown: {max_drawdown:.2f}%")
    
    # Returns
    returns = strat.analyzers.returns.get_analysis()
    annual_return = returns.get('rnorm100', 0)
    print(f"Annualized Return: {annual_return:.2f}%")
    
    # Trade Analysis
    trades = strat.analyzers.trades.get_analysis()
    total_trades = trades.get('total', {}).get('total', 0)
    won_trades = trades.get('won', {}).get('total', 0)
    lost_trades = trades.get('lost', {}).get('total', 0)
    
    print(f"\nTotal Trades: {total_trades}")
    
    if total_trades > 0:
        win_rate = (won_trades / total_trades) * 100
        print(f"Winning Trades: {won_trades}")
        print(f"Losing Trades: {lost_trades}")
        print(f"Win Rate: {win_rate:.2f}%")
        
        # Average P&L
        won_pnl = trades.get('won', {}).get('pnl', {}).get('average', 0)
        lost_pnl = trades.get('lost', {}).get('pnl', {}).get('average', 0)
        print(f"Average Win: ${won_pnl:.2f}")
        print(f"Average Loss: ${lost_pnl:.2f}")
        
        # Profit factor
        if lost_pnl != 0:
            profit_factor = abs(won_pnl / lost_pnl)
            print(f"Profit Factor: {profit_factor:.2f}")
    
    print("="*70)
    
    # Plot if requested
    if plot:
        print("\n📊 Generating chart...")
        cerebro.plot(style='candlestick')
    
    # Return results
    return {
        'final_value': final_value,
        'pnl': pnl,
        'return_pct': return_pct,
        'sharpe_ratio': sharpe_ratio if sharpe_ratio else 0,
        'max_drawdown': max_drawdown,
        'total_trades': total_trades,
        'win_rate': (won_trades / total_trades * 100) if total_trades > 0 else 0
    }


def compare_strategies(symbol='SPY', initial_cash=100000):
    """
    Compare multiple strategies side-by-side
    """
    
    print("\n" + "="*70)
    print("⚖️  STRATEGY COMPARISON")
    print("="*70)
    
    strategies = [
        ('200 SMA Trend', SMA200Strategy),
        ('50/200 SMA Cross', SMA200CrossStrategy),
    ]
    
    results = {}
    
    for name, strategy_class in strategies:
        print(f"\n{'='*70}")
        print(f"Testing: {name}")
        print(f"{'='*70}")
        
        result = run_backtest(
            strategy_class=strategy_class,
            symbol=symbol,
            initial_cash=initial_cash,
            timeframe='4H',
            plot=False
        )
        
        if result:
            results[name] = result
    
    # Print comparison
    print("\n" + "="*70)
    print("📊 STRATEGY COMPARISON SUMMARY")
    print("="*70)
    
    for name, result in results.items():
        print(f"\n{name}:")
        print(f"  Return: {result['return_pct']:+.2f}%")
        print(f"  Sharpe: {result['sharpe_ratio']:.2f}")
        print(f"  Max DD: {result['max_drawdown']:.2f}%")
        print(f"  Trades: {result['total_trades']}")
        print(f"  Win Rate: {result['win_rate']:.2f}%")
    
    # Find best strategy
    if results:
        best_strategy = max(results.items(), key=lambda x: x[1]['return_pct'])
        print(f"\n🏆 Best Strategy: {best_strategy[0]} ({best_strategy[1]['return_pct']:+.2f}%)")
    
    print("="*70 + "\n")


def quick_test():
    """Quick test on SPY with default settings"""
    
    print("\n🧪 Running quick test on SPY (4H candles)...")
    
    result = run_backtest(
        strategy_class=SMA200Strategy,
        symbol='SPY',
        initial_cash=100000,
        fromdate=datetime.now() - timedelta(days=180),  # 6 months
        todate=datetime.now(),
        timeframe='4H',
        plot=False
    )
    
    if result:
        print("\n✅ Quick test complete!")
        print("\n💡 Next steps:")
        print("  1. If results look good → Test on more symbols")
        print("  2. Adjust parameters in strategies/sma_200_strategy.py")
        print("  3. Run: compare_strategies() to test multiple strategies")
        print("  4. When ready → Deploy paper trading with live_trader.py")


if __name__ == '__main__':
    """
    Run backtests
    
    Usage:
        python backtest_runner.py                    # Quick test
        python backtest_runner.py --compare          # Compare strategies
        python backtest_runner.py --symbol AAPL      # Test specific symbol
    """
    
    import argparse
    
    parser = argparse.ArgumentParser(description='Backtrader Backtesting')
    parser.add_argument('--symbol', default='SPY', help='Stock symbol')
    parser.add_argument('--compare', action='store_true', help='Compare multiple strategies')
    parser.add_argument('--plot', action='store_true', help='Show chart')
    parser.add_argument('--days', type=int, default=180, help='Days of history')
    
    args = parser.parse_args()
    
    if args.compare:
        compare_strategies(symbol=args.symbol)
    else:
        run_backtest(
            strategy_class=SMA200Strategy,
            symbol=args.symbol,
            initial_cash=100000,
            fromdate=datetime.now() - timedelta(days=args.days),
            todate=datetime.now(),
            timeframe='4H',
            plot=args.plot
        )
