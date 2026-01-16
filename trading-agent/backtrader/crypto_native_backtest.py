"""
Crypto-Native Strategy Backtester
Tests strategies designed SPECIFICALLY for cryptocurrency markets

Not just adjusted stock strategies - these are built from the ground up for crypto!
"""
import backtrader as bt
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from strategies.crypto_momentum_strategy import CryptoMomentumStrategy
from strategies.crypto_flash_crash_strategy import CryptoFlashCrashStrategy
from strategies.sma_200_enhanced import SMA200Enhanced


class CryptoNativeBacktester:
    """Tests crypto-native strategies"""
    
    def __init__(self):
        self.results = {}
    
    def run_backtest(
        self,
        strategy_class,
        strategy_name,
        symbol,
        years=3,
        initial_cash=100000,
        commission=0.001,
        use_daily=True
    ):
        """Run single backtest"""
        
        print(f"\n{'='*70}")
        print(f"₿ Testing: {strategy_name} on {symbol}")
        print(f"{'='*70}")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=years*365)
        
        try:
            ticker = yf.Ticker(symbol)
            interval = '1d' if use_daily else '1h'
            
            print(f"📥 Fetching data...")
            
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
        
        cerebro = bt.Cerebro()
        cerebro.addstrategy(strategy_class, debug=False)
        cerebro.adddata(data)
        
        cerebro.broker.setcash(initial_cash)
        cerebro.broker.setcommission(commission=commission)
        
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        
        print(f"💰 Starting: ${initial_cash:,.0f}")
        
        results = cerebro.run()
        strat = results[0]
        
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
        
        print(f"\n📈 RESULTS:")
        print(f"   Final: ${final_value:,.2f}")
        print(f"   P&L: ${pnl:,.2f} ({return_pct:+.2f}%)")
        print(f"   Sharpe: {sharpe_ratio:.2f}" if sharpe_ratio else "   Sharpe: N/A")
        print(f"   Max DD: {max_dd:.2f}%")
        print(f"   Annual: {annual_return:.2f}%")
        print(f"   Trades: {total_trades} ({win_rate:.1f}% WR)")
        
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
    
    def run_comprehensive_test(self, strategies, crypto_symbols, years=3, use_daily=True):
        """Test all crypto-native strategies"""
        
        print("\n" + "="*70)
        print("🚀 CRYPTO-NATIVE STRATEGY BACKTEST")
        print("="*70)
        print(f"Strategies: {len(strategies)} (CRYPTO-SPECIFIC!)")
        print(f"Cryptos: {', '.join([s.replace('-USD', '') for s in crypto_symbols])}")
        print(f"Period: {years} years")
        print(f"Timeframe: {'Daily' if use_daily else '4H'}")
        print("")
        print("These strategies are designed FROM SCRATCH for crypto:")
        print("  • Momentum: Catches pumps & breakouts")
        print("  • Flash Crash: Buys panic sells")
        print("  • Enhanced SMA: Adapted for crypto volatility")
        print("="*70)
        
        for strategy_name, strategy_class in strategies:
            for symbol in crypto_symbols:
                self.run_backtest(
                    strategy_class=strategy_class,
                    strategy_name=strategy_name,
                    symbol=symbol,
                    years=years,
                    use_daily=use_daily
                )
        
        self.print_comparison()
    
    def print_comparison(self):
        """Print comprehensive comparison"""
        
        if not self.results:
            print("\n❌ No results")
            return
        
        print("\n" + "="*100)
        print("₿ CRYPTO-NATIVE STRATEGY COMPARISON")
        print("="*100)
        
        print(f"{'Strategy':<35} {'Crypto':<8} {'Return':<12} {'Sharpe':<8} {'MaxDD':<9} {'Trades':<8} {'WinRate'}")
        print("-"*100)
        
        sorted_results = sorted(
            self.results.items(),
            key=lambda x: x[1]['return_pct'],
            reverse=True
        )
        
        for key, result in sorted_results:
            crypto_name = result['symbol'].replace('-USD', '')
            print(
                f"{result['strategy']:<35} "
                f"{crypto_name:<8} "
                f"{result['return_pct']:>11.2f}% "
                f"{result['sharpe']:>7.2f} "
                f"{result['max_dd']:>8.2f}% "
                f"{result['total_trades']:>7} "
                f"{result['win_rate']:>7.1f}%"
            )
        
        print("="*100)
        
        # Strategy summaries
        print("\n" + "="*70)
        print("📊 STRATEGY AVERAGES")
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
        print("🏆 TOP PERFORMERS")
        print("="*70)
        
        best_return = max(self.results.items(), key=lambda x: x[1]['return_pct'])
        best_sharpe = max(self.results.items(), key=lambda x: x[1]['sharpe'])
        best_wr = max(self.results.items(), key=lambda x: x[1]['win_rate'])
        
        print(f"\n💰 Highest Return:")
        print(f"   {best_return[1]['strategy']} on {best_return[1]['symbol']}")
        print(f"   {best_return[1]['return_pct']:+.2f}%")
        
        print(f"\n📊 Best Risk-Adjusted:")
        print(f"   {best_sharpe[1]['strategy']} on {best_sharpe[1]['symbol']}")
        print(f"   Sharpe: {best_sharpe[1]['sharpe']:.2f}")
        
        print(f"\n🎯 Most Consistent:")
        print(f"   {best_wr[1]['strategy']} on {best_wr[1]['symbol']}")
        print(f"   Win Rate: {best_wr[1]['win_rate']:.1f}%")
        
        print("="*70)
        
        # Recommendations
        print("\n" + "="*70)
        print("💡 STRATEGY ANALYSIS")
        print("="*70)
        
        for strat_name, results_list in strategies.items():
            print(f"\n{strat_name}:")
            
            if 'Momentum' in strat_name:
                print("  📈 Designed to: Catch pumps, breakouts, whale activity")
                print("  ✅ Works best: During bull markets & parabolic moves")
                print("  ❌ Struggles: Sideways/choppy markets")
            elif 'Flash Crash' in strat_name:
                print("  💥 Designed to: Buy panic sells, catch bounces")
                print("  ✅ Works best: Volatile markets, flash crashes")
                print("  ❌ Struggles: Steady uptrends (no crashes to buy)")
            elif 'Enhanced' in strat_name:
                print("  🎯 Designed to: Filtered trend following")
                print("  ✅ Works best: Clear trends with good volume")
                print("  ❌ Struggles: Whipsaw markets")
        
        # Best overall
        strategy_scores = {}
        for strat_name, results_list in strategies.items():
            avg_return = sum(r['return_pct'] for r in results_list) / len(results_list)
            avg_sharpe = max(sum(r['sharpe'] for r in results_list) / len(results_list), 0.1)
            avg_dd = sum(r['max_dd'] for r in results_list) / len(results_list)
            avg_wr = sum(r['win_rate'] for r in results_list) / len(results_list)
            
            score = avg_return * avg_sharpe * (1 - avg_dd/100) * (avg_wr/100)
            strategy_scores[strat_name] = score
        
        best_overall = max(strategy_scores.items(), key=lambda x: x[1])
        
        print(f"\n🌟 OVERALL WINNER: {best_overall[0]}")
        print(f"   Composite Score: {best_overall[1]:.2f}")
        print("\n   This strategy has the best balance of:")
        print("   • High returns")
        print("   • Good risk management (Sharpe)")
        print("   • Controlled drawdowns")
        print("   • Consistent wins")
        
        print("\n💰 Ready to paper trade?")
        print("   ✅ Pick the winner above")
        print("   ✅ Test on BTC or ETH (most liquid)")
        print("   ✅ Start with $500-1000 real money")
        print("   ✅ Track for 2-3 months")
        print("   ✅ Scale up if working!")
        
        print("="*70 + "\n")


if __name__ == '__main__':
    """Run crypto-native backtest"""
    
    tester = CryptoNativeBacktester()
    
    # Crypto-native strategies
    strategies = [
        ('Crypto Momentum Breakout', CryptoMomentumStrategy),
        ('Crypto Flash Crash Buy', CryptoFlashCrashStrategy),
        ('Enhanced SMA (Crypto-Tuned)', SMA200Enhanced),
    ]
    
    # Major cryptos
    crypto_symbols = [
        'BTC-USD',
        'ETH-USD',
        'BNB-USD',
        'SOL-USD',
        'ADA-USD',
    ]
    
    print("\n🚀 Testing CRYPTO-NATIVE strategies...")
    print("   (Not just adjusted stock strategies!)")
    print("   This will take 5-10 minutes...\n")
    
    tester.run_comprehensive_test(
        strategies=strategies,
        crypto_symbols=crypto_symbols,
        years=3,
        use_daily=True
    )
    
    print("\n✅ Complete!")
    print("\n💡 Compare these to your stock results:")
    print("   • Crypto should have MUCH higher returns")
    print("   • But also higher drawdowns")
    print("   • Different strategies win on different cryptos")
    print("   • Momentum vs Flash Crash = different market conditions\n")
