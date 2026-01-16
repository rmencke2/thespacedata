"""
Enhanced 200 SMA Strategy with RSI and Volume Filters
Improves the basic 200 SMA by adding confirmation filters
"""
import backtrader as bt

class SMA200Enhanced(bt.Strategy):
    """
    Enhanced 200 SMA with RSI and Volume confirmation
    
    BUY Rules:
    1. Price crosses above 200 SMA (trend)
    2. RSI < 70 (not overbought)
    3. Volume > 20-day average (confirmation)
    
    SELL Rules:
    1. Price crosses below 200 SMA (trend reversal)
    OR
    2. Stop loss hit (2%)
    OR
    3. Take profit hit (6%)
    """
    
    params = dict(
        sma_period=200,
        rsi_period=14,
        rsi_overbought=70,
        rsi_oversold=30,
        volume_period=20,
        volume_factor=1.0,  # Require volume >= average
        stop_loss_pct=0.02,
        take_profit_pct=0.06,
        position_size=0.95,
        debug=False,
    )
    
    def __init__(self):
        """Initialize indicators"""
        
        self.dataclose = self.datas[0].close
        
        # 200 SMA for trend
        self.sma200 = bt.indicators.SimpleMovingAverage(
            self.datas[0],
            period=self.params.sma_period
        )
        
        # RSI for overbought/oversold
        self.rsi = bt.indicators.RSI(
            self.datas[0],
            period=self.params.rsi_period
        )
        
        # Volume indicators
        self.volume = self.datas[0].volume
        self.volume_sma = bt.indicators.SimpleMovingAverage(
            self.volume,
            period=self.params.volume_period
        )
        
        # Track orders
        self.order = None
        self.buyprice = None
        self.stop_loss = None
        self.take_profit = None
        
        # Performance tracking
        self.trades_count = 0
        self.wins = 0
        self.losses = 0
        
    def log(self, txt, dt=None):
        """Logging"""
        if self.params.debug:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()} {txt}')
    
    def notify_order(self, order):
        """Handle order notifications"""
        if order.status in [order.Submitted, order.Accepted]:
            return
        
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'✅ BUY EXECUTED: ${order.executed.price:.2f}')
                self.buyprice = order.executed.price
                self.stop_loss = self.buyprice * (1 - self.params.stop_loss_pct)
                self.take_profit = self.buyprice * (1 + self.params.take_profit_pct)
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
                
                self.log(f'💰 SELL EXECUTED: ${order.executed.price:.2f}')
        
        self.order = None
    
    def next(self):
        """Main strategy logic"""
        
        # Log current state
        self.log(
            f'Close: ${self.dataclose[0]:.2f} | '
            f'SMA200: ${self.sma200[0]:.2f} | '
            f'RSI: {self.rsi[0]:.1f} | '
            f'Vol: {self.volume[0]:.0f} (Avg: {self.volume_sma[0]:.0f})'
        )
        
        # Don't trade if we have pending orders
        if self.order:
            return
        
        if not self.position:
            # === BUY LOGIC ===
            
            # Check trend: Price crosses above 200 SMA
            if self.dataclose[0] > self.sma200[0] and self.dataclose[-1] <= self.sma200[-1]:
                
                # Filter 1: RSI not overbought
                if self.rsi[0] >= self.params.rsi_overbought:
                    self.log(f'⚠️  BUY REJECTED: RSI too high ({self.rsi[0]:.1f})')
                    return
                
                # Filter 2: Volume confirmation
                if self.volume[0] < self.volume_sma[0] * self.params.volume_factor:
                    self.log(f'⚠️  BUY REJECTED: Volume too low ({self.volume[0]:.0f} < {self.volume_sma[0]:.0f})')
                    return
                
                # All filters passed!
                self.log(f'🚀 BUY SIGNAL: Price above SMA, RSI={self.rsi[0]:.1f}, Volume OK')
                
                # Calculate position size
                cash = self.broker.getcash()
                size = int((cash * self.params.position_size) / self.dataclose[0])
                
                self.order = self.buy(size=max(size, 1))
        
        else:
            # === SELL LOGIC ===
            
            # Exit 1: Price crosses below 200 SMA
            if self.dataclose[0] < self.sma200[0] and self.dataclose[-1] >= self.sma200[-1]:
                self.log(f'📉 SELL SIGNAL: Price below SMA200')
                self.order = self.sell(size=self.position.size)
            
            # Exit 2: Stop loss
            elif self.stop_loss and self.dataclose[0] < self.stop_loss:
                self.log(f'🛑 STOP LOSS: ${self.dataclose[0]:.2f} < ${self.stop_loss:.2f}')
                self.order = self.sell(size=self.position.size)
            
            # Exit 3: Take profit
            elif self.take_profit and self.dataclose[0] > self.take_profit:
                self.log(f'💎 TAKE PROFIT: ${self.dataclose[0]:.2f} > ${self.take_profit:.2f}')
                self.order = self.sell(size=self.position.size)
    
    def stop(self):
        """Called at end - print stats"""
        total_trades = self.wins + self.losses
        win_rate = (self.wins / total_trades * 100) if total_trades > 0 else 0
        final_value = self.broker.getvalue()
        
        print('\n' + '='*70)
        print(f'📊 ENHANCED STRATEGY RESULTS')
        print('='*70)
        print(f'Final Value: ${final_value:,.2f}')
        print(f'Total Trades: {total_trades}')
        print(f'Win Rate: {win_rate:.1f}% ({self.wins}W / {self.losses}L)')
        print('='*70 + '\n')


if __name__ == '__main__':
    print("\n💡 Enhanced 200 SMA Strategy")
    print("   Adds: RSI filter + Volume confirmation")
    print("\nRun with: python comprehensive_backtest.py\n")
