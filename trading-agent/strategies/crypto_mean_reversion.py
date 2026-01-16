"""
Crypto-Optimized Mean Reversion Strategy
Designed specifically for cryptocurrency markets (24/7, high volatility)

Key differences from stock strategy:
- Wider thresholds (crypto swings more)
- Flash crash detection (buy the dip opportunities)
- Extreme RSI levels (crypto gets more extreme)
- Volume spike detection (whales moving)
- 24/7 awareness (no market close)
"""
import pandas as pd
import numpy as np
from typing import Dict, List

class CryptoMeanReversionStrategy:
    """
    Mean Reversion Strategy Optimized for Crypto Markets
    
    Crypto-specific features:
    - Flash crash detection (15%+ drops in 24h)
    - Extreme volatility handling (wider bands)
    - Volume spike detection (whale activity)
    - Weekend pattern awareness
    - 24/7 market consideration
    """
    
    def __init__(self, period: int = 20, std_dev: float = 1.5):
        """
        Initialize crypto mean reversion strategy
        
        Args:
            period: Moving average period (default 20)
            std_dev: Standard deviations for entry (default 1.5, higher for crypto)
        """
        self.period = period
        self.std_dev = std_dev
        self.name = "crypto_mean_reversion"
    
    def calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def detect_flash_crash(self, df: pd.DataFrame, lookback: int = 24) -> Dict:
        """
        Detect flash crash opportunities in crypto
        
        Flash crash = 15%+ drop in 24 hours with volume spike
        These often bounce back quickly in crypto
        
        Returns:
            Dict with flash_crash bool and details
        """
        if len(df) < lookback:
            return {'flash_crash': False}
        
        current_price = df['close'].iloc[-1]
        recent_high = df['high'].tail(lookback).max()
        
        # Calculate drop percentage
        drop_percent = (recent_high - current_price) / recent_high
        
        # Check volume spike
        avg_volume = df['volume'].tail(lookback * 3).mean()
        recent_volume = df['volume'].tail(lookback).mean()
        volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 0
        
        # Flash crash criteria for crypto
        if drop_percent > 0.15 and volume_ratio > 1.5:  # 15% drop + 50% volume spike
            return {
                'flash_crash': True,
                'drop_percent': drop_percent,
                'volume_ratio': volume_ratio,
                'severity': 'EXTREME' if drop_percent > 0.25 else 'HIGH'
            }
        elif drop_percent > 0.10 and volume_ratio > 1.3:  # 10% drop
            return {
                'flash_crash': True,
                'drop_percent': drop_percent,
                'volume_ratio': volume_ratio,
                'severity': 'MODERATE'
            }
        
        return {'flash_crash': False}
    
    def check_volume_spike(self, df: pd.DataFrame) -> bool:
        """
        Check for volume spike (whale activity)
        Crypto-specific: larger volume spikes are common
        """
        if len(df) < 20:
            return True
        
        avg_volume = df['volume'].tail(48).mean()  # 48 hours for crypto
        current_volume = df['volume'].iloc[-1]
        
        # Require higher volume in crypto (1.5x vs 0.8x for stocks)
        return current_volume >= (avg_volume * 1.5)
    
    def calculate_confidence(self, 
                           z_score: float, 
                           rsi: float, 
                           volume_spike: bool, 
                           flash_crash: Dict,
                           action: str) -> float:
        """
        Calculate confidence score for crypto signals (0.0 to 1.0)
        Crypto gets bonus confidence for extreme conditions
        """
        confidence = 0.0
        
        # Factor 1: Z-score magnitude (0.3 points, higher weight for crypto)
        if abs(z_score) > 3.0:  # Extreme for crypto
            confidence += 0.3
        elif abs(z_score) > 2.0:
            confidence += 0.2
        elif abs(z_score) > 1.5:
            confidence += 0.1
        
        # Factor 2: RSI extremes (0.25 points, more extreme for crypto)
        if action == 'LONG':
            if rsi < 20:  # Extremely oversold (crypto level)
                confidence += 0.25
            elif rsi < 30:
                confidence += 0.15
        elif action == 'SHORT':
            if rsi > 80:  # Extremely overbought (crypto level)
                confidence += 0.25
            elif rsi > 70:
                confidence += 0.15
        
        # Factor 3: Volume spike (0.2 points, critical for crypto)
        if volume_spike:
            confidence += 0.2
        
        # Factor 4: Flash crash bonus (0.25 points, crypto-specific)
        if flash_crash.get('flash_crash') and action == 'LONG':
            severity = flash_crash.get('severity', 'MODERATE')
            if severity == 'EXTREME':
                confidence += 0.25
            elif severity == 'HIGH':
                confidence += 0.20
            elif severity == 'MODERATE':
                confidence += 0.15
        
        return max(0.0, min(1.0, confidence))
    
    def generate_signal(self, symbol: str, df: pd.DataFrame) -> Dict:
        """
        Generate trading signal optimized for crypto
        
        Returns:
            Dictionary with action, reason, confidence, and metrics
        """
        if len(df) < self.period + 24:  # Need 24+ hours of data
            return {
                'action': 'HOLD',
                'reason': 'Insufficient data',
                'confidence': 0.0
            }
        
        try:
            # Calculate indicators
            ma = df['close'].rolling(window=self.period).mean()
            std = df['close'].rolling(window=self.period).std()
            
            current_price = df['close'].iloc[-1]
            current_ma = ma.iloc[-1]
            current_std = std.iloc[-1]
            
            # Calculate z-score
            z_score = (current_price - current_ma) / current_std if current_std > 0 else 0
            
            # Calculate RSI (crypto uses extreme levels)
            rsi = self.calculate_rsi(df).iloc[-1]
            
            # Check for flash crash
            flash_crash = self.detect_flash_crash(df)
            
            # Check volume spike
            volume_spike = self.check_volume_spike(df)
            
            # Determine action
            action = 'HOLD'
            reason = ''
            
            # PRIORITY 1: Flash crash = BUY (crypto-specific)
            if flash_crash.get('flash_crash'):
                action = 'LONG'
                severity = flash_crash.get('severity', 'MODERATE')
                drop = flash_crash.get('drop_percent', 0) * 100
                reason = f'Flash crash detected: {severity} ({drop:.1f}% drop)'
                
                # Still check RSI isn't TOO high
                if rsi > 60:
                    action = 'HOLD'
                    reason = f'Flash crash but RSI too high ({rsi:.1f})'
            
            # PRIORITY 2: Extreme oversold (crypto = RSI < 25)
            elif z_score < -self.std_dev and rsi < 25:
                action = 'LONG'
                reason = f'Extreme oversold: {abs(z_score):.2f} std devs, RSI {rsi:.1f}'
                
                # Volume confirmation critical for crypto
                if not volume_spike:
                    action = 'HOLD'
                    reason = 'Oversold but low volume'
            
            # Standard oversold (RSI < 35 for crypto)
            elif z_score < -self.std_dev and rsi < 35:
                action = 'LONG'
                reason = f'Oversold: {abs(z_score):.2f} std devs below MA'
                
                if not volume_spike:
                    # Lower confidence but don't reject completely
                    reason += ' (low volume warning)'
            
            # Extreme overbought (crypto = RSI > 75)
            elif z_score > self.std_dev and rsi > 75:
                action = 'SHORT'
                reason = f'Extreme overbought: {z_score:.2f} std devs, RSI {rsi:.1f}'
                
                if not volume_spike:
                    action = 'HOLD'
                    reason = 'Overbought but low volume'
            
            # Standard overbought (RSI > 65 for crypto)
            elif z_score > self.std_dev and rsi > 65:
                action = 'SHORT'
                reason = f'Overbought: {z_score:.2f} std devs above MA'
                
                if not volume_spike:
                    reason += ' (low volume warning)'
            
            # Exit signal (tighter for crypto - 0.3 std)
            elif abs(z_score) < 0.3:
                action = 'CLOSE'
                reason = 'Price returned to mean'
            
            # Calculate confidence
            confidence = self.calculate_confidence(
                z_score, rsi, volume_spike, flash_crash, action
            )
            
            # Crypto requires higher minimum confidence (0.5 vs 0.4)
            if action in ['LONG', 'SHORT'] and confidence < 0.5:
                return {
                    'action': 'HOLD',
                    'reason': f'Low confidence ({confidence:.2f})',
                    'confidence': confidence
                }
            
            return {
                'action': action,
                'reason': reason,
                'confidence': confidence,
                'metrics': {
                    'z_score': z_score,
                    'rsi': rsi,
                    'volume_spike': volume_spike,
                    'flash_crash': flash_crash,
                    'ma': current_ma,
                    'std': current_std,
                    'price': current_price
                }
            }
            
        except Exception as e:
            return {
                'action': 'HOLD',
                'reason': f'Error: {str(e)}',
                'confidence': 0.0
            }
    
    def generate_signals(self, data: Dict[str, pd.DataFrame]) -> List[Dict]:
        """Generate signals for multiple crypto pairs"""
        signals = []
        
        for symbol, df in data.items():
            signal = self.generate_signal(symbol, df)
            signal['symbol'] = symbol
            signal['strategy'] = self.name
            
            # Only return actionable signals
            if signal['action'] in ['LONG', 'SHORT', 'CLOSE']:
                signals.append(signal)
        
        # Sort by confidence (highest first)
        signals.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        return signals
    
    def backtest(self, df: pd.DataFrame, initial_capital: float = 10000) -> Dict:
        """Backtest the crypto strategy"""
        capital = initial_capital
        position = None
        trades = []
        
        for i in range(self.period + 24, len(df)):
            current_df = df.iloc[:i+1]
            signal = self.generate_signal("CRYPTO", current_df)
            
            current_price = df['close'].iloc[i]
            
            # Enter position
            if position is None and signal['action'] in ['LONG', 'SHORT']:
                position = {
                    'type': signal['action'],
                    'entry_price': current_price,
                    'entry_date': df.index[i],
                    'confidence': signal.get('confidence', 0)
                }
            
            # Exit position
            elif position is not None:
                should_exit = False
                exit_reason = ''
                
                if signal['action'] == 'CLOSE':
                    should_exit = True
                    exit_reason = 'Mean reversion complete'
                elif signal['action'] == 'LONG' and position['type'] == 'SHORT':
                    should_exit = True
                    exit_reason = 'Opposite signal'
                elif signal['action'] == 'SHORT' and position['type'] == 'LONG':
                    should_exit = True
                    exit_reason = 'Opposite signal'
                
                if should_exit:
                    if position['type'] == 'LONG':
                        pnl = current_price - position['entry_price']
                        pnl_pct = pnl / position['entry_price']
                    else:  # SHORT
                        pnl = position['entry_price'] - current_price
                        pnl_pct = pnl / position['entry_price']
                    
                    trades.append({
                        'type': position['type'],
                        'entry_price': position['entry_price'],
                        'exit_price': current_price,
                        'pnl': pnl,
                        'pnl_pct': pnl_pct,
                        'entry_date': position['entry_date'],
                        'exit_date': df.index[i],
                        'confidence': position['confidence'],
                        'exit_reason': exit_reason
                    })
                    
                    capital += pnl
                    position = None
        
        # Calculate metrics
        if not trades:
            return {
                'strategy': self.name,
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_return': 0,
                'total_return_pct': 0
            }
        
        winning_trades = [t for t in trades if t['pnl'] > 0]
        losing_trades = [t for t in trades if t['pnl'] <= 0]
        
        return {
            'strategy': self.name,
            'total_trades': len(trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': len(winning_trades) / len(trades) * 100,
            'total_return': capital - initial_capital,
            'total_return_pct': (capital - initial_capital) / initial_capital * 100,
            'avg_win': np.mean([t['pnl'] for t in winning_trades]) if winning_trades else 0,
            'avg_loss': np.mean([t['pnl'] for t in losing_trades]) if losing_trades else 0,
            'profit_factor': abs(sum(t['pnl'] for t in winning_trades) / sum(t['pnl'] for t in losing_trades)) if losing_trades else 0,
            'trades': trades
        }


if __name__ == "__main__":
    """Test the crypto-optimized strategy"""
    from utils.data_fetcher_crypto import DataFetcher
    
    print("\n" + "="*70)
    print("🪙 TESTING CRYPTO-OPTIMIZED MEAN REVERSION STRATEGY")
    print("="*70)
    
    fetcher = DataFetcher()
    strategy = CryptoMeanReversionStrategy(period=20, std_dev=1.5)
    
    # Test on crypto
    test_symbols = ['BTC/USD', 'ETH/USD']
    print(f"\nTesting on: {', '.join(test_symbols)}")
    print("\nFetching recent data...")
    
    data = fetcher.get_latest_bars(test_symbols, days=60)
    
    print("\nGenerating signals...")
    signals = strategy.generate_signals(data)
    
    if signals:
        print(f"\n✅ Found {len(signals)} signals:\n")
        for signal in signals:
            print(f"🪙 {signal['symbol']}: {signal['action']}")
            print(f"   Reason: {signal['reason']}")
            print(f"   Confidence: {signal['confidence']:.2%}")
            if 'metrics' in signal:
                metrics = signal['metrics']
                print(f"   Price: ${metrics['price']:,.2f}")
                print(f"   Z-Score: {metrics['z_score']:.2f}")
                print(f"   RSI: {metrics['rsi']:.1f}")
                print(f"   Volume Spike: {metrics['volume_spike']}")
                if metrics['flash_crash'].get('flash_crash'):
                    fc = metrics['flash_crash']
                    print(f"   🚨 FLASH CRASH: {fc['severity']} ({fc['drop_percent']*100:.1f}% drop)")
            print()
    else:
        print("\n⚠️  No signals generated")
        print("Market conditions not extreme enough for crypto strategy")
    
    print("="*70)
    print("\n💡 Crypto-Specific Features:")
    print("  🚨 Flash crash detection (15%+ drops)")
    print("  📊 Extreme RSI levels (20-80 vs 30-70)")
    print("  📈 Volume spike detection (whale activity)")
    print("  💪 Higher std dev threshold (1.5 vs 1.2)")
    print("  ⚡ Faster exits (0.3 std vs 0.5 std)")
    print("\n🎯 Expected: Higher volatility = More trades = Bigger swings!")
    print("="*70 + "\n")
