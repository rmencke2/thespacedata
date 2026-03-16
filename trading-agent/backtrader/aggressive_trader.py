"""
Aggressive High-Frequency Strategy
Trades 2-4 times per month (30-50 trades/year)

Changes from moderate:
- Even shorter breakout period (5 days)
- No volume requirement
- Very wide RSI range (40-85)
- Quick profit target (10%) for rapid turnover
- Trades both momentum AND mean reversion
"""
import os
import time
import json
from datetime import datetime, timedelta
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame

class AggressiveTrader:
    """
    High-frequency version - trades 30-50 times per year
    Lower win rate but more learning opportunities
    """
    
    def __init__(self, api_key=None, secret_key=None, paper=True):
        self.api_key = api_key or os.getenv('ALPACA_API_KEY')
        self.secret_key = secret_key or os.getenv('ALPACA_SECRET_KEY')
        
        if not self.api_key or not self.secret_key:
            raise ValueError("Alpaca API credentials required!")
        
        self.trading_client = TradingClient(
            api_key=self.api_key,
            secret_key=self.secret_key,
            paper=paper
        )
        
        self.data_client = CryptoHistoricalDataClient()
        
        # AGGRESSIVE PARAMETERS (very active)
        self.symbols = ['BTC/USD', 'ETH/USD']
        self.breakout_period = 5  # 5 days = frequent breakouts
        self.volume_period = 20
        self.rsi_period = 14
        self.rsi_oversold = 35  # Buy dips too
        self.rsi_overbought = 70  # Sell rallies
        self.momentum_period = 2  # 2-day momentum
        
        # Aggressive risk management
        self.stop_loss_pct = 0.05  # 5% = tight stops
        self.take_profit_pct = 0.10  # 10% = quick profits
        self.position_size_pct = 0.45  # 45% per position
        
        # Tracking
        self.positions = {}
        self.trade_log = []
        
        print("🔥 Aggressive High-Frequency Crypto Trader Initialized")
        print(f"   Mode: {'PAPER' if paper else 'LIVE'}")
        print(f"   Symbols: {', '.join(self.symbols)}")
        print(f"   Target: 30-50 trades/year (2-4 per month)")
        print(f"   Strategy: Aggressive breakouts + dip buying")
    
    def get_account_info(self):
        """Get account status"""
        account = self.trading_client.get_account()
        
        print(f"\n💰 Account Status:")
        print(f"   Cash: ${float(account.cash):,.2f}")
        print(f"   Portfolio: ${float(account.portfolio_value):,.2f}")
        
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
                return None
            
            df = df.reset_index()
            df = df[df['symbol'] == symbol]
            
            return df
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def calculate_indicators(self, df):
        """Calculate indicators"""
        if df is None or len(df) < 10:
            return None
        
        # 5-day high (very frequent breakouts)
        df['highest_5'] = df['high'].rolling(window=self.breakout_period).max()
        df['lowest_5'] = df['low'].rolling(window=self.breakout_period).min()
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Momentum (2-day)
        df['momentum'] = df['close'].diff(self.momentum_period)
        
        # Moving averages for trend
        df['sma_20'] = df['close'].rolling(window=20).mean()
        
        return df
    
    def check_buy_signal(self, symbol):
        """Check for buy signal - very aggressive"""
        df = self.get_historical_data(symbol, days=30)
        
        if df is None:
            return False, "No data"
        
        df = self.calculate_indicators(df)
        
        if df is None:
            return False, "Not enough data"
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        close = latest['close']
        highest_5 = prev['highest_5']
        lowest_5 = prev['lowest_5']
        rsi = latest['rsi']
        momentum = latest['momentum']
        sma_20 = latest['sma_20']
        
        print(f"\n📊 {symbol} Analysis:")
        print(f"   Price: ${close:.2f}")
        print(f"   5-day Range: ${lowest_5:.2f} - ${highest_5:.2f}")
        print(f"   RSI: {rsi:.1f}")
        print(f"   Momentum: {momentum:.2f}")
        print(f"   vs 20 SMA: ${sma_20:.2f}")
        
        # SIGNAL 1: Breakout above 5-day high
        if close > highest_5 and momentum > 0:
            return True, "🚀 BREAKOUT - Above 5-day high!"
        
        # SIGNAL 2: Oversold bounce (buy the dip)
        if rsi < self.rsi_oversold and close > sma_20:
            return True, "💎 DIP BUY - RSI oversold!"
        
        # SIGNAL 3: Quick momentum reversal
        if momentum > close * 0.03:  # 3%+ move
            return True, "⚡ MOMENTUM - Strong upward move!"
        
        return False, "No signal"
    
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
        
        pnl_pct = (current_price - entry_price) / entry_price
        
        print(f"\n📊 {symbol} Position:")
        print(f"   Entry: ${entry_price:.2f}")
        print(f"   Current: ${current_price:.2f}")
        print(f"   P&L: {pnl_pct*100:+.2f}%")
        
        # Exit 1: Stop loss (5% = tight!)
        if pnl_pct <= -self.stop_loss_pct:
            return True, f"🛑 STOP ({pnl_pct*100:.2f}%)"
        
        # Exit 2: Take profit (10% = quick!)
        if pnl_pct >= self.take_profit_pct:
            return True, f"💎 PROFIT ({pnl_pct*100:.2f}%)"
        
        # Exit 3: RSI overbought
        if rsi > self.rsi_overbought:
            return True, f"📈 OVERBOUGHT ({rsi:.1f})"
        
        # Exit 4: Momentum reversal
        if pnl_pct > 0.03 and rsi > 60:  # Lock in 3%+ gains
            return True, f"🔒 LOCK GAINS ({pnl_pct*100:.2f}%)"
        
        return False, "Hold"
    
    def execute_buy(self, symbol):
        """Execute buy order"""
        try:
            account = self.trading_client.get_account()
            buying_power = float(account.buying_power)
            position_value = buying_power * self.position_size_pct
            
            print(f"\n💰 BUY {symbol}: ${position_value:,.0f}")
            
            order_data = MarketOrderRequest(
                symbol=symbol,
                notional=position_value,
                side=OrderSide.BUY,
                time_in_force=TimeInForce.GTC
            )
            
            order = self.trading_client.submit_order(order_data)
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
            
            return False
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def execute_sell(self, symbol):
        """Execute sell order"""
        if symbol not in self.positions:
            return False
        
        try:
            position = self.positions[symbol]
            qty = position['quantity']
            
            print(f"\n💰 SELL {symbol}")
            
            order_data = MarketOrderRequest(
                symbol=symbol,
                qty=qty,
                side=OrderSide.SELL,
                time_in_force=TimeInForce.GTC
            )
            
            order = self.trading_client.submit_order(order_data)
            time.sleep(2)
            
            filled_order = self.trading_client.get_order_by_id(order.id)
            
            if filled_order.filled_at:
                fill_price = float(filled_order.filled_avg_price)
                entry_price = position['entry_price']
                
                pnl = (fill_price - entry_price) * qty
                pnl_pct = (fill_price - entry_price) / entry_price * 100
                
                print(f"   ✅ FILLED @ ${fill_price:.2f}")
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
            
            return False
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def run_strategy_check(self):
        """Run one iteration"""
        print(f"\n{'='*70}")
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}")
        
        self.get_account_info()
        
        for symbol in self.symbols:
            print(f"\nChecking {symbol}...")
            
            if symbol in self.positions:
                should_sell, reason = self.check_sell_signal(symbol, self.positions[symbol])
                print(f"Status: {reason}")
                
                if should_sell:
                    self.execute_sell(symbol)
            else:
                should_buy, reason = self.check_buy_signal(symbol)
                print(f"Status: {reason}")
                
                if should_buy:
                    self.execute_buy(symbol)
        
        # Save log
        filename = f"aggressive_trades_{datetime.now().strftime('%Y%m%d')}.json"
        with open(filename, 'w') as f:
            json.dump({
                'positions': self.positions,
                'trades': self.trade_log
            }, f, indent=2)
    
    def run_live(self, check_interval_minutes=60):
        """Run live trading loop"""
        print(f"\n🔥 Starting aggressive trading...")
        print(f"   Expected: 2-4 trades per month")
        print(f"   Press Ctrl+C to stop\n")
        
        try:
            while True:
                self.run_strategy_check()
                print(f"\n⏳ Next check in {check_interval_minutes} min...")
                time.sleep(check_interval_minutes * 60)
                
        except KeyboardInterrupt:
            print(f"\n\n🛑 Stopped")
            
            sells = [t for t in self.trade_log if t['action'] == 'SELL']
            if sells:
                total_pnl = sum(t['pnl'] for t in sells)
                wins = len([t for t in sells if t['pnl'] > 0])
                win_rate = (wins / len(sells)) * 100
                
                print(f"\n📊 SUMMARY:")
                print(f"Trades: {len(sells)}")
                print(f"Win Rate: {win_rate:.1f}%")
                print(f"P&L: ${total_pnl:,.2f}")


def main():
    print("\n" + "="*70)
    print("🔥 AGGRESSIVE HIGH-FREQUENCY TRADER")
    print("="*70)
    print("\nTrades 2-4 times per month")
    print("Maximum learning speed!")
    print("\n" + "="*70 + "\n")
    
    api_key = os.getenv('ALPACA_API_KEY')
    secret_key = os.getenv('ALPACA_SECRET_KEY')
    
    if not api_key or not secret_key:
        print("❌ API credentials not found!")
        return
    
    trader = AggressiveTrader(paper=True)
    trader.get_account_info()
    
    print("\n" + "="*70)
    print("OPTIONS:")
    print("="*70)
    print("1. Run ONE check (test)")
    print("2. Run LIVE")
    print("3. Exit")
    print("="*70)
    
    choice = input("\nChoice (1-3): ").strip()
    
    if choice == '1':
        trader.run_strategy_check()
    elif choice == '2':
        trader.run_live(60)
    else:
        print("\n👋 Bye!\n")


if __name__ == '__main__':
    main()
