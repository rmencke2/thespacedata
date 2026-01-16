"""
Performance Analyzer for Alpaca Crypto Paper Trading
Analyzes your live trading results vs backtest expectations
"""
import json
import os
from datetime import datetime
from glob import glob
import pandas as pd


class PerformanceAnalyzer:
    """Analyze paper trading performance"""
    
    def __init__(self):
        self.trades = []
        self.positions = {}
        
    def load_trade_logs(self):
        """Load all trade log files"""
        
        log_files = glob("alpaca_trades_*.json")
        
        if not log_files:
            print("❌ No trade logs found!")
            print("   Expected: alpaca_trades_YYYYMMDD.json")
            return False
        
        print(f"\n📁 Found {len(log_files)} trade log files")
        
        all_trades = []
        
        for log_file in sorted(log_files):
            try:
                with open(log_file, 'r') as f:
                    data = json.load(f)
                    
                    if 'trades' in data:
                        all_trades.extend(data['trades'])
                    
                    # Get latest positions
                    if 'positions' in data:
                        self.positions = data['positions']
                        
            except Exception as e:
                print(f"⚠️  Error reading {log_file}: {e}")
        
        self.trades = all_trades
        print(f"✅ Loaded {len(self.trades)} total trade actions")
        
        return True
    
    def analyze_trades(self):
        """Analyze completed trades"""
        
        print("\n" + "="*70)
        print("📊 TRADE ANALYSIS")
        print("="*70)
        
        if not self.trades:
            print("No trades yet - strategy is waiting for signals")
            return
        
        # Separate buys and sells
        buys = [t for t in self.trades if t['action'] == 'BUY']
        sells = [t for t in self.trades if t['action'] == 'SELL']
        
        print(f"\nTotal Actions: {len(self.trades)}")
        print(f"  Buy Orders: {len(buys)}")
        print(f"  Sell Orders: {len(sells)}")
        
        # Analyze completed trades
        if sells:
            print(f"\n{'='*70}")
            print("💰 COMPLETED TRADES")
            print(f"{'='*70}")
            
            total_pnl = 0
            wins = 0
            losses = 0
            
            for sell in sells:
                pnl = sell.get('pnl', 0)
                pnl_pct = sell.get('pnl_pct', 0)
                symbol = sell['symbol']
                timestamp = sell['timestamp']
                
                total_pnl += pnl
                
                if pnl > 0:
                    wins += 1
                    status = "✅ WIN"
                else:
                    losses += 1
                    status = "❌ LOSS"
                
                print(f"\n{status} - {symbol}")
                print(f"  Date: {timestamp}")
                print(f"  P&L: ${pnl:,.2f} ({pnl_pct:+.2f}%)")
                print(f"  Exit: ${sell['price']:.2f}")
            
            # Summary
            total_trades = wins + losses
            win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
            
            print(f"\n{'='*70}")
            print("📈 PERFORMANCE SUMMARY")
            print(f"{'='*70}")
            print(f"Completed Trades: {total_trades}")
            print(f"Wins: {wins}")
            print(f"Losses: {losses}")
            print(f"Win Rate: {win_rate:.1f}%")
            print(f"Total P&L: ${total_pnl:,.2f}")
            print(f"Average per Trade: ${total_pnl/total_trades:,.2f}")
            
            # Compare to backtest
            print(f"\n{'='*70}")
            print("📊 BACKTEST COMPARISON")
            print(f"{'='*70}")
            
            print("\n                    Backtest    Your Paper    Status")
            print("-" * 60)
            
            # ETH backtest targets
            bt_wr = 83.3
            bt_trades = 2  # 6 trades over 3 years = 2/year
            
            status_wr = "✅" if win_rate >= 60 else "⚠️" if win_rate >= 40 else "❌"
            
            print(f"Win Rate:           {bt_wr:.1f}%       {win_rate:.1f}%        {status_wr}")
            print(f"Trades (so far):    ~{bt_trades}          {total_trades}           -")
            
            # Days running
            if buys:
                first_trade = min(t['timestamp'] for t in buys)
                days = (datetime.now() - datetime.fromisoformat(first_trade)).days
                if days > 0:
                    expected_trades = (bt_trades / 365) * days
                    print(f"\nDays Running: {days}")
                    print(f"Expected Trades: {expected_trades:.1f}")
                    print(f"Actual Trades: {total_trades}")
            
        else:
            print("\nNo completed trades yet")
            
            if buys:
                print(f"\n⏳ OPEN POSITIONS: {len(buys)}")
                print("   (Not counted until sold)")
    
    def analyze_open_positions(self):
        """Analyze currently open positions"""
        
        if not self.positions:
            return
        
        print(f"\n{'='*70}")
        print("📊 OPEN POSITIONS")
        print(f"{'='*70}")
        
        for symbol, pos in self.positions.items():
            entry_price = pos['entry_price']
            quantity = pos['quantity']
            entry_time = pos['entry_time']
            
            # Calculate days held
            entry_dt = datetime.fromisoformat(entry_time)
            days_held = (datetime.now() - entry_dt).days
            
            # Estimate current value (would need live price)
            print(f"\n{symbol}:")
            print(f"  Entry Price: ${entry_price:,.2f}")
            print(f"  Quantity: {quantity:.6f}")
            print(f"  Entry Value: ${entry_price * quantity:,.2f}")
            print(f"  Days Held: {days_held}")
            print(f"  Entry Date: {entry_time}")
    
    def calculate_fee_impact(self):
        """Calculate how fees impact returns"""
        
        print(f"\n{'='*70}")
        print("💸 FEE IMPACT ANALYSIS")
        print(f"{'='*70}")
        
        sells = [t for t in self.trades if t['action'] == 'SELL']
        
        if not sells:
            print("\nNo completed trades yet to analyze fees")
            return
        
        print("\nAlpaca Commission: 0.1% per trade")
        print("Round-trip cost: 0.2% (buy + sell)")
        
        total_gross_pnl = 0
        total_fees = 0
        
        for sell in sells:
            pnl = sell.get('pnl', 0)
            
            # Estimate fees (0.1% of trade value each way)
            trade_value = sell['price'] * sell['quantity']
            estimated_fees = trade_value * 0.001 * 2  # Buy + sell
            
            total_gross_pnl += pnl + estimated_fees  # Gross before fees
            total_fees += estimated_fees
        
        net_pnl = total_gross_pnl - total_fees
        fee_percentage = (total_fees / abs(total_gross_pnl) * 100) if total_gross_pnl != 0 else 0
        
        print(f"\nGross P&L (before fees): ${total_gross_pnl:,.2f}")
        print(f"Estimated Fees: ${total_fees:,.2f}")
        print(f"Net P&L (after fees): ${net_pnl:,.2f}")
        print(f"\nFees ate {fee_percentage:.1f}% of gross profit")
        
        # Break-even analysis
        print(f"\n{'='*70}")
        print("📊 BREAK-EVEN ANALYSIS")
        print(f"{'='*70}")
        
        print("\nTo break even after 0.2% round-trip fees:")
        print("  $1,000 trade needs: +$2.00 (+0.2%)")
        print("  $10,000 trade needs: +$20.00 (+0.2%)")
        print("  $45,000 trade needs: +$90.00 (+0.2%)")
        
        print("\nYour current targets:")
        print("  Stop Loss: -8.0% (loses $3,600 on $45k)")
        print("  Take Profit: +20.0% (gains $9,000 on $45k)")
        print("  Fees: -0.2% (loses $90 on $45k)")
        
        print("\nNet after fees:")
        print("  Loss: -8.2% ($3,690)")
        print("  Win: +19.8% ($8,910)")
        
        # Recommendations
        print(f"\n{'='*70}")
        print("💡 OPTIMIZATION SUGGESTIONS")
        print(f"{'='*70}")
        
        avg_win = 19.8  # After fees
        avg_loss = 8.2  # After fees
        current_wr = 83.3  # Backtest win rate
        
        expected_value = (avg_win * current_wr/100) - (avg_loss * (100-current_wr)/100)
        
        print(f"\nExpected Value per trade: +{expected_value:.2f}%")
        
        if fee_percentage > 5:
            print("\n⚠️  Fees are eating >5% of profits!")
            print("   Consider: Larger positions, fewer trades")
        elif fee_percentage > 10:
            print("\n🚨 Fees are eating >10% of profits!")
            print("   CRITICAL: Position size too small")
        else:
            print(f"\n✅ Fees are manageable ({fee_percentage:.1f}%)")
    
    def recommend_optimizations(self):
        """Recommend strategy optimizations"""
        
        print(f"\n{'='*70}")
        print("🎯 OPTIMIZATION RECOMMENDATIONS")
        print(f"{'='*70}")
        
        sells = [t for t in self.trades if t['action'] == 'SELL']
        
        if len(sells) < 3:
            print("\n⏳ Need at least 3 completed trades for reliable analysis")
            print("   Keep paper trading!")
            return
        
        # Analyze win/loss patterns
        wins = [s for s in sells if s.get('pnl', 0) > 0]
        losses = [s for s in sells if s.get('pnl', 0) <= 0]
        
        if wins:
            avg_win = sum(s['pnl_pct'] for s in wins) / len(wins)
            print(f"\n✅ Average Win: +{avg_win:.2f}%")
            
            if avg_win < 15:
                print("   → Consider: Wider profit targets (25% instead of 20%)")
        
        if losses:
            avg_loss = abs(sum(s['pnl_pct'] for s in losses) / len(losses))
            print(f"\n❌ Average Loss: -{avg_loss:.2f}%")
            
            if avg_loss > 10:
                print("   → Consider: Tighter stops (5% instead of 8%)")
        
        # Position sizing
        buys = [t for t in self.trades if t['action'] == 'BUY']
        if buys:
            avg_position = sum(t['value'] for t in buys) / len(buys)
            print(f"\n💰 Average Position Size: ${avg_position:,.0f}")
            
            if avg_position < 10000:
                print("   ⚠️  Position too small - fees eat profits!")
                print("   → Consider: Increase to 50-60% of capital")
            elif avg_position > 75000:
                print("   ⚠️  Position very large - high risk!")
                print("   → Consider: Reduce to 40-50% of capital")
    
    def run_full_analysis(self):
        """Run complete analysis"""
        
        print("\n" + "="*70)
        print("📊 ALPACA CRYPTO PAPER TRADING ANALYSIS")
        print("="*70)
        print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Load data
        if not self.load_trade_logs():
            return
        
        # Run analyses
        self.analyze_trades()
        self.analyze_open_positions()
        self.calculate_fee_impact()
        self.recommend_optimizations()
        
        print("\n" + "="*70)
        print("✅ ANALYSIS COMPLETE")
        print("="*70)
        print("\nNext steps:")
        print("1. Review the numbers above")
        print("2. Compare to backtest targets")
        print("3. Implement optimizations if needed")
        print("4. Continue paper trading\n")


if __name__ == '__main__':
    analyzer = PerformanceAnalyzer()
    analyzer.run_full_analysis()
