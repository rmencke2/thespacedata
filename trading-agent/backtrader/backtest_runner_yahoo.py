"""
Backtest Runner using Yahoo Finance - FIXED with --daily support
"""
import backtrader as bt
import yfinance as yf
import pandas as pd
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from strategies.sma_200_strategy import SMA200Strategy

def run_backtest_yahoo(
    strategy_class,
    symbol='SPY',
    initial_cash=100000,
    commission=0.001,
    days=180,
    use_daily=False,  # NEW!
    plot=False
):
    """Run backtest using Yahoo Finance data"""
    
    print("\n" + "="*70)
    print("🚀 BACKTRADER + YAHOO FINANCE (FREE!)")
    print("="*70)
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Choose interval based on flag
    if use_daily:
        interval = '1d'
        timeframe_display = 'Daily'
    else:
        interval = '1h'
        timeframe_display = '4H (aggregated from 1H)'
    
    print(f"\n📊 Configuration:")
    print(f"   Symbol: {symbol}")
    print(f"   Strategy: {strategy_class.__name__}")
    print(f"   Timeframe: {timeframe_display}")
    print(f"   Period: {start_date.date()} to {end_date.date()}")
    print(f"   Initial Capital: ${initial_cash:,.0f}")
    print(f"   Commission: {commission*100:.2f}%")
    
    print(f"\n📥 Fetching data from Yahoo Finance...")
    
    try:
        ticker = yf.Ticker(symbol)
        
        df = ticker.history(
            start=start_date,
            end=end_date,
            interval=interval,
            auto_adjust=True
        )
        
        if df.empty:
            print(f"❌ No data for {symbol}")
            return None
        
        print(f"✅ Fetched {len(df)} bars ({timeframe_display})")
        
        # Aggregate to 4H if using hourly data
        if not use_daily and interval == '1h':
            df.columns = df.columns.str.lower()
            df_4h = df.resample('4h').agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum'
            }).dropna()
            
            print(f"✅ Aggregated to {len(df_4h)} 4H bars")
            df = df_4h
        
        # Create Backtrader feed
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
        import traceback
        traceback.print_exc()
        return None
    
    # Create Cerebro
    cerebro = bt.Cerebro()
    cerebro.addstrategy(strategy_class, debug=True)
    cerebro.adddata(data)
    
    # Setup broker
    cerebro.broker.setcash(initial_cash)
    cerebro.broker.setcommission(commission=commission)
    
    # Add analyzers
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
    
    print(f"\n💰 Starting Portfolio Value: ${cerebro.broker.getvalue():,.2f}")
    print(f"\n⚡ Running backtest...")
    print("-"*70)
    
    results = cerebro.run()
    strat = results[0]
    
    print("-"*70)
    
    # Results
    final_value = cerebro.broker.getvalue()
    pnl = final_value - initial_cash
    return_pct = (pnl / initial_cash) * 100
    
    print(f"\n💰 Final Portfolio Value: ${final_value:,.2f}")
    print(f"📈 Total P&L: ${pnl:,.2f} ({return_pct:+.2f}%)")
    
    # Analytics
    print("\n" + "="*70)
    print("📊 PERFORMANCE ANALYTICS")
    print("="*70)
    
    sharpe = strat.analyzers.sharpe.get_analysis()
    sharpe_ratio = sharpe.get('sharperatio', None)
    if sharpe_ratio:
        print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
    else:
        print(f"Sharpe Ratio: N/A")
    
    drawdown = strat.analyzers.drawdown.get_analysis()
    max_drawdown = drawdown.get('max', {}).get('drawdown', 0)
    print(f"Max Drawdown: {max_drawdown:.2f}%")
    
    returns = strat.analyzers.returns.get_analysis()
    annual_return = returns.get('rnorm100', 0)
    print(f"Annualized Return: {annual_return:.2f}%")
    
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
        
        won_pnl = trades.get('won', {}).get('pnl', {}).get('average', 0)
        lost_pnl = trades.get('lost', {}).get('pnl', {}).get('average', 0)
        print(f"Average Win: ${won_pnl:.2f}")
        print(f"Average Loss: ${lost_pnl:.2f}")
        
        if lost_pnl != 0:
            profit_factor = abs(won_pnl / lost_pnl)
            print(f"Profit Factor: {profit_factor:.2f}")
    
    print("="*70)
    
    if plot:
        print("\n📊 Generating chart...")
        cerebro.plot(style='candlestick')
    
    return {
        'final_value': final_value,
        'pnl': pnl,
        'return_pct': return_pct,
        'sharpe_ratio': sharpe_ratio if sharpe_ratio else 0,
        'max_drawdown': max_drawdown,
        'total_trades': total_trades,
        'win_rate': win_rate if total_trades > 0 else 0
    }


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Backtest with Yahoo Finance')
    parser.add_argument('--symbol', default='SPY', help='Stock symbol')
    parser.add_argument('--days', type=int, default=180, help='Days of history')
    parser.add_argument('--daily', action='store_true', help='Use daily candles')
    parser.add_argument('--plot', action='store_true', help='Show chart')
    
    args = parser.parse_args()
    
    print("\n💡 Using Yahoo Finance - FREE!")
    
    result = run_backtest_yahoo(
        strategy_class=SMA200Strategy,
        symbol=args.symbol,
        days=args.days,
        use_daily=args.daily,  # FIXED!
        plot=args.plot
    )
