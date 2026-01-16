"""
200 SMA Trend Following Strategy - Backtrader Implementation
Professional trading strategy for trending markets

Strategy Rules:
- BUY when price crosses ABOVE 200 SMA (uptrend confirmation)
- SELL/EXIT when price crosses BELOW 200 SMA (downtrend)
- Position sizing based on account risk
- Stop loss and take profit targets
"""
import backtrader as bt
import datetime
from typing import Dict, Any

class SMA200Strategy(bt.Strategy):
    """
    200 SMA Trend Following Strategy
    
    Classic institutional strategy - price above 200 SMA = uptrend
    """
    
    params = dict(
        sma_period=200,           # 200-period SMA
        risk_per_trade=0.02,      # 2% risk per trade
        stop_loss_pct=0.02,       # 2% stop loss
        take_profit_pct=0.06,     # 6% take profit (3:1 reward:risk)
        position_size=0.95,       # Use 95% of available capital per position
        debug=False,              # Print debug info
    )
    
    def __init__(self):
        """Initialize strategy components"""
        
        # Keep reference to close price
        self.dataclose = self.datas[0].close
        
        # Create 200 SMA indicator
        self.sma200 = bt.indicators.SimpleMovingAverage(
            self.datas[0],
            period=self.params.sma_period
        )
        
        # Track orders and positions
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.stop_loss = None
        self.take_profit = None
        
        # Performance tracking
        self.trades_count = 0
        self.wins = 0
        self.losses = 0
        
    def log(self, txt, dt=None):
        """Logging function"""
        if self.params.debug:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()} {txt}')
    
    def notify_order(self, order):
        """Handle order notifications"""
        if order.status in [order.Submitted, order.Accepted]:
            return
        
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    f'BUY EXECUTED, Price: {order.executed.price:.2f}, '
                    f'Cost: {order.executed.value:.2f}, '
                    f'Comm: {order.executed.comm:.2f}'
                )
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
                
                # Set stop loss and take profit
                self.stop_loss = self.buyprice * (1 - self.params.stop_loss_pct)
                self.take_profit = self.buyprice * (1 + self.params.take_profit_pct)
                
            else:  # Sell
                self.log(
                    f'SELL EXECUTED, Price: {order.executed.price:.2f}, '
                    f'Cost: {order.executed.value:.2f}, '
                    f'Comm: {order.executed.comm:.2f}'
                )
                
                # Calculate profit/loss
                if self.buyprice:
                    pnl = order.executed.price - self.buyprice
                    pnl_pct = (pnl / self.buyprice) * 100
                    
                    if pnl > 0:
                        self.wins += 1
                    else:
                        self.losses += 1
                    
                    self.trades_count += 1
                    
                    self.log(
                        f'TRADE #{self.trades_count} CLOSED, '
                        f'P&L: ${pnl:.2f} ({pnl_pct:+.2f}%)'
                    )
            
            self.bar_executed = len(self)
            
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        
        self.order = None
    
    def notify_trade(self, trade):
        """Handle trade notifications"""
        if not trade.isclosed:
            return
        
        self.log(f'TRADE PROFIT, Gross: ${trade.pnl:.2f}, Net: ${trade.pnlcomm:.2f}')
    
    def next(self):
        """Main strategy logic - called on each bar"""
        
        # Log current state
        self.log(f'Close: {self.dataclose[0]:.2f}, SMA200: {self.sma200[0]:.2f}')
        
        # Don't trade if we have pending orders
        if self.order:
            return
        
        # Check if we have a position
        if not self.position:
            
            # BUY SIGNAL: Price crosses above 200 SMA
            if self.dataclose[0] > self.sma200[0] and self.dataclose[-1] <= self.sma200[-1]:
                
                self.log(f'BUY SIGNAL - Price crossed above SMA200')
                
                # Calculate position size
                size = self.calculate_position_size()
                
                # Place buy order
                self.order = self.buy(size=size)
                self.log(f'BUY ORDER PLACED, Size: {size}')
        
        else:
            # We have a position - check exit conditions
            
            # Exit Condition 1: Price crosses below 200 SMA (trend reversal)
            if self.dataclose[0] < self.sma200[0] and self.dataclose[-1] >= self.sma200[-1]:
                self.log(f'SELL SIGNAL - Price crossed below SMA200')
                self.order = self.sell(size=self.position.size)
                self.log(f'SELL ORDER PLACED')
            
            # Exit Condition 2: Stop loss hit
            elif self.stop_loss and self.dataclose[0] < self.stop_loss:
                self.log(f'STOP LOSS HIT at {self.dataclose[0]:.2f} (Stop: {self.stop_loss:.2f})')
                self.order = self.sell(size=self.position.size)
            
            # Exit Condition 3: Take profit hit
            elif self.take_profit and self.dataclose[0] > self.take_profit:
                self.log(f'TAKE PROFIT HIT at {self.dataclose[0]:.2f} (Target: {self.take_profit:.2f})')
                self.order = self.sell(size=self.position.size)
    
    def calculate_position_size(self) -> int:
        """
        Calculate position size based on available capital and risk
        
        Returns:
            Number of shares/units to buy
        """
        # Get available cash
        cash = self.broker.getcash()
        
        # Calculate position value (use 95% of available cash)
        position_value = cash * self.params.position_size
        
        # Calculate number of shares
        price = self.dataclose[0]
        size = int(position_value / price)
        
        return max(size, 1)  # At least 1 share
    
    def stop(self):
        """Called when backtest ends - print final stats"""
        
        # Calculate win rate
        total_trades = self.wins + self.losses
        win_rate = (self.wins / total_trades * 100) if total_trades > 0 else 0
        
        # Get final portfolio value
        final_value = self.broker.getvalue()
        
        print('\n' + '='*70)
        print(f'📊 STRATEGY RESULTS - SMA Period: {self.params.sma_period}')
        print('='*70)
        print(f'Final Portfolio Value: ${final_value:,.2f}')
        print(f'Total Trades: {total_trades}')
        print(f'Winning Trades: {self.wins}')
        print(f'Losing Trades: {self.losses}')
        print(f'Win Rate: {win_rate:.2f}%')
        print('='*70 + '\n')


