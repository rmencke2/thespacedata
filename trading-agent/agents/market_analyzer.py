"""
Market Analyzer Agent
Analyzes market conditions and provides context for trading decisions
"""
from typing import Dict, List
import pandas as pd
from utils.data_fetcher import DataFetcher
from utils.config import Config

class MarketAnalyzerAgent:
    """
    Analyzes market conditions:
    - Current price and trends
    - Volatility assessment
    - Volume analysis
    - Market regime detection
    """
    
    def __init__(self):
        self.data_fetcher = DataFetcher()
        self.name = "market_analyzer"
    
    def analyze_symbol(self, symbol: str, df: pd.DataFrame) -> Dict:
        """
        Analyze a single symbol
        
        Returns:
            Dict with market analysis
        """
        if df.empty or len(df) < 20:
            return {
                'symbol': symbol,
                'status': 'insufficient_data',
                'message': 'Not enough historical data'
            }
        
        latest = df.iloc[-1]
        
        # Calculate metrics
        returns = df['close'].pct_change()
        volatility = returns.rolling(window=20).std().iloc[-1] * 100
        
        # Volume analysis
        avg_volume = df['volume'].tail(20).mean()
        volume_ratio = latest['volume'] / avg_volume if avg_volume > 0 else 1.0
        
        # Price trend
        sma_20 = df['close'].rolling(window=20).mean().iloc[-1]
        sma_50 = df['close'].rolling(window=50).mean().iloc[-1] if len(df) >= 50 else sma_20
        
        price_vs_sma20 = ((latest['close'] - sma_20) / sma_20) * 100
        
        # Determine market regime
        if volatility > 3:
            regime = 'high_volatility'
        elif volatility > 1.5:
            regime = 'medium_volatility'
        else:
            regime = 'low_volatility'
        
        # Trend direction
        if latest['close'] > sma_20 and sma_20 > sma_50:
            trend = 'uptrend'
        elif latest['close'] < sma_20 and sma_20 < sma_50:
            trend = 'downtrend'
        else:
            trend = 'sideways'
        
        # Trading recommendation
        if volatility > 3:
            recommendation = 'high_risk'
        elif volume_ratio > 1.5:
            recommendation = 'active_trading'
        else:
            recommendation = 'normal_trading'
        
        return {
            'symbol': symbol,
            'status': 'analyzed',
            'price': latest['close'],
            'volume': latest['volume'],
            'volume_ratio': volume_ratio,
            'volatility': volatility,
            'regime': regime,
            'trend': trend,
            'price_vs_sma20': price_vs_sma20,
            'sma_20': sma_20,
            'sma_50': sma_50,
            'recommendation': recommendation,
            'daily_return': returns.iloc[-1] * 100 if len(returns) > 0 else 0
        }
    
    def analyze_market(self, symbols: List[str] = None) -> Dict:
        """
        Analyze market conditions for multiple symbols
        
        Returns:
            Dict with overall market analysis
        """
        symbols = symbols or Config.STOCK_UNIVERSE
        
        print(f"\n🔍 Analyzing market for {len(symbols)} symbols...")
        
        # Get recent data
        data = self.data_fetcher.get_latest_bars(symbols, days=60)
        
        analyses = {}
        for symbol, df in data.items():
            analyses[symbol] = self.analyze_symbol(symbol, df)
        
        # Overall market assessment
        valid_analyses = [a for a in analyses.values() if a['status'] == 'analyzed']
        
        if not valid_analyses:
            return {
                'status': 'no_data',
                'message': 'Could not analyze any symbols',
                'timestamp': pd.Timestamp.now().isoformat()
            }
        
        avg_volatility = sum(a['volatility'] for a in valid_analyses) / len(valid_analyses)
        uptrend_count = sum(1 for a in valid_analyses if a['trend'] == 'uptrend')
        downtrend_count = sum(1 for a in valid_analyses if a['trend'] == 'downtrend')
        
        # Market sentiment
        if uptrend_count > len(valid_analyses) * 0.6:
            market_sentiment = 'bullish'
        elif downtrend_count > len(valid_analyses) * 0.6:
            market_sentiment = 'bearish'
        else:
            market_sentiment = 'neutral'
        
        return {
            'status': 'complete',
            'timestamp': pd.Timestamp.now().isoformat(),
            'symbols_analyzed': len(valid_analyses),
            'market_sentiment': market_sentiment,
            'avg_volatility': avg_volatility,
            'uptrend_count': uptrend_count,
            'downtrend_count': downtrend_count,
            'symbol_analyses': analyses,
            'recommendation': self._get_market_recommendation(
                market_sentiment,
                avg_volatility,
                valid_analyses
            )
        }
    
    def _get_market_recommendation(
        self,
        sentiment: str,
        volatility: float,
        analyses: List[Dict]
    ) -> str:
        """Generate overall market recommendation"""
        if volatility > 3:
            return "High volatility detected. Trade with caution, reduce position sizes."
        elif sentiment == 'bullish':
            return "Bullish market conditions. Look for long opportunities."
        elif sentiment == 'bearish':
            return "Bearish market conditions. Look for short opportunities or stay defensive."
        else:
            return "Neutral market. Focus on mean reversion strategies."
    
    def print_analysis(self, analysis: Dict):
        """Pretty print market analysis"""
        if analysis['status'] != 'complete':
            print(f"⚠️  {analysis.get('message', 'Analysis incomplete')}")
            return
        
        print("\n" + "="*70)
        print("MARKET ANALYSIS REPORT")
        print("="*70)
        print(f"Timestamp: {analysis['timestamp']}")
        print(f"Symbols Analyzed: {analysis['symbols_analyzed']}")
        print(f"Market Sentiment: {analysis['market_sentiment'].upper()}")
        print(f"Average Volatility: {analysis['avg_volatility']:.2f}%")
        print(f"Uptrend: {analysis['uptrend_count']} | Downtrend: {analysis['downtrend_count']}")
        print(f"\n💡 Recommendation: {analysis['recommendation']}")
        print("="*70)
        
        print("\nINDIVIDUAL STOCK ANALYSIS:")
        print("-"*70)
        
        for symbol, data in analysis['symbol_analyses'].items():
            if data['status'] == 'analyzed':
                print(f"\n{symbol}:")
                print(f"  Price: ${data['price']:.2f}")
                print(f"  Trend: {data['trend']}")
                print(f"  Volatility: {data['volatility']:.2f}%")
                print(f"  Volume Ratio: {data['volume_ratio']:.2f}x")
                print(f"  vs 20-day MA: {data['price_vs_sma20']:+.2f}%")
        
        print("-"*70 + "\n")


if __name__ == "__main__":
    # Test the market analyzer
    analyzer = MarketAnalyzerAgent()
    
    # Analyze market
    analysis = analyzer.analyze_market()
    analyzer.print_analysis(analysis)
