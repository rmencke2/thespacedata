"""
Strategy Comparison Dashboard
Compare Aggressive vs Conservative vs Crypto performance
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sqlite3
import pandas as pd
from datetime import datetime

def get_strategy_stats(db_path, initial_capital=30000):
    """Get statistics from a strategy database"""
    try:
        conn = sqlite3.connect(db_path)
        
        trades_df = pd.read_sql_query(
            'SELECT * FROM trades WHERE status = "closed"',
            conn
        )
        
        positions_df = pd.read_sql_query('SELECT * FROM positions', conn)
        
        conn.close()
        
        if trades_df.empty:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'best_trade': 0,
                'worst_trade': 0,
                'open_positions': len(positions_df),
                'total_exposure': 0,
                'return_pct': 0
            }
        
        winning = trades_df[trades_df['pnl'] > 0]
        losing = trades_df[trades_df['pnl'] <= 0]
        
        total_exposure = sum(
            abs(pos['quantity'] * pos['current_price']) 
            for _, pos in positions_df.iterrows()
        ) if not positions_df.empty else 0
        
        return {
            'total_trades': len(trades_df),
            'winning_trades': len(winning),
            'losing_trades': len(losing),
            'win_rate': (len(winning) / len(trades_df) * 100) if len(trades_df) > 0 else 0,
            'total_pnl': trades_df['pnl'].sum(),
            'avg_win': winning['pnl'].mean() if len(winning) > 0 else 0,
            'avg_loss': losing['pnl'].mean() if len(losing) > 0 else 0,
            'best_trade': trades_df['pnl'].max(),
            'worst_trade': trades_df['pnl'].min(),
            'open_positions': len(positions_df),
            'total_exposure': total_exposure,
            'return_pct': (trades_df['pnl'].sum() / initial_capital) * 100
        }
    except Exception as e:
        print(f"Error reading {db_path}: {e}")
        return None

def print_comparison():
    """Print side-by-side comparison of all 3 strategies"""
    
    agg_stats = get_strategy_stats('trades_aggressive.db', 30000)
    con_stats = get_strategy_stats('trades_conservative.db', 30000)
    cry_stats = get_strategy_stats('trades_crypto.db', 20000)
    
    print("\n" + "="*120)
    print("📊 TRIPLE STRATEGY COMPARISON DASHBOARD")
    print("="*120)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Allocation: Aggressive $30K | Conservative $30K | Crypto $20K | Total: $80K")
    print("="*120)
    
    print(f"\n{'METRIC':<25} {'🔥 AGGRESSIVE':<30} {'🛡️  CONSERVATIVE':<30} {'🪙 CRYPTO (24/7)':<30}")
    print("-"*120)
    
    if agg_stats and con_stats and cry_stats:
        print(f"{'Total Trades':<25} {agg_stats['total_trades']:<30} {con_stats['total_trades']:<30} {cry_stats['total_trades']:<30}")
        print(f"{'Win Rate':<25} {agg_stats['win_rate']:<29.1f}% {con_stats['win_rate']:<29.1f}% {cry_stats['win_rate']:<29.1f}%")
        
        agg_pnl_str = f"${agg_stats['total_pnl']:,.2f}"
        con_pnl_str = f"${con_stats['total_pnl']:,.2f}"
        cry_pnl_str = f"${cry_stats['total_pnl']:,.2f}"
        print(f"{'Total P&L':<25} {agg_pnl_str:<30} {con_pnl_str:<30} {cry_pnl_str:<30}")
        
        print(f"{'Return %':<25} {agg_stats['return_pct']:<29.2f}% {con_stats['return_pct']:<29.2f}% {cry_stats['return_pct']:<29.2f}%")
        
        agg_win_str = f"${agg_stats['avg_win']:,.2f}"
        con_win_str = f"${con_stats['avg_win']:,.2f}"
        cry_win_str = f"${cry_stats['avg_win']:,.2f}"
        print(f"{'Average Win':<25} {agg_win_str:<30} {con_win_str:<30} {cry_win_str:<30}")
        
        agg_loss_str = f"${agg_stats['avg_loss']:,.2f}"
        con_loss_str = f"${con_stats['avg_loss']:,.2f}"
        cry_loss_str = f"${cry_stats['avg_loss']:,.2f}"
        print(f"{'Average Loss':<25} {agg_loss_str:<30} {con_loss_str:<30} {cry_loss_str:<30}")
        
        agg_best_str = f"${agg_stats['best_trade']:,.2f}"
        con_best_str = f"${con_stats['best_trade']:,.2f}"
        cry_best_str = f"${cry_stats['best_trade']:,.2f}"
        print(f"{'Best Trade':<25} {agg_best_str:<30} {con_best_str:<30} {cry_best_str:<30}")
        
        agg_worst_str = f"${agg_stats['worst_trade']:,.2f}"
        con_worst_str = f"${con_stats['worst_trade']:,.2f}"
        cry_worst_str = f"${cry_stats['worst_trade']:,.2f}"
        print(f"{'Worst Trade':<25} {agg_worst_str:<30} {con_worst_str:<30} {cry_worst_str:<30}")
        
        print(f"{'Open Positions':<25} {agg_stats['open_positions']:<30} {con_stats['open_positions']:<30} {cry_stats['open_positions']:<30}")
        
        print("-"*120)
        
        total_pnl = agg_stats['total_pnl'] + con_stats['total_pnl'] + cry_stats['total_pnl']
        total_return_pct = (total_pnl / 80000) * 100
        
        print(f"\n💼 COMBINED PORTFOLIO:")
        print(f"   Total P&L: ${total_pnl:,.2f}")
        print(f"   Total Return: {total_return_pct:.2f}%")
        print(f"   Starting Capital: $80,000")
        print(f"   Current Value: ${80000 + total_pnl:,.2f}")
        
        print("\n🏆 INDIVIDUAL PERFORMANCE:")
        stats_list = [
            ('🔥 Aggressive', agg_stats),
            ('🛡️  Conservative', con_stats),
            ('🪙 Crypto', cry_stats)
        ]
        stats_list.sort(key=lambda x: x[1]['total_pnl'], reverse=True)
        
        for i, (name, stats) in enumerate(stats_list, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
            print(f"   {medal} {name}: ${stats['total_pnl']:,.2f} ({stats['return_pct']:.2f}%)")
        
        print(f"\n📈 TRADING ACTIVITY:")
        print(f"   Aggressive: {agg_stats['total_trades']} trades ({agg_stats['winning_trades']}W-{agg_stats['losing_trades']}L)")
        print(f"   Conservative: {con_stats['total_trades']} trades ({con_stats['winning_trades']}W-{con_stats['losing_trades']}L)")
        print(f"   Crypto: {cry_stats['total_trades']} trades ({cry_stats['winning_trades']}W-{cry_stats['losing_trades']}L)")
        print(f"   TOTAL: {agg_stats['total_trades'] + con_stats['total_trades'] + cry_stats['total_trades']} trades")
        
        print(f"\n⚖️  PROFIT FACTORS:")
        if agg_stats['avg_loss'] != 0:
            agg_pf = abs(agg_stats['avg_win'] / agg_stats['avg_loss'])
            print(f"   Aggressive: {agg_pf:.2f}")
        if con_stats['avg_loss'] != 0:
            con_pf = abs(con_stats['avg_win'] / con_stats['avg_loss'])
            print(f"   Conservative: {con_pf:.2f}")
        if cry_stats['avg_loss'] != 0:
            cry_pf = abs(cry_stats['avg_win'] / cry_stats['avg_loss'])
            print(f"   Crypto: {cry_pf:.2f}")
    
    else:
        print("⚠️  Unable to load strategy data. Make sure all strategies have run.")
    
    print("\n" + "="*120)
    print("\n💡 COMMANDS:")
    print("   Start all: ./start_all.sh")
    print("   Stop all: ./stop_all.sh")
    print("   Individual: python run_aggressive.py | run_conservative.py | run_crypto.py")
    print("="*120 + "\n")

if __name__ == "__main__":
    print_comparison()
