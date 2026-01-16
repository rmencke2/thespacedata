"""
Crypto Strategy Runner - OPTIMIZED VERSION
Uses crypto-specific strategy with existing infrastructure
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import crypto config
import config_crypto as config_module
sys.modules['utils.config'] = type(sys)('utils.config')
sys.modules['utils.config'].Config = config_module.Config

# Import crypto-specific data fetcher
import utils.data_fetcher_crypto as data_fetcher_crypto_module
sys.modules['utils.data_fetcher'] = data_fetcher_crypto_module

import schedule
import time
from datetime import datetime
from graph_orchestrator import TradingOrchestrator
from utils.database import TradingDatabase

class CryptoTradingRunner:
    """Runs 24/7 crypto trading with optimized strategy"""
    
    def __init__(self):
        self.config = config_module.Config
        self.orchestrator = TradingOrchestrator(portfolio_value=self.config.INITIAL_CAPITAL)
        self.db = TradingDatabase(self.config.DATABASE_PATH)
        self.running = True
        
        print("\n" + "="*70)
        print("🪙 CRYPTO TRADING SYSTEM (24/7) - OPTIMIZED")
        print("="*70)
        print("⚠️  This is PAPER TRADING ONLY - No real money at risk")
        print("💡 Using crypto-optimized mean reversion strategy")
        print("="*70 + "\n")
        
        self.config.print_config()
    
    def morning_routine(self):
        print("\n" + "="*70)
        print(f"🪙 CRYPTO - DAILY RESET - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        self.orchestrator.risk_manager.reset_daily_pnl()
        account = self.orchestrator.execution_agent.get_account_info()
        
        if account.get('status') == 'connected':
            print(f"💰 Account Equity: ${account['equity']:,.2f}")
            self.orchestrator.risk_manager.update_portfolio_value(account['equity'])
        
        print("✅ Daily reset complete\n")
    
    def trading_routine(self):
        print("\n" + "="*70)
        print(f"🪙 CRYPTO - TRADING SCAN - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        try:
            result = self.orchestrator.run_trading_cycle()
            print(f"✅ Trading scan complete")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def position_check(self):
        print(f"\n🔍 CRYPTO - Position check - {datetime.now().strftime('%H:%M:%S')}")
        try:
            result = self.orchestrator.manage_positions()
            if result.get('positions_closed', 0) > 0:
                print(f"✅ Closed {result['positions_closed']} positions")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def end_of_day_summary(self):
        print("\n" + "="*70)
        print(f"🪙 CRYPTO - DAILY SUMMARY - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        self.orchestrator.risk_manager.print_risk_summary()
        
        try:
            self.db.print_summary()
        except:
            print("No trades yet")
        
        print("💡 Crypto trading continues 24/7!")
        print("="*70 + "\n")
    
    def run_once(self):
        print("\n🧪 RUNNING SINGLE CYCLE (TEST MODE)\n")
        self.morning_routine()
        self.trading_routine()
        self.position_check()
        self.end_of_day_summary()
        print("✅ Test cycle complete!")
    
    def run_continuously(self):
        print("\n🚀 Starting CRYPTO continuous trading mode...")
        print("\n24/7 SCHEDULE:")
        print("  Daily Reset: 00:00 UTC")
        print("  Trading Scans: Every 4 hours")
        print("  Position Checks: Every 30 minutes")
        print("  Daily Summary: 23:55 UTC")
        print("\n💡 Crypto never sleeps - neither does this bot!")
        print("⏸️  Press Ctrl+C to stop\n")
        
        schedule.every().day.at("00:00").do(self.morning_routine)
        schedule.every().day.at("00:05").do(self.trading_routine)
        schedule.every().day.at("04:00").do(self.trading_routine)
        schedule.every().day.at("08:00").do(self.trading_routine)
        schedule.every().day.at("12:00").do(self.trading_routine)
        schedule.every().day.at("16:00").do(self.trading_routine)
        schedule.every().day.at("20:00").do(self.trading_routine)
        schedule.every(30).minutes.do(self.position_check)
        schedule.every().day.at("23:55").do(self.end_of_day_summary)
        
        print("Running initial cycle...\n")
        self.morning_routine()
        self.trading_routine()
        
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            print("\n\n⏹️  Stopping crypto trading...")
            self.end_of_day_summary()
            print("\n✅ Stopped safely.\n")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Crypto Trading System (24/7)')
    parser.add_argument('--mode', choices=['once', 'continuous'], default='once')
    args = parser.parse_args()
    
    runner = CryptoTradingRunner()
    
    if args.mode == 'once':
        runner.run_once()
    else:
        runner.run_continuously()

if __name__ == "__main__":
    main()