class SMA200CrossStrategy(bt.Strategy):
    """
    Alternative: More aggressive crossover strategy
    BUY when fast SMA crosses above slow SMA
    """
    
    params = dict(
        fast_period=50,           # 50-period fast SMA
        slow_period=200,          # 200-period slow SMA
        risk_per_trade=0.02,
        stop_loss_pct=0.02,
        position_size=0.95,
        debug=False,
    )
    
    def __init__(self):
        self.dataclose = self.datas[0].close
        
        # Create SMAs
        self.sma_fast = bt.indicators.SimpleMovingAverage(
            self.datas[0],
            period=self.params.fast_period
        )
        self.sma_slow = bt.indicators.SimpleMovingAverage(
            self.datas[0],
            period=self.params.slow_period
        )
        
        # Crossover indicator
        self.crossover = bt.indicators.CrossOver(self.sma_fast, self.sma_slow)
        
        self.order = None
        self.trades_count = 0
        self.wins = 0
        self.losses = 0
    
    def log(self, txt, dt=None):
        if self.params.debug:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()} {txt}')
    
    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.buyprice = order.executed.price
                self.log(f'BUY EXECUTED: {self.buyprice:.2f}')
            else:
                if hasattr(self, 'buyprice'):
                    pnl = order.executed.price - self.buyprice
                    if pnl > 0:
                        self.wins += 1
                    else:
                        self.losses += 1
                    self.trades_count += 1
                self.log(f'SELL EXECUTED: {order.executed.price:.2f}')
        
        self.order = None
    
    def next(self):
        if self.order:
            return
        
        if not self.position:
            # BUY on golden cross (fast crosses above slow)
            if self.crossover > 0:
                cash = self.broker.getcash()
                size = int((cash * self.params.position_size) / self.dataclose[0])
                self.order = self.buy(size=max(size, 1))
                self.log('GOLDEN CROSS - BUY SIGNAL')
        
        else:
            # SELL on death cross (fast crosses below slow)
            if self.crossover < 0:
                self.order = self.sell(size=self.position.size)
                self.log('DEATH CROSS - SELL SIGNAL')
    
    def stop(self):
        total_trades = self.wins + self.losses
        win_rate = (self.wins / total_trades * 100) if total_trades > 0 else 0
        final_value = self.broker.getvalue()
        
        print('\n' + '='*70)
        print(f'📊 CROSSOVER STRATEGY RESULTS - {self.params.fast_period}/{self.params.slow_period} SMA')
        print('='*70)
        print(f'Final Portfolio Value: ${final_value:,.2f}')
        print(f'Total Trades: {total_trades}')
        print(f'Win Rate: {win_rate:.2f}%')
        print('='*70 + '\n')


if __name__ == '__main__':
    """Test the strategy with sample data"""
    print("\n💡 To test this strategy, run:")
    print("   python backtest_runner.py")
    print("\nThis will backtest the 200 SMA strategy on real historical data.\n")
