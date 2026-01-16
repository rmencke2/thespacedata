"""
Conservative Strategy Runner
Runs the conservative trading configuration
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import conservative config
import config_conservative as config_module
sys.modules['utils.config'] = type(sys)('utils.config')
sys.modules['utils.config'].Config = config_module.Config

import schedule
import time
from datetime import datetime
from graph_orchestrator import TradingOrchestrator
from utils.database import TradingDatabase

class ConservativeTradingRunner:
    """Runs conservative trading strategy"""
    
    def __init__(self):
        # Use conservative config
        self.config = config_module.Config
        self.orchestrator = TradingOrchestrator(portfolio_value=self.config.INITIAL_CAPITAL)
        self.db = TradingDatabase(self.config.DATABASE_PATH)
        self.running = True
        
        print("\n" + "="*70)
        print("🛡️  CONSERVATIVE TRADING SYSTEM")
        print("="*70)
        print("⚠️  This is PAPER TRADING ONLY - No real money at risk")
        print("="*70 + "\n")
        
        self.config.print_config()
    
    def morning_routine(self):
        print("\n" + "="*70)
        print(f"🌅 CONSERVATIVE - MORNING - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        self.orchestrator.risk_manager.reset_daily_pnl()
        account = self.orchestrator.execution_agent.get_account_info()
        
        if account.get('status') == 'connected':
            print(f"💰 Account Equity: ${account['equity']:,.2f}")
            self.orchestrator.risk_manager.update_portfolio_value(account['equity'])
        
        print("✅ Morning routine complete\n")
    
    def trading_routine(self):
        print("\n" + "="*70)
        print(f"📈 CONSERVATIVE - TRADING - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        try:
            result = self.orchestrator.run_trading_cycle()
            self.orchestrator.manage_positions()
            print(f"✅ Trading routine complete")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def position_check(self):
        print(f"\n🔍 CONSERVATIVE - Position check - {datetime.now().strftime('%H:%M:%S')}")
        try:
            result = self.orchestrator.manage_positions()
            if result['positions_closed'] > 0:
                print(f"✅ Closed {result['positions_closed']} positions")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def end_of_day_routine(self):
        print("\n" + "="*70)
        print(f"🌙 CONSERVATIVE - END OF DAY - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        self.orchestrator.risk_manager.print_risk_summary()
        
        try:
            self.db.print_summary()
        except:
            print("No trades yet")
        
        self.orchestrator.execution_agent.cancel_all_orders()
        print("✅ End of day complete\n")
    
    def run_once(self):
        print("\n🧪 RUNNING SINGLE CYCLE (TEST MODE)\n")
        self.morning_routine()
        self.trading_routine()
        self.position_check()
        self.end_of_day_routine()
        print("✅ Test cycle complete!")
    
    def run_continuously(self):
        print("\n🚀 Starting CONSERVATIVE continuous trading mode...")
        print("\nSchedule:")
        print(f"  Morning: {self.config.MARKET_OPEN} ET")
        print(f"  Trading: {self.config.TRADING_SCHEDULE} ET")
        print(f"  Position checks: Every 30 minutes")
        print(f"  End of day: {self.config.MARKET_CLOSE} ET")
        print("\n⏸️  Press Ctrl+C to stop\n")
        
        schedule.every().day.at(self.config.MARKET_OPEN).do(self.morning_routine)
        schedule.every().day.at(self.config.TRADING_SCHEDULE).do(self.trading_routine)
        schedule.every(30).minutes.do(self.position_check)
        schedule.every().day.at(self.config.MARKET_CLOSE).do(self.end_of_day_routine)
        
        print("Running initial cycle...\n")
        self.morning_routine()
        self.trading_routine()
        
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            print("\n\n⏹️  Stopping conservative trading...")
            self.end_of_day_routine()
            print("\n✅ Stopped safely.\n")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Conservative Trading System')
    parser.add_argument('--mode', choices=['once', 'continuous'], default='once')
    args = parser.parse_args()
    
    runner = ConservativeTradingRunner()
    
    if args.mode == 'once':
        runner.run_once()
    else:
        runner.run_continuously()

if __name__ == "__main__":
    main()
