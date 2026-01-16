"""
Comprehensive Backtesting System
Tests all strategies on multiple symbols over 5 years
Provides detailed comparison and performance metrics
"""
import backtrader as bt
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from strategies.sma_200_strategy import SMA200Strategy
from strategies.sma_200_enhanced import SMA200Enhanced
from strategies.multi_indicator_strategy import MultiIndicatorStrategy


class ComprehensiveBacktester:
    """
    Tests multiple strategies on multiple symbols
    """
    
    def __init__(self):
        self.results = {}
    
    def run_backtest(
        self,
        strategy_class,
        strategy_name,
        symbol,
        years=5,
        initial_cash=100000,
        commission=0.001,
        use_daily=True
    ):
        """Run single backtest"""
        
        print(f"\n{'='*70}")
        print(f"📊 Testing: {strategy_name} on {symbol}")
        print(f"{'='*70}")
        
        # Get data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=years*365)
        
        try:
            ticker = yf.Ticker(symbol)
            interval = '1d' if use_daily else '1h'
            
            df = ticker.history(
                start=start_date,
                end=end_date,
                interval=interval,
                auto_adjust=True
            )
            
            if df.empty:
                print(f"❌ No data for {symbol}")
                return None
            
            # Aggregate to 4H if needed
            if not use_daily and interval == '1h':
                df.columns = df.columns.str.lower()
                df = df.resample('4h').agg({
                    'open': 'first',
                    'high': 'max',
                    'low': 'min',
                    'close': 'last',
                    'volume': 'sum'
                }).dropna()
            
            print(f"✅ Loaded {len(df)} bars")
            
            # Create feed
            data = bt.feeds.PandasData(
                dataname=df,
                datetime=None,
                open='open' if 'open' in df.columns else 'Open',
                high='high' if 'high' in df.columns else 'High',
                low='low' if 'low' in df.columns else 'Low',
                close='close' if 'close' in df.columns else 'Close',
                volume='volume' if 'volume' in df.columns else 'Volume',
                openinterest=-1
            )
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
        
        # Create Cerebro
        cerebro = bt.Cerebro()
        cerebro.addstrategy(strategy_class, debug=False)
        cerebro.adddata(data)
        
        # Setup
        cerebro.broker.setcash(initial_cash)
        cerebro.broker.setcommission(commission=commission)
        
        # Analyzers
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        
        print(f"💰 Starting: ${initial_cash:,.0f}")
        
        # Run
        results = cerebro.run()
        strat = results[0]
        
        # Get results
        final_value = cerebro.broker.getvalue()
        pnl = final_value - initial_cash
        return_pct = (pnl / initial_cash) * 100
        
        sharpe = strat.analyzers.sharpe.get_analysis()
        sharpe_ratio = sharpe.get('sharperatio', None)
        
        drawdown = strat.analyzers.drawdown.get_analysis()
        max_dd = drawdown.get('max', {}).get('drawdown', 0)
        
        returns = strat.analyzers.returns.get_analysis()
        annual_return = returns.get('rnorm100', 0)
        
        trades = strat.analyzers.trades.get_analysis()
        total_trades = trades.get('total', {}).get('total', 0)
        won = trades.get('won', {}).get('total', 0)
        lost = trades.get('lost', {}).get('total', 0)
        
        win_rate = (won / total_trades * 100) if total_trades > 0 else 0
        
        # Print summary
        print(f"\n📈 RESULTS:")
        print(f"   Final Value: ${final_value:,.2f}")
        print(f"   P&L: ${pnl:,.2f} ({return_pct:+.2f}%)")
        print(f"   Sharpe: {sharpe_ratio:.2f}" if sharpe_ratio else "   Sharpe: N/A")
        print(f"   Max DD: {max_dd:.2f}%")
        print(f"   Annual Return: {annual_return:.2f}%")
        print(f"   Trades: {total_trades} ({win_rate:.1f}% win rate)")
        
        # Store results
        result_key = f"{strategy_name}_{symbol}"
        self.results[result_key] = {
            'strategy': strategy_name,
            'symbol': symbol,
            'final_value': final_value,
            'pnl': pnl,
            'return_pct': return_pct,
            'sharpe': sharpe_ratio if sharpe_ratio else 0,
            'max_dd': max_dd,
            'annual_return': annual_return,
            'total_trades': total_trades,
            'win_rate': win_rate,
            'wins': won,
            'losses': lost
        }
        
        return self.results[result_key]
    
    def run_comprehensive_test(
        self,
        strategies,
        symbols,
        years=5,
        use_daily=True
    ):
        """Test all strategies on all symbols"""
        
        print("\n" + "="*70)
        print("🚀 COMPREHENSIVE BACKTEST")
        print("="*70)
        print(f"Strategies: {len(strategies)}")
        print(f"Symbols: {', '.join(symbols)}")
        print(f"Period: {years} years")
        print(f"Timeframe: {'Daily' if use_daily else '4H'}")
        print("="*70)
        
        for strategy_name, strategy_class in strategies:
            for symbol in symbols:
                self.run_backtest(
                    strategy_class=strategy_class,
                    strategy_name=strategy_name,
                    symbol=symbol,
                    years=years,
                    use_daily=use_daily
                )
        
        # Print comparison
        self.print_comparison()
    
    def print_comparison(self):
        """Print detailed comparison table"""
        
        if not self.results:
            print("\n❌ No results to compare")
            return
        
        print("\n" + "="*100)
        print("📊 STRATEGY COMPARISON TABLE")
        print("="*100)
        
        # Header
        print(f"{'Strategy':<30} {'Symbol':<8} {'Return':<10} {'Sharpe':<8} {'MaxDD':<8} {'Trades':<8} {'WinRate':<8}")
        print("-"*100)
        
        # Sort by return
        sorted_results = sorted(
            self.results.items(),
            key=lambda x: x[1]['return_pct'],
            reverse=True
        )
        
        for key, result in sorted_results:
            print(
                f"{result['strategy']:<30} "
                f"{result['symbol']:<8} "
                f"{result['return_pct']:>9.2f}% "
                f"{result['sharpe']:>7.2f} "
                f"{result['max_dd']:>7.2f}% "
                f"{result['total_trades']:>7} "
                f"{result['win_rate']:>7.1f}%"
            )
        
        print("="*100)
        
        # Summary by strategy
        print("\n" + "="*70)
        print("📈 STRATEGY SUMMARY (Averaged across all symbols)")
        print("="*70)
        
        strategies = {}
        for key, result in self.results.items():
            strat_name = result['strategy']
            if strat_name not in strategies:
                strategies[strat_name] = []
            strategies[strat_name].append(result)
        
        for strat_name, results_list in strategies.items():
            avg_return = sum(r['return_pct'] for r in results_list) / len(results_list)
            avg_sharpe = sum(r['sharpe'] for r in results_list) / len(results_list)
            avg_dd = sum(r['max_dd'] for r in results_list) / len(results_list)
            avg_trades = sum(r['total_trades'] for r in results_list) / len(results_list)
            avg_wr = sum(r['win_rate'] for r in results_list) / len(results_list)
            
            print(f"\n{strat_name}:")
            print(f"  Avg Return: {avg_return:+.2f}%")
            print(f"  Avg Sharpe: {avg_sharpe:.2f}")
            print(f"  Avg Max DD: {avg_dd:.2f}%")
            print(f"  Avg Trades: {avg_trades:.0f}")
            print(f"  Avg Win Rate: {avg_wr:.1f}%")
        
        print("="*70)
        
        # Best performers
        print("\n" + "="*70)
        print("🏆 BEST PERFORMERS")
        print("="*70)
        
        best_return = max(self.results.items(), key=lambda x: x[1]['return_pct'])
        best_sharpe = max(self.results.items(), key=lambda x: x[1]['sharpe'])
        best_wr = max(self.results.items(), key=lambda x: x[1]['win_rate'])
        
        print(f"\n🥇 Best Return: {best_return[1]['strategy']} on {best_return[1]['symbol']}")
        print(f"   Return: {best_return[1]['return_pct']:+.2f}%")
        
        print(f"\n📊 Best Sharpe: {best_sharpe[1]['strategy']} on {best_sharpe[1]['symbol']}")
        print(f"   Sharpe: {best_sharpe[1]['sharpe']:.2f}")
        
        print(f"\n🎯 Best Win Rate: {best_wr[1]['strategy']} on {best_wr[1]['symbol']}")
        print(f"   Win Rate: {best_wr[1]['win_rate']:.1f}%")
        
        print("="*70)
        
        # Recommendations
        print("\n" + "="*70)
        print("💡 RECOMMENDATIONS")
        print("="*70)
        
        # Find most consistent strategy
        strategy_scores = {}
        for strat_name, results_list in strategies.items():
            # Score = avg return * avg sharpe * (1 - avg_dd/100) * (avg_wr/100)
            avg_return = sum(r['return_pct'] for r in results_list) / len(results_list)
            avg_sharpe = max(sum(r['sharpe'] for r in results_list) / len(results_list), 0.1)
            avg_dd = sum(r['max_dd'] for r in results_list) / len(results_list)
            avg_wr = sum(r['win_rate'] for r in results_list) / len(results_list)
            
            score = avg_return * avg_sharpe * (1 - avg_dd/100) * (avg_wr/100)
            strategy_scores[strat_name] = score
        
        best_overall = max(strategy_scores.items(), key=lambda x: x[1])
        
        print(f"\n🌟 Best Overall Strategy: {best_overall[0]}")
        print(f"   Composite Score: {best_overall[1]:.2f}")
        print("\n✅ This strategy shows the best balance of:")
        print("   - Consistent returns")
        print("   - Risk-adjusted performance (Sharpe)")
        print("   - Drawdown control")
        print("   - Win rate")
        
        print("\n💰 Ready for paper trading? Check if:")
        print("   ✅ Return > 10% annually")
        print("   ✅ Sharpe > 1.0")
        print("   ✅ Max DD < 15%")
        print("   ✅ Win Rate > 50%")
        print("   ✅ Profitable on multiple symbols")
        
        print("="*70 + "\n")


if __name__ == '__main__':
    """Run comprehensive backtest"""
    
    # Initialize
    tester = ComprehensiveBacktester()
    
    # Define strategies to test
    strategies = [
        ('Basic 200 SMA', SMA200Strategy),
        ('Enhanced (RSI+Vol)', SMA200Enhanced),
        ('Multi-Indicator', MultiIndicatorStrategy),
    ]
    
    # Define symbols to test
    symbols = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'NVDA']
    
    # Run comprehensive test
    print("\n💡 Starting comprehensive backtest...")
    print("   This will take a few minutes...\n")
    
    tester.run_comprehensive_test(
        strategies=strategies,
        symbols=symbols,
        years=5,
        use_daily=True  # Daily candles
    )
    
    print("\n✅ Backtest complete!")
    print("\n💡 Next steps:")
    print("   1. Review the results above")
    print("   2. Pick the best strategy")
    print("   3. Paper trade it for 1-2 months")
    print("   4. Only then consider real money\n")
