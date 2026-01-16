"""
Performance Dashboard
View your trading performance with simple visualizations
"""
from utils.database import TradingDatabase
import pandas as pd
from datetime import datetime, timedelta

class PerformanceDashboard:
    """Simple performance dashboard"""
    
    def __init__(self):
        self.db = TradingDatabase()
    
    def print_dashboard(self, days: int = 30):
        """Print a comprehensive dashboard"""
        print("\n" + "="*80)
        print("📊 TRADING PERFORMANCE DASHBOARD")
        print("="*80)
        print(f"Period: Last {days} days")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # Get summary
        summary = self.db.get_performance_summary(days)
        
        # Overall metrics
        print("\n📈 OVERALL PERFORMANCE")
        print("-"*80)
        print(f"Total Trades: {summary['total_trades']}")
        print(f"Winning Trades: {summary['winning_trades']} ({summary['win_rate']:.1f}%)")
        print(f"Losing Trades: {summary['losing_trades']}")
        print(f"\nTotal P&L: ${summary['total_pnl']:.2f}")
        print(f"Average P&L per Trade: {summary['avg_pnl_percent']:.2f}%")
        print(f"Average Win: ${summary['avg_win']:.2f}")
        print(f"Average Loss: ${summary['avg_loss']:.2f}")
        
        if summary['avg_loss'] != 0:
            profit_factor = abs(summary['avg_win'] / summary['avg_loss'])
            print(f"Profit Factor: {profit_factor:.2f}")
        
        print(f"\nBest Trade: ${summary['best_trade']:.2f}")
        print(f"Worst Trade: ${summary['worst_trade']:.2f}")
        
        # Open positions
        positions = self.db.get_open_positions()
        print("\n💼 OPEN POSITIONS")
        print("-"*80)
        
        if positions:
            print(f"Currently holding {len(positions)} positions:\n")
            for pos in positions:
                pnl_str = f"${pos['unrealized_pnl']:+.2f}" if 'unrealized_pnl' in pos else "N/A"
                print(f"  {pos['symbol']:6} | {pos['quantity']:>6.0f} shares | "
                      f"Entry: ${pos['entry_price']:.2f} | "
                      f"Current: ${pos['current_price']:.2f} | "
                      f"P&L: {pnl_str}")
        else:
            print("No open positions")
        
        # Recent trades
        print("\n📋 RECENT TRADES")
        print("-"*80)
        
        conn = self.db.db_path
        import sqlite3
        conn = sqlite3.connect(self.db.db_path)
        recent_trades = pd.read_sql_query(
            '''SELECT symbol, side, quantity, entry_price, exit_price, 
               pnl, pnl_percent, timestamp, strategy 
               FROM trades 
               WHERE status = "closed" 
               ORDER BY timestamp DESC 
               LIMIT 10''',
            conn
        )
        conn.close()
        
        if not recent_trades.empty:
            print("\nLast 10 closed trades:\n")
            for _, trade in recent_trades.iterrows():
                pnl_str = f"${trade['pnl']:+.2f} ({trade['pnl_percent']:+.2f}%)"
                emoji = "✅" if trade['pnl'] > 0 else "❌"
                print(f"  {emoji} {trade['symbol']:6} | {trade['side']:4} | "
                      f"${trade['entry_price']:.2f} → ${trade['exit_price']:.2f} | "
                      f"{pnl_str} | {trade['strategy']}")
        else:
            print("No closed trades yet")
        
        # Strategy breakdown
        print("\n📊 STRATEGY BREAKDOWN")
        print("-"*80)
        
        conn = sqlite3.connect(self.db.db_path)
        strategy_stats = pd.read_sql_query(
            '''SELECT strategy, 
               COUNT(*) as trades,
               SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
               SUM(pnl) as total_pnl,
               AVG(pnl_percent) as avg_pnl_pct
               FROM trades 
               WHERE status = "closed"
               GROUP BY strategy''',
            conn
        )
        conn.close()
        
        if not strategy_stats.empty:
            for _, row in strategy_stats.iterrows():
                win_rate = (row['wins'] / row['trades'] * 100) if row['trades'] > 0 else 0
                print(f"\n{row['strategy'].upper()}:")
                print(f"  Trades: {int(row['trades'])} | "
                      f"Win Rate: {win_rate:.1f}% | "
                      f"Total P&L: ${row['total_pnl']:.2f} | "
                      f"Avg: {row['avg_pnl_pct']:.2f}%")
        else:
            print("No strategy data available yet")
        
        # Performance by symbol
        print("\n🎯 PERFORMANCE BY SYMBOL")
        print("-"*80)
        
        conn = sqlite3.connect(self.db.db_path)
        symbol_stats = pd.read_sql_query(
            '''SELECT symbol,
               COUNT(*) as trades,
               SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
               SUM(pnl) as total_pnl,
               AVG(pnl_percent) as avg_pnl_pct
               FROM trades
               WHERE status = "closed"
               GROUP BY symbol
               ORDER BY total_pnl DESC''',
            conn
        )
        conn.close()
        
        if not symbol_stats.empty:
            for _, row in symbol_stats.iterrows():
                win_rate = (row['wins'] / row['trades'] * 100) if row['trades'] > 0 else 0
                emoji = "🟢" if row['total_pnl'] > 0 else "🔴"
                print(f"{emoji} {row['symbol']:6} | "
                      f"Trades: {int(row['trades']):3} | "
                      f"Win Rate: {win_rate:5.1f}% | "
                      f"P&L: ${row['total_pnl']:+7.2f} | "
                      f"Avg: {row['avg_pnl_pct']:+5.2f}%")
        else:
            print("No symbol data available yet")
        
        print("\n" + "="*80)
        
        # Tips
        if summary['total_trades'] > 0:
            print("\n💡 INSIGHTS:")
            if summary['win_rate'] > 60:
                print("  ✅ Excellent win rate! Keep up the good work.")
            elif summary['win_rate'] > 50:
                print("  ✅ Profitable win rate. Consider optimizing further.")
            else:
                print("  ⚠️  Win rate below 50%. Review your strategies.")
            
            if summary['total_pnl'] > 0:
                print("  ✅ Overall profitable trading!")
            else:
                print("  ⚠️  Net loss. Consider adjusting risk parameters.")
            
            if summary['avg_loss'] != 0:
                profit_factor = abs(summary['avg_win'] / summary['avg_loss'])
                if profit_factor > 2:
                    print("  ✅ Excellent profit factor (>2). Wins are much larger than losses.")
                elif profit_factor > 1.5:
                    print("  ✅ Good profit factor (>1.5).")
                else:
                    print("  ⚠️  Low profit factor. Your wins aren't much larger than losses.")
        
        print("="*80 + "\n")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Trading Performance Dashboard')
    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='Number of days to analyze (default: 30)'
    )
    
    args = parser.parse_args()
    
    dashboard = PerformanceDashboard()
    dashboard.print_dashboard(days=args.days)

if __name__ == "__main__":
    main()
