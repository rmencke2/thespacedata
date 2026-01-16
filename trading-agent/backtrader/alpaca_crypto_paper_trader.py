"""
Alpaca Crypto Paper Trading - Momentum Strategy
Live trading version of your backtested Momentum Breakout strategy

This will:
- Check BTC/ETH every hour for signals
- Execute trades on Alpaca paper account
- Track performance vs backtest
- Log everything for analysis
"""
import os
import time
import json
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame

class AlpacaCryptoMomentumTrader:
    """
    Live paper trading implementation of Crypto Momentum strategy
    """
    
    def __init__(self, api_key=None, secret_key=None, paper=True):
        """Initialize Alpaca clients"""
        
        # Get credentials from environment or parameters
        self.api_key = api_key or os.getenv('ALPACA_API_KEY')
        self.secret_key = secret_key or os.getenv('ALPACA_SECRET_KEY')
        
        if not self.api_key or not self.secret_key:
            raise ValueError("Alpaca API credentials required! Set ALPACA_API_KEY and ALPACA_SECRET_KEY")
        
        # Initialize clients
        self.trading_client = TradingClient(
            api_key=self.api_key,
            secret_key=self.secret_key,
            paper=paper
        )
        
        self.data_client = CryptoHistoricalDataClient()
        
        # Strategy parameters (from your backtest)
        self.symbols = ['BTC/USD', 'ETH/USD']  # Start with winners
        self.breakout_period = 20
        self.volume_multiplier = 2.0
        self.rsi_min = 60
        self.rsi_max = 80
        self.momentum_period = 3
        
        # Risk management
        self.stop_loss_pct = 0.08  # 8%
        self.take_profit_pct = 0.20  # 20%
        self.position_size_pct = 0.45  # 45% per position (can hold 2)
        
        # Tracking
        self.positions = {}
        self.trade_log = []
        self.last_check = {}
        
        print("🚀 Alpaca Crypto Paper Trader Initialized")
        print(f"   Mode: {'PAPER' if paper else 'LIVE'}")
        print(f"   Symbols: {', '.join(self.symbols)}")
        print(f"   Strategy: Momentum Breakout")
    
    def get_account_info(self):
        """Get account status"""
        account = self.trading_client.get_account()
        
        print(f"\n💰 Account Status:")
        print(f"   Cash: ${float(account.cash):,.2f}")
        print(f"   Portfolio: ${float(account.portfolio_value):,.2f}")
        print(f"   Buying Power: ${float(account.buying_power):,.2f}")
        print(f"   Crypto Status: {account.crypto_status}")
        
        return account
    
    def get_historical_data(self, symbol, days=30):
        """Get historical data for analysis"""
        
        # Alpaca crypto uses BTC/USD format (keep the slash!)
        
        try:
            # Request parameters
            request_params = CryptoBarsRequest(
                symbol_or_symbols=[symbol],  # Use symbol as-is: 'BTC/USD'
                timeframe=TimeFrame.Day,
                start=datetime.now() - timedelta(days=days)
            )
            
            # Get data
            bars = self.data_client.get_crypto_bars(request_params)
            
            # Convert to DataFrame
            df = bars.df
            
            if df.empty:
                print(f"⚠️  No data for {symbol}")
                return None
            
            # Clean up
            df = df.reset_index()
            df = df[df['symbol'] == symbol]  # Filter for our symbol
            
            return df
            
        except Exception as e:
            print(f"❌ Error getting data for {symbol}: {e}")
            return None
    
    def calculate_indicators(self, df):
        """Calculate momentum indicators"""
        
        if df is None or len(df) < self.breakout_period + 1:
            return None
        
        # Breakout: 20-day high
        df['highest_20'] = df['high'].rolling(window=self.breakout_period).max()
        
        # Volume: 20-day average
        df['volume_sma'] = df['volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_sma']
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Momentum (3-day)
        df['momentum'] = df['close'].diff(self.momentum_period)
        
        return df
    
    def check_buy_signal(self, symbol):
        """Check if we should buy"""
        
        # Get data
        df = self.get_historical_data(symbol, days=30)
        
        if df is None:
            return False, "No data"
        
        # Calculate indicators
        df = self.calculate_indicators(df)
        
        if df is None:
            return False, "Not enough data"
        
        # Get latest values
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        close = latest['close']
        highest_20 = prev['highest_20']  # Previous day's high
        volume_ratio = latest['volume_ratio']
        rsi = latest['rsi']
        momentum = latest['momentum']
        
        print(f"\n📊 {symbol} Analysis:")
        print(f"   Price: ${close:.2f}")
        print(f"   20-day High: ${highest_20:.2f}")
        print(f"   Volume: {volume_ratio:.2f}x avg")
        print(f"   RSI: {rsi:.1f}")
        print(f"   Momentum: {momentum:.2f}")
        
        # Check 1: Breakout above 20-day high
        if close <= highest_20:
            return False, f"No breakout (${close:.2f} <= ${highest_20:.2f})"
        
        # Check 2: Volume explosion
        if volume_ratio < self.volume_multiplier:
            return False, f"Low volume ({volume_ratio:.2f}x < {self.volume_multiplier}x)"
        
        # Check 3: RSI in range
        if not (self.rsi_min <= rsi <= self.rsi_max):
            return False, f"RSI out of range ({rsi:.1f})"
        
        # Check 4: Momentum positive
        if momentum <= 0:
            return False, f"Negative momentum ({momentum:.2f})"
        
        # ALL CHECKS PASSED!
        return True, "🚀 BUY SIGNAL - All conditions met!"
    
    def check_sell_signal(self, symbol, position):
        """Check if we should sell"""
        
        # Get current price
        df = self.get_historical_data(symbol, days=5)
        
        if df is None:
            return False, "No data"
        
        # Calculate indicators
        df = self.calculate_indicators(df)
        
        if df is None:
            return False, "Not enough data"
        
        latest = df.iloc[-1]
        current_price = latest['close']
        entry_price = position['entry_price']
        rsi = latest['rsi']
        volume_ratio = latest['volume_ratio']
        
        # Calculate P&L
        pnl_pct = (current_price - entry_price) / entry_price
        
        print(f"\n📊 {symbol} Position Check:")
        print(f"   Entry: ${entry_price:.2f}")
        print(f"   Current: ${current_price:.2f}")
        print(f"   P&L: {pnl_pct*100:+.2f}%")
        print(f"   RSI: {rsi:.1f}")
        print(f"   Volume: {volume_ratio:.2f}x")
        
        # Exit 1: Stop loss
        if pnl_pct <= -self.stop_loss_pct:
            return True, f"🛑 STOP LOSS ({pnl_pct*100:.2f}%)"
        
        # Exit 2: Take profit
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
            # Get account
            account = self.trading_client.get_account()
            buying_power = float(account.buying_power)
            
            # Calculate position size
            position_value = buying_power * self.position_size_pct
            
            print(f"\n💰 Executing BUY for {symbol}")
            print(f"   Buying Power: ${buying_power:,.2f}")
            print(f"   Position Size: ${position_value:,.2f}")
            
            # Create order
            order_data = MarketOrderRequest(
                symbol=symbol,
                notional=position_value,  # Dollar amount
                side=OrderSide.BUY,
                time_in_force=TimeInForce.GTC
            )
            
            # Submit order
            order = self.trading_client.submit_order(order_data)
            
            print(f"   ✅ Order submitted: {order.id}")
            
            # Wait for fill
            time.sleep(2)
            
            # Get filled order
            filled_order = self.trading_client.get_order_by_id(order.id)
            
            if filled_order.filled_at:
                fill_price = float(filled_order.filled_avg_price)
                qty = float(filled_order.filled_qty)
                
                print(f"   ✅ FILLED: {qty:.6f} @ ${fill_price:.2f}")
                
                # Track position
                self.positions[symbol] = {
                    'entry_price': fill_price,
                    'quantity': qty,
                    'entry_time': datetime.now(),
                    'order_id': order.id
                }
                
                # Log trade
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
            print(f"   Quantity: {qty:.6f}")
            
            # Create order
            order_data = MarketOrderRequest(
                symbol=symbol,
                qty=qty,
                side=OrderSide.SELL,
                time_in_force=TimeInForce.GTC
            )
            
            # Submit order
            order = self.trading_client.submit_order(order_data)
            
            print(f"   ✅ Order submitted: {order.id}")
            
            # Wait for fill
            time.sleep(2)
            
            # Get filled order
            filled_order = self.trading_client.get_order_by_id(order.id)
            
            if filled_order.filled_at:
                fill_price = float(filled_order.filled_avg_price)
                entry_price = position['entry_price']
                
                pnl = (fill_price - entry_price) * qty
                pnl_pct = (fill_price - entry_price) / entry_price * 100
                
                print(f"   ✅ FILLED: {qty:.6f} @ ${fill_price:.2f}")
                print(f"   💵 P&L: ${pnl:,.2f} ({pnl_pct:+.2f}%)")
                
                # Log trade
                self.trade_log.append({
                    'timestamp': datetime.now().isoformat(),
                    'symbol': symbol,
                    'action': 'SELL',
                    'price': fill_price,
                    'quantity': qty,
                    'pnl': pnl,
                    'pnl_pct': pnl_pct
                })
                
                # Remove position
                del self.positions[symbol]
                
                return True
            else:
                print(f"   ⚠️  Order not filled yet")
                return False
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def run_strategy_check(self):
        """Run one iteration of strategy checks"""
        
        print(f"\n{'='*70}")
        print(f"⏰ Strategy Check - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}")
        
        # Check account
        self.get_account_info()
        
        # Check each symbol
        for symbol in self.symbols:
            print(f"\n{'='*70}")
            print(f"Checking {symbol}...")
            print(f"{'='*70}")
            
            # Do we have a position?
            if symbol in self.positions:
                # Check if we should sell
                should_sell, reason = self.check_sell_signal(symbol, self.positions[symbol])
                
                print(f"Position Status: {reason}")
                
                if should_sell:
                    self.execute_sell(symbol)
            else:
                # Check if we should buy
                should_buy, reason = self.check_buy_signal(symbol)
                
                print(f"Signal Status: {reason}")
                
                if should_buy:
                    self.execute_buy(symbol)
        
        # Save trade log
        self.save_trade_log()
    
    def save_trade_log(self):
        """Save trade log to file"""
        
        filename = f"alpaca_trades_{datetime.now().strftime('%Y%m%d')}.json"
        
        with open(filename, 'w') as f:
            json.dump({
                'positions': self.positions,
                'trades': self.trade_log
            }, f, indent=2)
    
    def run_live(self, check_interval_minutes=60):
        """Run live trading loop"""
        
        print(f"\n🚀 Starting live paper trading...")
        print(f"   Check interval: Every {check_interval_minutes} minutes")
        print(f"   Press Ctrl+C to stop\n")
        
        try:
            while True:
                self.run_strategy_check()
                
                # Wait for next check
                print(f"\n⏳ Next check in {check_interval_minutes} minutes...")
                time.sleep(check_interval_minutes * 60)
                
        except KeyboardInterrupt:
            print(f"\n\n🛑 Stopped by user")
            self.print_summary()
    
    def print_summary(self):
        """Print trading summary"""
        
        print(f"\n{'='*70}")
        print("📊 TRADING SUMMARY")
        print(f"{'='*70}")
        
        # Calculate stats
        total_trades = len([t for t in self.trade_log if t['action'] == 'SELL'])
        
        if total_trades > 0:
            sells = [t for t in self.trade_log if t['action'] == 'SELL']
            total_pnl = sum(t['pnl'] for t in sells)
            wins = len([t for t in sells if t['pnl'] > 0])
            win_rate = (wins / total_trades) * 100
            
            print(f"Total Trades: {total_trades}")
            print(f"Win Rate: {win_rate:.1f}%")
            print(f"Total P&L: ${total_pnl:,.2f}")
        else:
            print("No completed trades yet")
        
        # Current positions
        if self.positions:
            print(f"\nOpen Positions:")
            for symbol, pos in self.positions.items():
                print(f"  {symbol}: {pos['quantity']:.6f} @ ${pos['entry_price']:.2f}")
        
        print(f"{'='*70}\n")


