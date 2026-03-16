"""
Advanced Multi-Indicator Strategy
Combines multiple indicators for high-probability trades

This is a professional-grade strategy that uses:
- Trend (200 SMA + 50 SMA)
- Momentum (MACD)
- Strength (RSI)
- Volatility (ATR for stops)
- Volume (confirmation)
"""
import backtrader as bt

class MultiIndicatorStrategy(bt.Strategy):
    """
    Advanced Multi-Indicator Strategy
    
    BUY Requirements (ALL must be true):
    1. Price > 200 SMA (long-term uptrend)
    2. Price > 50 SMA (short-term uptrend)
    3. MACD positive crossover (momentum shift)
    4. RSI between 40-70 (healthy, not extreme)
    5. Volume > 20-day average (confirmation)
    6. Recent pullback to 50 SMA (better entry)
    
    SELL Triggers:
    1. Price < 50 SMA (trend weakening)
    OR
    2. MACD negative crossover
    OR
    3. RSI > 75 (overbought)
    OR
    4. ATR-based trailing stop
    """
    
    params = dict(
        # Trend indicators
        sma_long=200,
        sma_short=50,
        
        # Momentum
        macd_fast=12,
        macd_slow=26,
        macd_signal=9,
        
        # Strength
        rsi_period=14,
        rsi_min=40,
        rsi_max=70,
        rsi_exit=75,
        
        # Volume
        volume_period=20,
        volume_factor=1.0,
        
        # Risk management
        atr_period=14,
        atr_stop_multiplier=2.0,  # Stop = 2x ATR below entry
        risk_per_trade=0.02,  # Risk 2% per trade
        position_size=0.95,
        
        debug=False,
    )
    
    def __init__(self):
        """Initialize all indicators"""
        
        self.dataclose = self.datas[0].close
        
        # === TREND INDICATORS ===
        self.sma_long = bt.indicators.SimpleMovingAverage(
            self.datas[0],
            period=self.params.sma_long
        )
        
        self.sma_short = bt.indicators.SimpleMovingAverage(
            self.datas[0],
            period=self.params.sma_short
        )
        
        # === MOMENTUM INDICATORS ===
        self.macd = bt.indicators.MACD(
            self.datas[0],
            period_me1=self.params.macd_fast,
            period_me2=self.params.macd_slow,
            period_signal=self.params.macd_signal
        )
        
        # MACD crossover signal
        self.macd_cross = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)
        
        # === STRENGTH INDICATORS ===
        self.rsi = bt.indicators.RSI(
            self.datas[0],
            period=self.params.rsi_period
        )
        
        # === VOLATILITY INDICATORS ===
        self.atr = bt.indicators.ATR(
            self.datas[0],
            period=self.params.atr_period
        )
        
        # === VOLUME INDICATORS ===
        self.volume = self.datas[0].volume
        self.volume_sma = bt.indicators.SimpleMovingAverage(
            self.volume,
            period=self.params.volume_period
        )
        
        # Order tracking
        self.order = None
        self.buyprice = None
        self.atr_stop = None
        
        # Performance
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
                self.log(f'✅ BUY: ${order.executed.price:.2f}')
                self.buyprice = order.executed.price
                
                # Set ATR-based stop
                self.atr_stop = self.buyprice - (self.atr[0] * self.params.atr_stop_multiplier)
                self.log(f'   ATR Stop: ${self.atr_stop:.2f} (ATR={self.atr[0]:.2f})')
                
            else:
                if self.buyprice:
                    pnl = order.executed.price - self.buyprice
                    pnl_pct = (pnl / self.buyprice) * 100
                    
                    if pnl > 0:
                        self.wins += 1
                        self.log(f'✅ WIN: ${pnl:.2f} ({pnl_pct:+.2f}%)')
                    else:
                        self.losses += 1
                        self.log(f'❌ LOSS: ${pnl:.2f} ({pnl_pct:+.2f}%)')
                    
                    self.trades_count += 1
                
                self.log(f'💰 SELL: ${order.executed.price:.2f}')
        
        self.order = None
    
    def next(self):
        """Main strategy logic with multiple confirmations"""
        
        # Log state
        self.log(
            f'Price: ${self.dataclose[0]:.2f} | '
            f'SMA200: ${self.sma_long[0]:.2f} | '
            f'SMA50: ${self.sma_short[0]:.2f} | '
            f'RSI: {self.rsi[0]:.1f} | '
            f'MACD: {self.macd.macd[0]:.2f}'
        )
        
        if self.order:
            return
        
        if not self.position:
            # === MULTI-INDICATOR BUY LOGIC ===
            
            # Check 1: Long-term trend
            if self.dataclose[0] <= self.sma_long[0]:
                self.log(f'❌ No buy: Price below 200 SMA')
                return
            
            # Check 2: Short-term trend
            if self.dataclose[0] <= self.sma_short[0]:
                self.log(f'❌ No buy: Price below 50 SMA')
                return
            
            # Check 3: MACD positive crossover
            if self.macd_cross[0] <= 0:
                self.log(f'❌ No buy: No MACD crossover')
                return
            
            # Check 4: RSI healthy range
            if not (self.params.rsi_min <= self.rsi[0] <= self.params.rsi_max):
                self.log(f'❌ No buy: RSI {self.rsi[0]:.1f} outside {self.params.rsi_min}-{self.params.rsi_max}')
                return
            
            # Check 5: Volume confirmation
            if self.volume[0] < self.volume_sma[0] * self.params.volume_factor:
                self.log(f'❌ No buy: Low volume')
                return
            
            # ALL CHECKS PASSED!
            self.log(f'🚀🚀🚀 STRONG BUY SIGNAL - All indicators aligned!')
            self.log(f'   ✅ Price > 200 SMA & 50 SMA')
            self.log(f'   ✅ MACD crossover')
            self.log(f'   ✅ RSI {self.rsi[0]:.1f} in healthy range')
            self.log(f'   ✅ Volume confirmed')
            
            # Calculate position size
            cash = self.broker.getcash()
            size = int((cash * self.params.position_size) / self.dataclose[0])
            
            self.order = self.buy(size=max(size, 1))
        
        else:
            # === MULTI-INDICATOR SELL LOGIC ===
            
            # Exit 1: Price below 50 SMA (trend weakening)
            if self.dataclose[0] < self.sma_short[0]:
                self.log(f'📉 SELL: Price below 50 SMA')
                self.order = self.sell(size=self.position.size)
            
            # Exit 2: MACD negative crossover
            elif self.macd_cross[0] < 0:
                self.log(f'📉 SELL: MACD negative crossover')
                self.order = self.sell(size=self.position.size)
            
            # Exit 3: RSI overbought
            elif self.rsi[0] > self.params.rsi_exit:
                self.log(f'📈 SELL: RSI overbought ({self.rsi[0]:.1f})')
                self.order = self.sell(size=self.position.size)
            
            # Exit 4: ATR trailing stop
            elif self.atr_stop and self.dataclose[0] < self.atr_stop:
                self.log(f'🛑 SELL: ATR stop hit')
                self.order = self.sell(size=self.position.size)
            
            # Update trailing stop (move up only)
            else:
                new_stop = self.dataclose[0] - (self.atr[0] * self.params.atr_stop_multiplier)
                if new_stop > self.atr_stop:
                    self.atr_stop = new_stop
                    self.log(f'📊 Trail stop updated: ${self.atr_stop:.2f}')
    
    def stop(self):
        """Final stats"""
        total_trades = self.wins + self.losses
        win_rate = (self.wins / total_trades * 100) if total_trades > 0 else 0
        final_value = self.broker.getvalue()
        
        print('\n' + '='*70)
        print(f'📊 MULTI-INDICATOR STRATEGY RESULTS')
        print('='*70)
        print(f'Final Value: ${final_value:,.2f}')
        print(f'Total Trades: {total_trades}')
        print(f'Win Rate: {win_rate:.1f}% ({self.wins}W / {self.losses}L)')
        print('='*70 + '\n')


if __name__ == '__main__':
    print("\n💡 Advanced Multi-Indicator Strategy")
    print("   Uses: 200 SMA + 50 SMA + MACD + RSI + Volume + ATR")
    print("\nRun with: python comprehensive_backtest.py\n")
