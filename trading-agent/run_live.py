"""
Live Trading Runner
Run the trading system in paper trading mode
"""
import schedule
import time
from datetime import datetime
from graph_orchestrator import TradingOrchestrator
from utils.config import Config
from utils.database import TradingDatabase
import sys

class LiveTradingRunner:
    """
    Runs the trading system on a schedule:
    - Opens positions based on signals
    - Manages existing positions
    - Monitors risk
    """
    
    def __init__(self, portfolio_value: float = 10000):
        self.orchestrator = TradingOrchestrator(portfolio_value)
        self.db = TradingDatabase()
        self.running = True
        
        print("\n" + "="*70)
        print("LIVE PAPER TRADING SYSTEM")
        print("="*70)
        print("⚠️  This is PAPER TRADING ONLY - No real money at risk")
        print("="*70 + "\n")
        
        # Validate configuration
        if not Config.validate():
            print("\n❌ Configuration invalid. Please set up your .env file.")
            print("See README.md for instructions.\n")
            sys.exit(1)
        
        Config.print_config()
    
    def morning_routine(self):
        """Run at market open"""
        print("\n" + "="*70)
        print(f"🌅 MORNING ROUTINE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        # Reset daily P&L
        self.orchestrator.risk_manager.reset_daily_pnl()
        
        # Get account info
        account = self.orchestrator.execution_agent.get_account_info()
        print(f"\n💰 Account Status: {account['status']}")
        print(f"   Equity: ${account['equity']:,.2f}")
        
        # Update portfolio value
        self.orchestrator.risk_manager.update_portfolio_value(account['equity'])
        
        print("\n✅ Morning routine complete\n")
    
    def trading_routine(self):
        """Run trading analysis and execution"""
        print("\n" + "="*70)
        print(f"📈 TRADING ROUTINE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        try:
            # Run the trading cycle
            result = self.orchestrator.run_trading_cycle()
            
            # Manage existing positions
            self.orchestrator.manage_positions()
            
            print(f"\n✅ Trading routine complete")
            
        except Exception as e:
            print(f"\n❌ Error in trading routine: {e}")
            import traceback
            traceback.print_exc()
    
    def position_check(self):
        """Check and manage positions throughout the day"""
        print(f"\n🔍 Position check - {datetime.now().strftime('%H:%M:%S')}")
        
        try:
            # Manage positions (check stops, exit signals)
            result = self.orchestrator.manage_positions()
            
            if result['positions_closed'] > 0:
                print(f"✅ Closed {result['positions_closed']} positions")
            
        except Exception as e:
            print(f"❌ Error checking positions: {e}")
    
    def end_of_day_routine(self):
        """Run at market close"""
        print("\n" + "="*70)
        print(f"🌙 END OF DAY ROUTINE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        # Print performance summary
        self.orchestrator.risk_manager.print_risk_summary()
        self.db.print_summary()
        
        # Cancel any open orders
        self.orchestrator.execution_agent.cancel_all_orders()
        
        print("\n✅ End of day routine complete\n")
    
    def run_once(self):
        """Run a single trading cycle (for testing)"""
        print("\n🧪 RUNNING SINGLE CYCLE (TEST MODE)\n")
        
        self.morning_routine()
        self.trading_routine()
        self.position_check()
        self.end_of_day_routine()
        
        print("\n✅ Test cycle complete!")
    
    def run_continuously(self):
        """Run the trading system on a schedule"""
        print("\n🚀 Starting continuous trading mode...")
        print("\nSchedule:")
        print(f"  Morning routine: {Config.MARKET_OPEN} ET")
        print(f"  Trading routine: {Config.TRADING_SCHEDULE} ET")
        print(f"  Position checks: Every 30 minutes")
        print(f"  End of day: {Config.MARKET_CLOSE} ET")
        print("\n⏸️  Press Ctrl+C to stop\n")
        
        # Schedule jobs
        schedule.every().day.at(Config.MARKET_OPEN).do(self.morning_routine)
        schedule.every().day.at(Config.TRADING_SCHEDULE).do(self.trading_routine)
        schedule.every(30).minutes.do(self.position_check)
        schedule.every().day.at(Config.MARKET_CLOSE).do(self.end_of_day_routine)
        
        # Run immediately on start
        print("Running initial cycle...\n")
        self.morning_routine()
        self.trading_routine()
        
        # Main loop
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            print("\n\n⏹️  Stopping trading system...")
            self.end_of_day_routine()
            print("\n✅ Trading system stopped safely.\n")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Live Paper Trading System')
    parser.add_argument(
        '--mode',
        choices=['once', 'continuous'],
        default='once',
        help='Run mode: once for single cycle, continuous for scheduled trading'
    )
    parser.add_argument(
        '--portfolio',
        type=float,
        default=10000,
        help='Starting portfolio value (default: 10000)'
    )
    
    args = parser.parse_args()
    
    # Create runner
    runner = LiveTradingRunner(portfolio_value=args.portfolio)
    
    # Run
    if args.mode == 'once':
        runner.run_once()
    else:
        runner.run_continuously()

if __name__ == "__main__":
    main()