def main():
    """Main entry point"""
    
    print("\n" + "="*70)
    print("🚀 ALPACA CRYPTO PAPER TRADER")
    print("="*70)
    print("\nMomentum Breakout Strategy")
    print("Based on your +95% backtest on ETH!")
    print("\n" + "="*70 + "\n")
    
    # Check for API keys
    api_key = os.getenv('ALPACA_API_KEY')
    secret_key = os.getenv('ALPACA_SECRET_KEY')
    
    if not api_key or not secret_key:
        print("❌ Alpaca API credentials not found!")
        print("\nPlease set environment variables:")
        print("  export ALPACA_API_KEY='your_paper_key'")
        print("  export ALPACA_SECRET_KEY='your_paper_secret'")
        print("\nOr edit this script to hardcode them (not recommended)\n")
        return
    
    # Initialize trader
    trader = AlpacaCryptoMomentumTrader(paper=True)
    
    # Get initial account status
    trader.get_account_info()
    
    # Ask user what to do
    print("\n" + "="*70)
    print("OPTIONS:")
    print("="*70)
    print("1. Run ONE strategy check (test)")
    print("2. Run LIVE (checks every hour)")
    print("3. Exit")
    print("="*70)
    
    choice = input("\nYour choice (1-3): ").strip()
    
    if choice == '1':
        print("\n🔍 Running single strategy check...\n")
        trader.run_strategy_check()
        trader.print_summary()
        
    elif choice == '2':
        print("\n🚀 Starting live trading...\n")
        trader.run_live(check_interval_minutes=60)
        
    else:
        print("\n👋 Goodbye!\n")


if __name__ == '__main__':
    main()
