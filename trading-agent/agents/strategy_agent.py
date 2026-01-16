"""
Strategy Agent
Generates trading signals using multiple strategies
"""
from typing import Dict, List
import pandas as pd
from strategies.mean_reversion import MeanReversionStrategy
from strategies.momentum import MomentumStrategy
from utils.config import Config

class StrategyAgent:
    """
    Generates trading signals by combining multiple strategies:
    - Mean Reversion
    - Momentum
    - Combines signals with voting/weighting
    """
    
    def __init__(self):
        self.strategies = {
            'mean_reversion': MeanReversionStrategy(),
            'momentum': MomentumStrategy()
        }
        self.name = "strategy_agent"
    
    def generate_signals(self, symbol: str, df: pd.DataFrame, market_context: Dict = None) -> Dict:
        """
        Generate trading signals from all strategies
        
        Args:
            symbol: Stock symbol
            df: Price data
            market_context: Market analysis from MarketAnalyzerAgent
        
        Returns:
            Dict with combined signals and recommendations
        """
        if df.empty or len(df) < 50:
            return {
                'symbol': symbol,
                'status': 'insufficient_data',
                'signal': 'hold',
                'confidence': 0
            }
        
        # Get signals from each strategy
        signals = {}
        for strategy_name, strategy in self.strategies.items():
            # Mean reversion strategy requires symbol parameter
            if strategy_name == 'mean_reversion':
                signals[strategy_name] = strategy.generate_signal(symbol, df)
            else:
                signals[strategy_name] = strategy.generate_signal(df)
        
        # Combine signals
        combined = self._combine_signals(signals, market_context)
        
        return {
            'symbol': symbol,
            'status': 'complete',
            'signal': combined['action'],
            'confidence': combined['confidence'],
            'strategy_signals': signals,
            'reasoning': combined['reasoning'],
            'entry_price': combined.get('entry_price'),
            'stop_loss': combined.get('stop_loss'),
            'target_price': combined.get('target_price')
        }
    
    def _combine_signals(self, signals: Dict, market_context: Dict = None) -> Dict:
        """
        Combine signals from multiple strategies
        
        Uses a weighted voting system:
        - If strategies agree, high confidence
        - If strategies disagree, lower confidence or hold
        - Consider market context for weighting
        """
        # Normalize actions (mean reversion uses LONG/SHORT, momentum uses buy/sell)
        normalized_actions = []
        strengths = []
        
        for s in signals.values():
            action = s.get('action', 'hold').lower()
            # Normalize mean reversion actions
            if action == 'long':
                normalized_actions.append('buy')
            elif action == 'short':
                normalized_actions.append('sell')
            else:
                normalized_actions.append(action)
            
            # Get signal strength (different strategies use different keys)
            strength = s.get('signal_strength', s.get('confidence', 0))
            strengths.append(strength)
        
        actions = normalized_actions
        
        # Count votes
        buy_votes = actions.count('buy')
        sell_votes = actions.count('sell')
        close_votes = actions.count('close')
        hold_votes = actions.count('hold')
        
        total_strategies = len(actions)
        
        # Determine action
        if close_votes > 0:
            action = 'close'
            confidence = close_votes / total_strategies
            reasoning = "Multiple strategies suggest closing position"
        
        elif buy_votes > sell_votes and buy_votes > hold_votes:
            action = 'buy'
            confidence = buy_votes / total_strategies
            reasoning = f"{buy_votes}/{total_strategies} strategies suggest buying"
        
        elif sell_votes > buy_votes and sell_votes > hold_votes:
            action = 'sell'
            confidence = sell_votes / total_strategies
            reasoning = f"{sell_votes}/{total_strategies} strategies suggest selling"
        
        else:
            action = 'hold'
            confidence = 0
            reasoning = "No clear consensus from strategies"
        
        # Adjust confidence based on signal strengths
        if action in ['buy', 'sell']:
            avg_strength = sum(strengths) / len(strengths)
            confidence = confidence * avg_strength
        
        # Adjust based on market context
        if market_context and market_context.get('status') == 'complete':
            regime = market_context.get('regime', 'normal')
            if regime == 'high_volatility':
                confidence *= 0.7  # Reduce confidence in high volatility
                reasoning += " (reduced due to high volatility)"
        
        # Get additional details from strongest signal
        # Use signal_strength or confidence, whichever is available
        def get_strength(s):
            return s.get('signal_strength', s.get('confidence', 0))
        
        strongest_signal = max(signals.values(), key=get_strength)
        
        result = {
            'action': action,
            'confidence': confidence,
            'reasoning': reasoning
        }
        
        if action in ['buy', 'sell']:
            result.update({
                'entry_price': strongest_signal.get('entry_price'),
                'stop_loss': strongest_signal.get('stop_loss'),
                'target_price': strongest_signal.get('target_price')
            })
        
        return result
    
    def scan_universe(self, symbols: List[str], market_data: Dict, market_context: Dict = None) -> List[Dict]:
        """
        Scan entire trading universe for signals
        
        Args:
            symbols: List of symbols to scan
            market_data: Dict mapping symbol to DataFrame
            market_context: Market analysis
        
        Returns:
            List of trading opportunities sorted by confidence
        """
        opportunities = []
        
        for symbol in symbols:
            if symbol not in market_data:
                continue
            
            df = market_data[symbol]
            signals = self.generate_signals(symbol, df, market_context)
            
            if signals['signal'] in ['buy', 'sell'] and signals['confidence'] > 0.3:
                opportunities.append(signals)
        
        # Sort by confidence
        opportunities.sort(key=lambda x: x['confidence'], reverse=True)
        
        return opportunities
    
    def print_signals(self, signals: Dict):
        """Pretty print trading signals"""
        print("\n" + "="*70)
        print(f"TRADING SIGNALS: {signals['symbol']}")
        print("="*70)
        
        if signals['status'] != 'complete':
            print(f"⚠️  {signals.get('message', 'Signals not available')}")
            return
        
        print(f"📊 Overall Signal: {signals['signal'].upper()}")
        print(f"💪 Confidence: {signals['confidence']*100:.1f}%")
        print(f"💡 Reasoning: {signals['reasoning']}")
        
        if signals.get('entry_price'):
            print(f"\n💰 Entry Price: ${signals['entry_price']:.2f}")
            if signals.get('stop_loss'):
                print(f"🛑 Stop Loss: ${signals['stop_loss']:.2f}")
            if signals.get('target_price'):
                print(f"🎯 Target: ${signals['target_price']:.2f}")
        
        print("\n📈 Strategy Breakdown:")
        print("-"*70)
        for strategy_name, strategy_signal in signals['strategy_signals'].items():
            print(f"\n{strategy_name.replace('_', ' ').title()}:")
            print(f"  Action: {strategy_signal['action'].upper()}")
            print(f"  Strength: {strategy_signal['signal_strength']:.2f}")
            print(f"  Reason: {strategy_signal['reason']}")
        
        print("="*70 + "\n")
    
    def print_opportunities(self, opportunities: List[Dict]):
        """Print list of trading opportunities"""
        if not opportunities:
            print("\n⚠️  No trading opportunities found.\n")
            return
        
        print("\n" + "="*70)
        print(f"TRADING OPPORTUNITIES ({len(opportunities)} found)")
        print("="*70)
        
        for i, opp in enumerate(opportunities, 1):
            print(f"\n{i}. {opp['symbol']} - {opp['signal'].upper()}")
            print(f"   Confidence: {opp['confidence']*100:.1f}%")
            print(f"   Entry: ${opp.get('entry_price', 0):.2f}")
            print(f"   Reasoning: {opp['reasoning']}")
        
        print("="*70 + "\n")


if __name__ == "__main__":
    # Test the strategy agent
    from utils.data_fetcher import DataFetcher
    from agents.market_analyzer import MarketAnalyzerAgent
    
    print("\n🤖 Testing Strategy Agent...\n")
    
    # Get market data
    fetcher = DataFetcher()
    symbols = ['TSLA', 'NVDA']
    market_data = fetcher.get_latest_bars(symbols, days=60)
    
    # Get market context
    analyzer = MarketAnalyzerAgent()
    market_context = analyzer.analyze_market(symbols)
    
    # Generate signals
    agent = StrategyAgent()
    
    for symbol in symbols:
        if symbol in market_data:
            signals = agent.generate_signals(symbol, market_data[symbol], market_context)
            agent.print_signals(signals)
    
    # Scan for opportunities
    opportunities = agent.scan_universe(symbols, market_data, market_context)
    agent.print_opportunities(opportunities)
