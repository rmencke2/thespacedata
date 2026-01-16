"""
Moderate Activity Momentum Strategy
Trades 1-2 times per month (12-24 trades/year)

Changes from conservative:
- Shorter breakout period (10 days vs 20)
- Lower volume requirement (1.5x vs 2x)
- Wider RSI range (50-80 vs 60-80)
- Smaller profit target (15% vs 20%) for faster exits
"""
import os
import time
import json
from datetime import datetime, timedelta
import pandas as pd
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame

class ModerateActivityTrader:
    """
    More active version - trades 12-24 times per year
    Still maintains good risk/reward
    """
    
    def __init__(self, api_key=None, secret_key=None, paper=True):
        # Get credentials
        self.api_key = api_key or os.getenv('ALPACA_API_KEY')
        self.secret_key = secret_key or os.getenv('ALPACA_SECRET_KEY')
        
        if not self.api_key or not self.secret_key:
            raise ValueError("Alpaca API credentials required!")
        
        # Initialize clients
        self.trading_client = TradingClient(
            api_key=self.api_key,
            secret_key=self.secret_key,
            paper=paper
        )
        
        self.data_client = CryptoHistoricalDataClient()
        
        # MODERATE PARAMETERS (more active)
        self.symbols = ['BTC/USD', 'ETH/USD']
        self.breakout_period = 10  # 10 days (vs 20) = 2x more signals
        self.volume_period = 20
        self.volume_multiplier = 1.5  # 1.5x (vs 2x) = easier to trigger
        self.rsi_period = 14
        self.rsi_min = 50  # 50 (vs 60) = wider range
        self.rsi_max = 80
        self.momentum_period = 3
        
        # Risk management (adjusted for more frequent trading)
        self.stop_loss_pct = 0.06  # 6% (vs 8%) = tighter stops
        self.take_profit_pct = 0.15  # 15% (vs 20%) = faster exits
        self.position_size_pct = 0.50  # 50% per position
        
        # Tracking
        self.positions = {}
        self.trade_log = []
        
        print("🚀 Moderate Activity Crypto Trader Initialized")
        print(f"   Mode: {'PAPER' if paper else 'LIVE'}")
        print(f"   Symbols: {', '.join(self.symbols)}")
        print(f"   Target: 12-24 trades/year (1-2 per month)")
        print(f"   Strategy: Moderate momentum breakout")
    
    def get_account_info(self):
        """Get account status"""
        account = self.trading_client.get_account()
        
        print(f"\n💰 Account Status:")
        print(f"   Cash: ${float(account.cash):,.2f}")
        print(f"   Portfolio: ${float(account.portfolio_value):,.2f}")
        print(f"   Buying Power: ${float(account.buying_power):,.2f}")
        
        return account
    
    def get_historical_data(self, symbol, days=30):
        """Get historical data"""
        try:
            request_params = CryptoBarsRequest(
                symbol_or_symbols=[symbol],
                timeframe=TimeFrame.Day,
                start=datetime.now() - timedelta(days=days)
            )
            
            bars = self.data_client.get_crypto_bars(request_params)
            df = bars.df
            
            if df.empty:
                print(f"⚠️  No data for {symbol}")
                return None
            
            df = df.reset_index()
            df = df[df['symbol'] == symbol]
            
            return df
            
        except Exception as e:
            print(f"❌ Error getting data for {symbol}: {e}")
            return None
    
    def calculate_indicators(self, df):
        """Calculate indicators"""
        if df is None or len(df) < self.breakout_period + 1:
            return None
        
        # 10-day high (more frequent breakouts)
        df['highest_10'] = df['high'].rolling(window=self.breakout_period).max()
        
        # Volume
        df['volume_sma'] = df['volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_sma']
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Momentum
        df['momentum'] = df['close'].diff(self.momentum_period)
        
        return df
    
    def check_buy_signal(self, symbol):
        """Check for buy signal - more lenient rules"""
        df = self.get_historical_data(symbol, days=30)
        
        if df is None:
            return False, "No data"
        
        df = self.calculate_indicators(df)
        
        if df is None:
            return False, "Not enough data"
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        close = latest['close']
        highest_10 = prev['highest_10']
        volume_ratio = latest['volume_ratio']
        rsi = latest['rsi']
        momentum = latest['momentum']
        
        print(f"\n📊 {symbol} Analysis:")
        print(f"   Price: ${close:.2f}")
        print(f"   10-day High: ${highest_10:.2f}")
        print(f"   Volume: {volume_ratio:.2f}x avg")
        print(f"   RSI: {rsi:.1f}")
        print(f"   Momentum: {momentum:.2f}")
        
        # Check 1: Breakout above 10-day high
        if close <= highest_10:
            return False, f"No breakout (${close:.2f} <= ${highest_10:.2f})"
        
        # Check 2: Volume at least 1.5x
        if volume_ratio < self.volume_multiplier:
            return False, f"Low volume ({volume_ratio:.2f}x < {self.volume_multiplier}x)"
        
        # Check 3: RSI 50-80 (wider range)
        if not (self.rsi_min <= rsi <= self.rsi_max):
            return False, f"RSI out of range ({rsi:.1f})"
        
        # Check 4: Momentum positive
        if momentum <= 0:
            return False, f"Negative momentum ({momentum:.2f})"
        
        return True, "🚀 BUY SIGNAL - Moderate breakout detected!"
    
    def check_sell_signal(self, symbol, position):
        """Check for sell signal"""
        df = self.get_historical_data(symbol, days=5)
        
        if df is None:
            return False, "No data"
        
        df = self.calculate_indicators(df)
        
        if df is None:
            return False, "Not enough data"
        
        latest = df.iloc[-1]
        current_price = latest['close']
        entry_price = position['entry_price']
        rsi = latest['rsi']
        volume_ratio = latest['volume_ratio']
        
        pnl_pct = (current_price - entry_price) / entry_price
        
        print(f"\n📊 {symbol} Position Check:")
        print(f"   Entry: ${entry_price:.2f}")
        print(f"   Current: ${current_price:.2f}")
        print(f"   P&L: {pnl_pct*100:+.2f}%")
        
        # Exit 1: Stop loss (6%)
        if pnl_pct <= -self.stop_loss_pct:
            return True, f"🛑 STOP LOSS ({pnl_pct*100:.2f}%)"
        
        # Exit 2: Take profit (15%)
        if pnl_pct >= self.take_profit_pct:
            return True, f"💎 TAKE PROFIT ({pnl_pct*100:.2f}%)"
        
        # Exit 3: RSI extreme
        if rsi > 85:
            return True, f"📈 RSI EXTREME ({rsi:.1f})"
        
        # Exit 4: Volume dying
        if volume_ratio < 0.5:
            return True, f"📉 VOLUME DYING ({volume_ratio:.2f}x)"
        
        return False, "Hold"
    
    def execute_buy(self, symbol):
        """Execute buy order"""
        try:
            account = self.trading_client.get_account()
            buying_power = float(account.buying_power)
            position_value = buying_power * self.position_size_pct
            
            print(f"\n💰 Executing BUY for {symbol}")
            print(f"   Position Size: ${position_value:,.2f}")
            
            order_data = MarketOrderRequest(
                symbol=symbol,
                notional=position_value,
                side=OrderSide.BUY,
                time_in_force=TimeInForce.GTC
            )
            
            order = self.trading_client.submit_order(order_data)
            print(f"   ✅ Order submitted: {order.id}")
            
            time.sleep(2)
            
            filled_order = self.trading_client.get_order_by_id(order.id)
            
            if filled_order.filled_at:
                fill_price = float(filled_order.filled_avg_price)
                qty = float(filled_order.filled_qty)
                
                print(f"   ✅ FILLED: {qty:.6f} @ ${fill_price:.2f}")
                
                self.positions[symbol] = {
                    'entry_price': fill_price,
                    'quantity': qty,
                    'entry_time': datetime.now(),
                    'order_id': order.id
                }
                
                self.trade_log.append({
                    'timestamp': datetime.now().isoformat(),
                    'symbol': symbol,
                    'action': 'BUY',
                    'price': fill_price,
                    'quantity': qty,
                    'value': position_value
                })
                
                return True
            else:
                print(f"   ⚠️  Order not filled yet")
                return False
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def execute_sell(self, symbol):
        """Execute sell order"""
        if symbol not in self.positions:
            print(f"⚠️  No position for {symbol}")
            return False
        
        try:
            position = self.positions[symbol]
            qty = position['quantity']
            
            print(f"\n💰 Executing SELL for {symbol}")
            
            order_data = MarketOrderRequest(
                symbol=symbol,
                qty=qty,
                side=OrderSide.SELL,
                time_in_force=TimeInForce.GTC
            )
            
            order = self.trading_client.submit_order(order_data)
            print(f"   ✅ Order submitted: {order.id}")
            
            time.sleep(2)
            
            filled_order = self.trading_client.get_order_by_id(order.id)
            
            if filled_order.filled_at:
                fill_price = float(filled_order.filled_avg_price)
                entry_price = position['entry_price']
                
                pnl = (fill_price - entry_price) * qty
                pnl_pct = (fill_price - entry_price) / entry_price * 100
                
                print(f"   ✅ FILLED: {qty:.6f} @ ${fill_price:.2f}")
                print(f"   💵 P&L: ${pnl:,.2f} ({pnl_pct:+.2f}%)")
                
                self.trade_log.append({
                    'timestamp': datetime.now().isoformat(),
                    'symbol': symbol,
                    'action': 'SELL',
                    'price': fill_price,
                    'quantity': qty,
                    'pnl': pnl,
                    'pnl_pct': pnl_pct
                })
                
                del self.positions[symbol]
                
                return True
            else:
                print(f"   ⚠️  Order not filled yet")
                return False
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def run_strategy_check(self):
        """Run one iteration"""
        print(f"\n{'='*70}")
        print(f"⏰ Strategy Check - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}")
        
        self.get_account_info()
        
        for symbol in self.symbols:
            print(f"\n{'='*70}")
            print(f"Checking {symbol}...")
            print(f"{'='*70}")
            
            if symbol in self.positions:
                should_sell, reason = self.check_sell_signal(symbol, self.positions[symbol])
                print(f"Position Status: {reason}")
                
                if should_sell:
                    self.execute_sell(symbol)
            else:
                should_buy, reason = self.check_buy_signal(symbol)
                print(f"Signal Status: {reason}")
                
                if should_buy:
                    self.execute_buy(symbol)
        
        # Save log
        filename = f"moderate_trades_{datetime.now().strftime('%Y%m%d')}.json"
        with open(filename, 'w') as f:
            json.dump({
                'positions': self.positions,
                'trades': self.trade_log
            }, f, indent=2)
    
    def run_live(self, check_interval_minutes=60):
        """Run live trading loop"""
        print(f"\n🚀 Starting moderate activity trading...")
        print(f"   Check interval: Every {check_interval_minutes} minutes")
        print(f"   Expected: 1-2 trades per month")
        print(f"   Press Ctrl+C to stop\n")
        
        try:
            while True:
                self.run_strategy_check()
                print(f"\n⏳ Next check in {check_interval_minutes} minutes...")
                time.sleep(check_interval_minutes * 60)
                
        except KeyboardInterrupt:
            print(f"\n\n🛑 Stopped by user")
            
            total_trades = len([t for t in self.trade_log if t['action'] == 'SELL'])
            if total_trades > 0:
                sells = [t for t in self.trade_log if t['action'] == 'SELL']
                total_pnl = sum(t['pnl'] for t in sells)
                wins = len([t for t in sells if t['pnl'] > 0])
                win_rate = (wins / total_trades) * 100
                
                print(f"\n📊 SUMMARY:")
                print(f"Total Trades: {total_trades}")
                print(f"Win Rate: {win_rate:.1f}%")
                print(f"Total P&L: ${total_pnl:,.2f}")


def main():
    print("\n" + "="*70)
    print("🚀 MODERATE ACTIVITY CRYPTO TRADER")
    print("="*70)
    print("\nTrades 1-2 times per month (vs 2 times per year)")
    print("More action while maintaining good win rate!")
    print("\n" + "="*70 + "\n")
    
    api_key = os.getenv('ALPACA_API_KEY')
    secret_key = os.getenv('ALPACA_SECRET_KEY')
    
    if not api_key or not secret_key:
        print("❌ Alpaca API credentials not found!")
        return
    
    trader = ModerateActivityTrader(paper=True)
    trader.get_account_info()
    
    print("\n" + "="*70)
    print("OPTIONS:")
    print("="*70)
    print("1. Run ONE strategy check (test)")
    print("2. Run LIVE (checks every hour)")
    print("3. Exit")
    print("="*70)
    
    choice = input("\nYour choice (1-3): ").strip()
    
    if choice == '1':
        print("\n🔍 Running single check...\n")
        trader.run_strategy_check()
        
    elif choice == '2':
        print("\n🚀 Starting live trading...\n")
        trader.run_live(check_interval_minutes=60)
        
    else:
        print("\n👋 Goodbye!\n")


if __name__ == '__main__':
    main()
