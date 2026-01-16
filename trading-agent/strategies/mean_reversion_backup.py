"""
Mean Reversion Trading Strategy
Buy when price drops below moving average, sell when it rises above
"""
import pandas as pd
import numpy as np
from typing import Dict, Optional
from utils.config import Config

class MeanReversionStrategy:
    """
    Mean reversion strategy:
    - Buy when price is N standard deviations below moving average
    - Sell when price returns to moving average
    - Short when price is N standard deviations above moving average
    """
    
    def __init__(
        self,
        period: int = None,
        std_dev: float = None
    ):
        self.period = period or Config.MEAN_REVERSION_PERIOD
        self.std_dev = std_dev or Config.MEAN_REVERSION_STD
        self.name = "mean_reversion"
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators"""
        df = df.copy()
        
        # Moving average
        df['sma'] = df['close'].rolling(window=self.period).mean()
        
        # Standard deviation
        df['std'] = df['close'].rolling(window=self.period).std()
        
        # Bollinger Bands
        df['upper_band'] = df['sma'] + (self.std_dev * df['std'])
        df['lower_band'] = df['sma'] - (self.std_dev * df['std'])
        
        # Distance from mean (in standard deviations)
        df['z_score'] = (df['close'] - df['sma']) / df['std']
        
        return df
    
    def generate_signal(self, df: pd.DataFrame) -> Dict:
        """
        Generate trading signal
        
        Returns:
            Dict with 'action', 'signal_strength', 'reason'
        """
        df = self.calculate_indicators(df)
        
        if len(df) < self.period + 1:
            return {
                'action': 'hold',
                'signal_strength': 0,
                'reason': 'Insufficient data'
            }
        
        # ADD THIS AFTER GENERATING SIGNAL
        if signal['action'] != 'HOLD':
            # Require above-average volume
            avg_volume = df['volume'].tail(20).mean()
            current_volume = df['volume'].iloc[-1]
    
        if current_volume < avg_volume * 0.8:  # Less than 80% of average
            signal['action'] = 'HOLD'
            signal['reason'] = 'Insufficient volume' 

        latest = df.iloc[-1]
        previous = df.iloc[-2]
        
        # Buy signal: price crossed below lower band
        if (latest['close'] < latest['lower_band'] and 
            previous['close'] >= previous['lower_band']):
            return {
                'action': 'buy',
                'signal_strength': abs(latest['z_score']) / self.std_dev,
                'reason': f"Price ${latest['close']:.2f} crossed below lower band ${latest['lower_band']:.2f}",
                'entry_price': latest['close'],
                'target_price': latest['sma'],
                'stop_loss': latest['close'] * (1 - Config.STOP_LOSS_PERCENT)
            }
        
        # Sell signal: price crossed above upper band
        elif (latest['close'] > latest['upper_band'] and 
              previous['close'] <= previous['upper_band']):
            return {
                'action': 'sell',  # Can be short or close long
                'signal_strength': abs(latest['z_score']) / self.std_dev,
                'reason': f"Price ${latest['close']:.2f} crossed above upper band ${latest['upper_band']:.2f}",
                'entry_price': latest['close'],
                'target_price': latest['sma'],
                'stop_loss': latest['close'] * (1 + Config.STOP_LOSS_PERCENT)
            }
        
        # Exit signal: price returned to mean
        elif abs(latest['z_score']) < 0.5:
            return {
                'action': 'close',
                'signal_strength': 1.0,
                'reason': f"Price ${latest['close']:.2f} returned to mean ${latest['sma']:.2f}",
            }
        
        else:
            return {
                'action': 'hold',
                'signal_strength': 0,
                'reason': f"No clear signal. Z-score: {latest['z_score']:.2f}",
                'current_price': latest['close'],
                'sma': latest['sma'],
                'z_score': latest['z_score']
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
        
        for i in range(self.period + 1, len(df)):
            current = df.iloc[i]
            previous = df.iloc[i-1]
            
            # Entry signals
            if position == 0:
                # Buy signal
                if (current['close'] < current['lower_band'] and 
                    previous['close'] >= previous['lower_band']):
                    position = 1
                    entry_price = current['close']
                    trades.append({
                        'entry_date': df.index[i],
                        'entry_price': entry_price,
                        'type': 'long'
                    })
                
                # Short signal
                elif (current['close'] > current['upper_band'] and 
                      previous['close'] <= previous['upper_band']):
                    position = -1
                    entry_price = current['close']
                    trades.append({
                        'entry_date': df.index[i],
                        'entry_price': entry_price,
                        'type': 'short'
                    })
            
            # Exit signals
            elif position != 0:
                # Exit when price returns to mean
                if abs(current['z_score']) < 0.5:
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
                        'pnl_percent': pnl_percent
                    })
                    position = 0
                
                # Stop loss
                elif position == 1 and current['close'] < entry_price * (1 - Config.STOP_LOSS_PERCENT):
                    pnl = current['close'] - entry_price
                    pnl_percent = (pnl / entry_price) * 100
                    capital += pnl
                    trades[-1].update({
                        'exit_date': df.index[i],
                        'exit_price': current['close'],
                        'pnl': pnl,
                        'pnl_percent': pnl_percent,
                        'exit_reason': 'stop_loss'
                    })
                    position = 0
                
                elif position == -1 and current['close'] > entry_price * (1 + Config.STOP_LOSS_PERCENT):
                    pnl = entry_price - current['close']
                    pnl_percent = (pnl / entry_price) * 100
                    capital += pnl
                    trades[-1].update({
                        'exit_date': df.index[i],
                        'exit_price': current['close'],
                        'pnl': pnl,
                        'pnl_percent': pnl_percent,
                        'exit_reason': 'stop_loss'
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
    
    print("\n📊 Testing Mean Reversion Strategy...\n")
    
    fetcher = DataFetcher()
    data = fetcher.get_historical_data(
        ['TSLA'],
        '2023-01-01',
        '2024-12-31'
    )
    
    if 'TSLA' in data:
        strategy = MeanReversionStrategy()
        
        # Test signal generation
        signal = strategy.generate_signal(data['TSLA'])
        print(f"Current Signal: {signal['action'].upper()}")
        print(f"Reason: {signal['reason']}")
        print(f"Signal Strength: {signal['signal_strength']:.2f}\n")
        
        # Backtest
        results = strategy.backtest(data['TSLA'])
        print("\n📈 Backtest Results:")
        print(f"Total Trades: {results['total_trades']}")
        print(f"Win Rate: {results['win_rate']:.2f}%")
        print(f"Total Return: ${results['total_return']:.2f} ({results['total_return_percent']:.2f}%)")
        print(f"Average Win: ${results['avg_win']:.2f}")
        print(f"Average Loss: ${results['avg_loss']:.2f}")
