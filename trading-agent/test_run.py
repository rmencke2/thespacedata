#!/usr/bin/env python3
"""
Test run of the strategy agent to verify fixes work
"""
from agents.strategy_agent import StrategyAgent
from agents.market_analyzer import MarketAnalyzerAgent
from utils.data_fetcher import DataFetcher

print('\n' + '='*70)
print('TESTING STRATEGY AGENT WITH FIXES')
print('='*70 + '\n')

# Initialize agents
print('📦 Initializing agents...')
fetcher = DataFetcher()
analyzer = MarketAnalyzerAgent()
strategy_agent = StrategyAgent()
print('✅ Agents initialized\n')

# Test with a few symbols
test_symbols = ['TSLA', 'NVDA', 'AMD', 'MSFT']
print(f'📊 Testing symbols: {", ".join(test_symbols)}\n')

# Fetch market data
print('📥 Fetching market data (60 days)...')
try:
    market_data = fetcher.get_latest_bars(test_symbols, days=60)
    print(f'✅ Fetched data for {len(market_data)} symbols\n')
except Exception as e:
    print(f'❌ Error fetching data: {e}\n')
    exit(1)

# Get market context
print('🔍 Analyzing market conditions...')
try:
    market_context = analyzer.analyze_market(test_symbols)
    sentiment = market_context.get('market_sentiment', 'unknown')
    print(f'✅ Market sentiment: {sentiment}\n')
except Exception as e:
    print(f'⚠️  Error analyzing market: {e}')
    market_context = None
    print()

# Generate signals for each symbol
print('🎯 Generating trading signals...\n')
print('-'*70)
signals_generated = 0
for symbol in test_symbols:
    if symbol not in market_data:
        print(f'⚠️  {symbol}: No data available')
        continue
    
    try:
        signals = strategy_agent.generate_signals(symbol, market_data[symbol], market_context)
        signals_generated += 1
        
        print(f'\n📈 {symbol}:')
        print(f'   Signal: {signals["signal"].upper()}')
        print(f'   Confidence: {signals["confidence"]*100:.1f}%')
        print(f'   Status: {signals["status"]}')
        
        if signals['status'] == 'complete':
            print(f'   Reasoning: {signals["reasoning"]}')
            
            # Show individual strategy signals
            if 'strategy_signals' in signals:
                print(f'   Strategy breakdown:')
                for strat_name, strat_signal in signals['strategy_signals'].items():
                    action = strat_signal.get('action', 'hold')
                    strength = strat_signal.get('signal_strength', strat_signal.get('confidence', 0))
                    print(f'     - {strat_name}: {action.upper()} (strength: {strength:.2f})')
            
            if signals.get('entry_price'):
                print(f'   Entry Price: ${signals["entry_price"]:.2f}')
            if signals.get('stop_loss'):
                print(f'   Stop Loss: ${signals["stop_loss"]:.2f}')
        else:
            print(f'   ⚠️  {signals.get("message", "Insufficient data")}')
        
    except Exception as e:
        print(f'\n❌ {symbol}: Error generating signals - {e}')
        import traceback
        traceback.print_exc()

print('\n' + '-'*70)

# Scan for opportunities
print('\n🔍 Scanning for trading opportunities (confidence > 0.3)...')
print('-'*70)
try:
    opportunities = strategy_agent.scan_universe(test_symbols, market_data, market_context)
    print(f'\n✅ Found {len(opportunities)} trading opportunities\n')
    
    if opportunities:
        strategy_agent.print_opportunities(opportunities)
    else:
        print('⚠️  No trading opportunities found')
        print('   This is normal if:')
        print('   - Market conditions are sideways/neutral')
        print('   - Confidence thresholds are not met')
        print('   - Strategies are in agreement to hold')
        print()
except Exception as e:
    print(f'\n❌ Error scanning for opportunities: {e}')
    import traceback
    traceback.print_exc()

print('='*70)
print(f'\n✅ Test complete! Generated signals for {signals_generated}/{len(test_symbols)} symbols')
print('='*70 + '\n')
