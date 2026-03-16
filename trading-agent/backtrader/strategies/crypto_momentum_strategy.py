"""
Crypto Momentum Breakout Strategy
Designed specifically for cryptocurrency markets

Catches: Parabolic pumps, breakouts, volume explosions
Avoids: Dumps, dead coins, low volume traps

Crypto-specific features:
- Volume spike detection (whale activity)
- Momentum acceleration (catching pumps early)
- Quick profit taking (crypto moves fast)
- Flash crash protection (buy the panic)
"""
import backtrader as bt

class CryptoMomentumStrategy(bt.Strategy):
    """
    Crypto-Specific Momentum Strategy
    
    BUY when:
    1. Price breaks above 20-day high (breakout)
    2. Volume > 2x average (whale accumulation)
    3. RSI > 60 but < 80 (momentum but not exhausted)
    4. 3-day momentum positive (trend accelerating)
    
    SELL when:
    1. Price drops 8% from entry (crypto stop loss)
    2. OR hits 20% profit target (take profits fast)
    3. OR RSI > 85 (extreme overbought)
    4. OR volume drops 50% (momentum dying)
    """
    
    params = dict(
        # Breakout detection
        breakout_period=20,  # 20-day high breakout
        
        # Volume explosion
        volume_period=20,
        volume_multiplier=2.0,  # Need 2x average volume
        volume_exit_drop=0.5,  # Exit if volume drops 50%
        
        # Momentum
        momentum_period=3,  # 3-day momentum
        rsi_period=14,
        rsi_entry_min=60,  # Strength required
        rsi_entry_max=80,  # But not exhausted
        rsi_exit=85,  # Extreme = exit
        
        # Crypto risk management
        stop_loss_pct=0.08,  # 8% stop (crypto volatility)
        take_profit_pct=0.20,  # 20% target (take profits fast!)
        
        # Position sizing
        position_size=0.95,
        
        debug=False,
    )
    
    def __init__(self):
        """Initialize crypto momentum indicators"""
        
        self.dataclose = self.datas[0].close
        self.datahigh = self.datas[0].high
        self.volume = self.datas[0].volume
        
        # Breakout detection
        self.highest = bt.indicators.Highest(
            self.datahigh,
            period=self.params.breakout_period
        )
        
        # Volume indicators
        self.volume_sma = bt.indicators.SimpleMovingAverage(
            self.volume,
            period=self.params.volume_period
        )
        
        # Momentum
        self.momentum = bt.indicators.Momentum(
            self.datas[0],
            period=self.params.momentum_period
        )
        
        # RSI
        self.rsi = bt.indicators.RSI(
            self.datas[0],
            period=self.params.rsi_period
        )
        
        # Track positions
        self.order = None
        self.buyprice = None
        self.stop_loss = None
        self.take_profit = None
        self.entry_volume = None
        
        # Stats
        self.trades_count = 0
        self.wins = 0
        self.losses = 0
        
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
                self.entry_volume = self.volume[0]
                self.stop_loss = self.buyprice * (1 - self.params.stop_loss_pct)
                self.take_profit = self.buyprice * (1 + self.params.take_profit_pct)
                
                self.log(f'🚀 BREAKOUT BUY: ${self.buyprice:.2f}')
                self.log(f'   Stop: ${self.stop_loss:.2f} | Target: ${self.take_profit:.2f}')
            else:
                if self.buyprice:
                    pnl = order.executed.price - self.buyprice
                    pnl_pct = (pnl / self.buyprice) * 100
                    
                    if pnl > 0:
                        self.wins += 1
                        self.log(f'✅ PROFIT: ${pnl:.2f} ({pnl_pct:+.2f}%)')
                    else:
                        self.losses += 1
                        self.log(f'❌ LOSS: ${pnl:.2f} ({pnl_pct:+.2f}%)')
                    
                    self.trades_count += 1
                
                self.log(f'💰 SOLD: ${order.executed.price:.2f}')
        
        self.order = None
    
    def next(self):
        """Crypto momentum logic"""
        
        # Calculate volume spike
        volume_ratio = self.volume[0] / self.volume_sma[0] if self.volume_sma[0] > 0 else 0
        
        self.log(
            f'Price: ${self.dataclose[0]:.2f} | '
            f'High20: ${self.highest[0]:.2f} | '
            f'RSI: {self.rsi[0]:.1f} | '
            f'Vol: {volume_ratio:.2f}x | '
            f'Mom: {self.momentum[0]:.2f}'
        )
        
        if self.order:
            return
        
        if not self.position:
            # === CRYPTO BREAKOUT BUY ===
            
            # Check 1: Price breaking out above 20-day high
            if self.dataclose[0] <= self.highest[-1]:
                return
            
            # Check 2: Volume explosion (whale activity)
            if volume_ratio < self.params.volume_multiplier:
                self.log(f'❌ No buy: Volume too low ({volume_ratio:.2f}x)')
                return
            
            # Check 3: RSI shows strength but not exhaustion
            if not (self.params.rsi_entry_min <= self.rsi[0] <= self.params.rsi_entry_max):
                self.log(f'❌ No buy: RSI {self.rsi[0]:.1f} outside range')
                return
            
            # Check 4: Momentum accelerating
            if self.momentum[0] <= 0:
                self.log(f'❌ No buy: Momentum negative')
                return
            
            # ALL CHECKS PASSED - CRYPTO PUMP DETECTED!
            self.log(f'🚀🚀🚀 CRYPTO BREAKOUT!')
            self.log(f'   ✅ New 20-day high: ${self.dataclose[0]:.2f}')
            self.log(f'   ✅ Volume spike: {volume_ratio:.2f}x average')
            self.log(f'   ✅ RSI: {self.rsi[0]:.1f} (strong momentum)')
            self.log(f'   ✅ Momentum: {self.momentum[0]:.2f}')
            
            # Calculate position
            cash = self.broker.getcash()
            size = int((cash * self.params.position_size) / self.dataclose[0])
            
            self.order = self.buy(size=max(size, 1))
        
        else:
            # === CRYPTO EXIT LOGIC ===
            
            # Exit 1: Stop loss (8% for crypto volatility)
            if self.dataclose[0] < self.stop_loss:
                self.log(f'🛑 STOP LOSS: ${self.dataclose[0]:.2f} < ${self.stop_loss:.2f}')
                self.order = self.sell(size=self.position.size)
            
            # Exit 2: Take profit (20% - take profits fast in crypto!)
            elif self.dataclose[0] > self.take_profit:
                self.log(f'💎 TAKE PROFIT: ${self.dataclose[0]:.2f} > ${self.take_profit:.2f}')
                self.order = self.sell(size=self.position.size)
            
            # Exit 3: RSI extreme overbought (pump exhaustion)
            elif self.rsi[0] > self.params.rsi_exit:
                self.log(f'📈 EXIT: RSI extreme ({self.rsi[0]:.1f})')
                self.order = self.sell(size=self.position.size)
            
            # Exit 4: Volume dying (momentum over)
            elif self.entry_volume and volume_ratio < self.params.volume_exit_drop:
                self.log(f'📉 EXIT: Volume dying ({volume_ratio:.2f}x)')
                self.order = self.sell(size=self.position.size)
    
    def stop(self):
        """Final stats"""
        total_trades = self.wins + self.losses
        win_rate = (self.wins / total_trades * 100) if total_trades > 0 else 0
        final_value = self.broker.getvalue()
        
        print('\n' + '='*70)
        print(f'🚀 CRYPTO MOMENTUM STRATEGY RESULTS')
        print('='*70)
        print(f'Final Value: ${final_value:,.2f}')
        print(f'Total Trades: {total_trades}')
        print(f'Win Rate: {win_rate:.1f}% ({self.wins}W / {self.losses}L)')
        print('='*70 + '\n')


if __name__ == '__main__':
    print("\n🚀 Crypto Momentum Breakout Strategy")
    print("   Catches: Pumps, breakouts, whale activity")
    print("   Avoids: Low volume, weak momentum")
    print("\nRun with: python crypto_native_backtest.py\n")
