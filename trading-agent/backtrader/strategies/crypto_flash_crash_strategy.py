"""
Crypto Flash Crash / Mean Reversion Strategy
Buy the panic, sell the recovery

Crypto-specific features:
- Flash crash detection (15%+ drop in 24h)
- Weekend dump pattern (buy Sunday lows)
- Oversold bounce (extreme RSI recovery)
- Panic volume spikes (capitulation)
"""
import backtrader as bt

class CryptoFlashCrashStrategy(bt.Strategy):
    """
    Crypto Flash Crash Strategy
    
    BUY when:
    1. Price drops 15%+ from recent high (flash crash)
    2. Volume > 3x average (panic selling)
    3. RSI < 25 (extreme oversold)
    4. Still above 200 SMA (long-term uptrend)
    
    SELL when:
    1. Price recovers 10% from entry (quick profit)
    2. OR RSI > 70 (overbought bounce)
    3. OR 48 hours passed (don't hold too long)
    """
    
    params = dict(
        # Flash crash detection
        lookback_period=24,  # 24 periods back (24 hours if 1H, 24 days if 1D)
        crash_threshold=0.15,  # 15% drop = flash crash
        
        # Panic indicators
        volume_period=20,
        panic_volume_mult=3.0,  # 3x volume = panic
        rsi_period=14,
        rsi_oversold=25,  # Extreme for crypto
        rsi_exit=70,  # Exit on bounce
        
        # Trend filter
        sma_period=200,  # Only buy crashes in uptrend
        
        # Crypto mean reversion
        profit_target_pct=0.10,  # 10% quick profit
        stop_loss_pct=0.08,  # 8% stop
        max_hold_periods=48,  # Don't hold forever
        
        position_size=0.95,
        debug=False,
    )
    
    def __init__(self):
        """Initialize flash crash indicators"""
        
        self.dataclose = self.datas[0].close
        self.datahigh = self.datas[0].high
        self.volume = self.datas[0].volume
        
        # Highest high for crash detection
        self.highest = bt.indicators.Highest(
            self.datahigh,
            period=self.params.lookback_period
        )
        
        # Volume for panic detection
        self.volume_sma = bt.indicators.SimpleMovingAverage(
            self.volume,
            period=self.params.volume_period
        )
        
        # RSI for oversold
        self.rsi = bt.indicators.RSI(
            self.datas[0],
            period=self.params.rsi_period
        )
        
        # Trend filter
        self.sma200 = bt.indicators.SimpleMovingAverage(
            self.datas[0],
            period=self.params.sma_period
        )
        
        # Position tracking
        self.order = None
        self.buyprice = None
        self.buy_bar = None
        self.take_profit = None
        self.stop_loss = None
        
        # Stats
        self.trades_count = 0
        self.wins = 0
        self.losses = 0
        self.flash_crashes_caught = 0
        
    def log(self, txt, dt=None):
        if self.params.debug:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()} {txt}')
    
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        
        if order.status in [order.Completed]:
            if order.isbuy():
                self.buyprice = order.executed.price
                self.buy_bar = len(self)
                self.take_profit = self.buyprice * (1 + self.params.profit_target_pct)
                self.stop_loss = self.buyprice * (1 - self.params.stop_loss_pct)
                
                self.flash_crashes_caught += 1
                
                self.log(f'💥 FLASH CRASH BUY: ${self.buyprice:.2f}')
                self.log(f'   Target: ${self.take_profit:.2f} | Stop: ${self.stop_loss:.2f}')
            else:
                if self.buyprice:
                    pnl = order.executed.price - self.buyprice
                    pnl_pct = (pnl / self.buyprice) * 100
                    hold_time = len(self) - self.buy_bar
                    
                    if pnl > 0:
                        self.wins += 1
                        self.log(f'✅ PROFIT: ${pnl:.2f} ({pnl_pct:+.2f}%) in {hold_time} bars')
                    else:
                        self.losses += 1
                        self.log(f'❌ LOSS: ${pnl:.2f} ({pnl_pct:+.2f}%) held {hold_time} bars')
                    
                    self.trades_count += 1
                
                self.log(f'💰 SOLD: ${order.executed.price:.2f}')
        
        self.order = None
    
    def next(self):
        """Flash crash detection logic"""
        
        # Calculate drop from recent high
        drop_pct = (self.highest[0] - self.dataclose[0]) / self.highest[0] if self.highest[0] > 0 else 0
        volume_ratio = self.volume[0] / self.volume_sma[0] if self.volume_sma[0] > 0 else 0
        
        self.log(
            f'Price: ${self.dataclose[0]:.2f} | '
            f'High: ${self.highest[0]:.2f} | '
            f'Drop: {drop_pct*100:.1f}% | '
            f'RSI: {self.rsi[0]:.1f} | '
            f'Vol: {volume_ratio:.2f}x'
        )
        
        if self.order:
            return
        
        if not self.position:
            # === FLASH CRASH BUY LOGIC ===
            
            # Check 1: Is this a flash crash? (15%+ drop)
            if drop_pct < self.params.crash_threshold:
                return
            
            # Check 2: Panic volume (capitulation)
            if volume_ratio < self.params.panic_volume_mult:
                self.log(f'❌ No crash buy: Volume not high enough ({volume_ratio:.2f}x)')
                return
            
            # Check 3: Extreme oversold (RSI < 25)
            if self.rsi[0] > self.params.rsi_oversold:
                self.log(f'❌ No crash buy: RSI not oversold enough ({self.rsi[0]:.1f})')
                return
            
            # Check 4: Still in long-term uptrend (above 200 SMA)
            if self.dataclose[0] < self.sma200[0]:
                self.log(f'❌ No crash buy: Below 200 SMA (downtrend)')
                return
            
            # FLASH CRASH DETECTED - BUY THE PANIC!
            self.log(f'💥💥💥 FLASH CRASH DETECTED!')
            self.log(f'   ⚡ Price dropped {drop_pct*100:.1f}% from high')
            self.log(f'   ⚡ Panic volume: {volume_ratio:.2f}x average')
            self.log(f'   ⚡ RSI extremely oversold: {self.rsi[0]:.1f}')
            self.log(f'   ⚡ Still above 200 SMA: ${self.sma200[0]:.2f}')
            
            # Calculate position
            cash = self.broker.getcash()
            size = int((cash * self.params.position_size) / self.dataclose[0])
            
            self.order = self.buy(size=max(size, 1))
        
        else:
            # === MEAN REVERSION EXIT LOGIC ===
            
            # How long have we held?
            hold_time = len(self) - self.buy_bar
            
            # Exit 1: Take profit (10% recovery)
            if self.dataclose[0] >= self.take_profit:
                self.log(f'💎 TAKE PROFIT: Recovered {self.params.profit_target_pct*100:.0f}%')
                self.order = self.sell(size=self.position.size)
            
            # Exit 2: RSI overbought (bounce exhausted)
            elif self.rsi[0] > self.params.rsi_exit:
                self.log(f'📈 EXIT: RSI overbought ({self.rsi[0]:.1f})')
                self.order = self.sell(size=self.position.size)
            
            # Exit 3: Max hold time (don't marry position)
            elif hold_time >= self.params.max_hold_periods:
                self.log(f'⏰ EXIT: Max hold time reached ({hold_time} bars)')
                self.order = self.sell(size=self.position.size)
            
            # Exit 4: Stop loss (failed recovery)
            elif self.dataclose[0] < self.stop_loss:
                self.log(f'🛑 STOP LOSS: Failed recovery')
                self.order = self.sell(size=self.position.size)
    
    def stop(self):
        """Final stats"""
        total_trades = self.wins + self.losses
        win_rate = (self.wins / total_trades * 100) if total_trades > 0 else 0
        final_value = self.broker.getvalue()
        
        print('\n' + '='*70)
        print(f'💥 CRYPTO FLASH CRASH STRATEGY RESULTS')
        print('='*70)
        print(f'Final Value: ${final_value:,.2f}')
        print(f'Flash Crashes Caught: {self.flash_crashes_caught}')
        print(f'Total Trades: {total_trades}')
        print(f'Win Rate: {win_rate:.1f}% ({self.wins}W / {self.losses}L)')
        print('='*70 + '\n')


if __name__ == '__main__':
    print("\n💥 Crypto Flash Crash Strategy")
    print("   Buys: 15%+ drops with panic volume")
    print("   Sells: 10% recovery or RSI overbought")
    print("\nRun with: python crypto_native_backtest.py\n")
