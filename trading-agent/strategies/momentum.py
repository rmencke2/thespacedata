"""
Momentum Trading Strategy
Ride trends using moving average crossovers and RSI
"""
import pandas as pd
import numpy as np
from typing import Dict
from utils.config import Config

class MomentumStrategy:
    """
    Momentum strategy:
    - Buy when fast MA crosses above slow MA and RSI is not overbought
    - Sell when fast MA crosses below slow MA and RSI is not oversold
    - Use RSI for confirmation
    """
    
    def __init__(
        self,
        fast_period: int = None,
        slow_period: int = None,
        rsi_period: int = None
    ):
        self.fast_period = fast_period or Config.MOMENTUM_FAST_PERIOD
        self.slow_period = slow_period or Config.MOMENTUM_SLOW_PERIOD
        self.rsi_period = rsi_period or Config.MOMENTUM_RSI_PERIOD
        self.name = "momentum"
    
    def calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators"""
        df = df.copy()
        
        # Moving averages
        df['fast_ma'] = df['close'].rolling(window=self.fast_period).mean()
        df['slow_ma'] = df['close'].rolling(window=self.slow_period).mean()
        
        # RSI
        df['rsi'] = self.calculate_rsi(df, self.rsi_period)
        
        # Trend strength
        df['trend_strength'] = (df['fast_ma'] - df['slow_ma']) / df['slow_ma'] * 100
        
        return df
    
    def generate_signal(self, df: pd.DataFrame) -> Dict:
        """
        Generate trading signal
        
        Returns:
            Dict with 'action', 'signal_strength', 'reason'
        """
        df = self.calculate_indicators(df)
        
        if len(df) < self.slow_period + 1:
            return {
                'action': 'hold',
                'signal_strength': 0,
                'reason': 'Insufficient data'
            }
        
        latest = df.iloc[-1]
        previous = df.iloc[-2]
        
        # Buy signal: fast MA crosses above slow MA
        if (latest['fast_ma'] > latest['slow_ma'] and 
            previous['fast_ma'] <= previous['slow_ma'] and
            latest['rsi'] < Config.MOMENTUM_RSI_OVERBOUGHT):
            
            signal_strength = min(abs(latest['trend_strength']) / 5, 1.0)  # Normalize to 0-1
            
            return {
                'action': 'buy',
                'signal_strength': signal_strength,
                'reason': f"Bullish crossover. Fast MA: ${latest['fast_ma']:.2f}, Slow MA: ${latest['slow_ma']:.2f}, RSI: {latest['rsi']:.1f}",
                'entry_price': latest['close'],
                'stop_loss': latest['slow_ma'] * (1 - Config.STOP_LOSS_PERCENT),
                'rsi': latest['rsi'],
                'trend_strength': latest['trend_strength']
            }
        
        # Sell signal: fast MA crosses below slow MA
        elif (latest['fast_ma'] < latest['slow_ma'] and 
              previous['fast_ma'] >= previous['slow_ma'] and
              latest['rsi'] > Config.MOMENTUM_RSI_OVERSOLD):
            
            signal_strength = min(abs(latest['trend_strength']) / 5, 1.0)
            
            return {
                'action': 'sell',
                'signal_strength': signal_strength,
                'reason': f"Bearish crossover. Fast MA: ${latest['fast_ma']:.2f}, Slow MA: ${latest['slow_ma']:.2f}, RSI: {latest['rsi']:.1f}",
                'entry_price': latest['close'],
                'stop_loss': latest['slow_ma'] * (1 + Config.STOP_LOSS_PERCENT),
                'rsi': latest['rsi'],
                'trend_strength': latest['trend_strength']
            }
        
        # Close long position if trend weakens
        elif (latest['fast_ma'] < latest['slow_ma'] and 
              latest['rsi'] > 60):
            return {
                'action': 'close',
                'signal_strength': 0.8,
                'reason': f"Trend weakening. RSI: {latest['rsi']:.1f}"
            }
        
        # Continue holding
        else:
            action = 'hold'
            reason_parts = []
            
            if latest['fast_ma'] > latest['slow_ma']:
                reason_parts.append("In uptrend")
            else:
                reason_parts.append("In downtrend")
            
            if latest['rsi'] > Config.MOMENTUM_RSI_OVERBOUGHT:
                reason_parts.append("RSI overbought")
            elif latest['rsi'] < Config.MOMENTUM_RSI_OVERSOLD:
                reason_parts.append("RSI oversold")
            
            return {
                'action': action,
                'signal_strength': 0,
                'reason': ", ".join(reason_parts),
                'current_price': latest['close'],
                'fast_ma': latest['fast_ma'],
                'slow_ma': latest['slow_ma'],
                'rsi': latest['rsi'],
                'trend_strength': latest['trend_strength']
            }
    
    def backtest(self, df: pd.DataFrame, initial_capital: float = 10000) -> Dict:
        """
        Backtest the strategy
        
        Returns:
            Dict with performance metrics
        """
        df = self.calculate_indicators(df)
        
        capital = initial_capital
        position = 0  # 0 = no position, 1 = long, -1 = short
        entry_price = 0
        trades = []
        
        for i in range(self.slow_period + 1, len(df)):
            current = df.iloc[i]
            previous = df.iloc[i-1]
            
            # Entry signals
            if position == 0:
                # Buy signal
                if (current['fast_ma'] > current['slow_ma'] and 
                    previous['fast_ma'] <= previous['slow_ma'] and
                    current['rsi'] < Config.MOMENTUM_RSI_OVERBOUGHT):
                    position = 1
                    entry_price = current['close']
                    trades.append({
                        'entry_date': df.index[i],
                        'entry_price': entry_price,
                        'type': 'long',
                        'entry_rsi': current['rsi']
                    })
                
                # Short signal
                elif (current['fast_ma'] < current['slow_ma'] and 
                      previous['fast_ma'] >= previous['slow_ma'] and
                      current['rsi'] > Config.MOMENTUM_RSI_OVERSOLD):
                    position = -1
                    entry_price = current['close']
                    trades.append({
                        'entry_date': df.index[i],
                        'entry_price': entry_price,
                        'type': 'short',
                        'entry_rsi': current['rsi']
                    })
            
            # Exit signals
            elif position != 0:
                exit_signal = False
                exit_reason = 'signal'
                
                # Exit on opposite crossover
                if position == 1 and current['fast_ma'] < current['slow_ma']:
                    exit_signal = True
                elif position == -1 and current['fast_ma'] > current['slow_ma']:
                    exit_signal = True
                
                # Stop loss
                elif position == 1 and current['close'] < entry_price * (1 - Config.STOP_LOSS_PERCENT):
                    exit_signal = True
                    exit_reason = 'stop_loss'
                elif position == -1 and current['close'] > entry_price * (1 + Config.STOP_LOSS_PERCENT):
                    exit_signal = True
                    exit_reason = 'stop_loss'
                
                if exit_signal:
                    if position == 1:  # Close long
                        pnl = current['close'] - entry_price
                        pnl_percent = (pnl / entry_price) * 100
                    else:  # Close short
                        pnl = entry_price - current['close']
                        pnl_percent = (pnl / entry_price) * 100
                    
                    capital += pnl
                    trades[-1].update({
                        'exit_date': df.index[i],
                        'exit_price': current['close'],
                        'pnl': pnl,
                        'pnl_percent': pnl_percent,
                        'exit_reason': exit_reason,
                        'exit_rsi': current['rsi']
                    })
                    position = 0
        
        # Calculate metrics
        closed_trades = [t for t in trades if 'exit_price' in t]
        
        if not closed_trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_return': 0,
                'total_return_percent': 0
            }
        
        winning_trades = [t for t in closed_trades if t['pnl'] > 0]
        losing_trades = [t for t in closed_trades if t['pnl'] <= 0]
        
        return {
            'strategy': self.name,
            'total_trades': len(closed_trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': len(winning_trades) / len(closed_trades) * 100,
            'total_return': capital - initial_capital,
            'total_return_percent': ((capital - initial_capital) / initial_capital) * 100,
            'avg_win': np.mean([t['pnl'] for t in winning_trades]) if winning_trades else 0,
            'avg_loss': np.mean([t['pnl'] for t in losing_trades]) if losing_trades else 0,
            'trades': closed_trades
        }


if __name__ == "__main__":
    # Test the strategy
    from utils.data_fetcher import DataFetcher
    
    print("\n🚀 Testing Momentum Strategy...\n")
    
    fetcher = DataFetcher()
    data = fetcher.get_historical_data(
        ['NVDA'],
        '2023-01-01',
        '2024-12-31'
    )
    
    if 'NVDA' in data:
        strategy = MomentumStrategy()
        
        # Test signal generation
        signal = strategy.generate_signal(data['NVDA'])
        print(f"Current Signal: {signal['action'].upper()}")
        print(f"Reason: {signal['reason']}")
        print(f"Signal Strength: {signal['signal_strength']:.2f}\n")
        
        # Backtest
        results = strategy.backtest(data['NVDA'])
        print("\n📈 Backtest Results:")
        print(f"Total Trades: {results['total_trades']}")
        print(f"Win Rate: {results['win_rate']:.2f}%")
        print(f"Total Return: ${results['total_return']:.2f} ({results['total_return_percent']:.2f}%)")
        print(f"Average Win: ${results['avg_win']:.2f}")
        print(f"Average Loss: ${results['avg_loss']:.2f}")
