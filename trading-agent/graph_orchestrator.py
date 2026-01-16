"""
LangGraph Orchestrator
Coordinates all agents in a workflow
"""
from typing import Dict, TypedDict, Annotated
from langgraph.graph import StateGraph, END
import operator
from agents.market_analyzer import MarketAnalyzerAgent
from agents.strategy_agent import StrategyAgent
from agents.risk_manager import RiskManagerAgent
from agents.execution_agent import ExecutionAgent
from utils.data_fetcher import DataFetcher
from utils.config import Config
from utils.database import TradingDatabase

# Define the state that flows between agents
class TradingState(TypedDict):
    """State passed between agents"""
    symbols: list
    market_data: Dict
    market_analysis: Dict
    signals: list
    opportunities: list
    validated_trades: list
    executed_trades: list
    portfolio_value: float
    messages: Annotated[list, operator.add]

class TradingOrchestrator:
    """
    Orchestrates the multi-agent trading workflow:
    1. Market Analyzer → Analyze market conditions
    2. Strategy Agent → Generate trading signals
    3. Risk Manager → Validate trades
    4. Execution Agent → Execute approved trades
    """
    
    def __init__(self, portfolio_value: float = 10000):
        self.portfolio_value = portfolio_value
        
        # Initialize agents
        self.market_analyzer = MarketAnalyzerAgent()
        self.strategy_agent = StrategyAgent()
        self.risk_manager = RiskManagerAgent(portfolio_value)
        self.execution_agent = ExecutionAgent()
        self.data_fetcher = DataFetcher()
        self.db = TradingDatabase()
        
        # Build the graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(TradingState)
        
        # Add nodes (agents)
        workflow.add_node("fetch_data", self.fetch_data_node)
        workflow.add_node("analyze_market", self.analyze_market_node)
        workflow.add_node("generate_signals", self.generate_signals_node)
        workflow.add_node("validate_trades", self.validate_trades_node)
        workflow.add_node("execute_trades", self.execute_trades_node)
        
        # Define the flow
        workflow.set_entry_point("fetch_data")
        workflow.add_edge("fetch_data", "analyze_market")
        workflow.add_edge("analyze_market", "generate_signals")
        workflow.add_edge("generate_signals", "validate_trades")
        workflow.add_edge("validate_trades", "execute_trades")
        workflow.add_edge("execute_trades", END)
        
        return workflow.compile()
    
    def fetch_data_node(self, state: TradingState) -> TradingState:
        """Node: Fetch market data"""
        print("\n📊 [1/5] Fetching market data...")
        
        symbols = state.get('symbols', Config.STOCK_UNIVERSE)
        market_data = self.data_fetcher.get_latest_bars(symbols, days=60)
        
        state['market_data'] = market_data
        state['messages'] = [f"Fetched data for {len(market_data)} symbols"]
        
        return state
    
    def analyze_market_node(self, state: TradingState) -> TradingState:
        """Node: Analyze market conditions"""
        print("🔍 [2/5] Analyzing market conditions...")
        
        symbols = list(state['market_data'].keys())
        market_analysis = self.market_analyzer.analyze_market(symbols)
        
        state['market_analysis'] = market_analysis
        state['messages'].append(
            f"Market sentiment: {market_analysis.get('market_sentiment', 'unknown')}"
        )
        
        # Print analysis
        self.market_analyzer.print_analysis(market_analysis)
        
        return state
    
    def generate_signals_node(self, state: TradingState) -> TradingState:
        """Node: Generate trading signals"""
        print("🎯 [3/5] Generating trading signals...")
        
        opportunities = self.strategy_agent.scan_universe(
            list(state['market_data'].keys()),
            state['market_data'],
            state['market_analysis']
        )
        
        state['opportunities'] = opportunities
        state['messages'].append(f"Found {len(opportunities)} trading opportunities")
        
        # Print opportunities
        self.strategy_agent.print_opportunities(opportunities)
        
        return state
    
    def validate_trades_node(self, state: TradingState) -> TradingState:
        """Node: Validate trades with risk management"""
        print("🛡️  [4/5] Validating trades...")
        
        validated_trades = []
        
        for opportunity in state['opportunities']:
            symbol = opportunity['symbol']
            
            # Get volatility from market data
            df = state['market_data'].get(symbol)
            volatility = None
            if df is not None and not df.empty:
                returns = df['close'].pct_change()
                volatility = returns.rolling(window=20).std().iloc[-1] * 100
            
            # Validate with risk manager
            validation = self.risk_manager.validate_trade(
                symbol=symbol,
                action=opportunity['signal'],
                entry_price=opportunity['entry_price'],
                stop_loss=opportunity['stop_loss'],
                confidence=opportunity['confidence'],
                volatility=volatility
            )
            
            if validation['approved']:
                validated_trades.append({
                    'symbol': symbol,
                    'action': opportunity['signal'],
                    'confidence': opportunity['confidence'],
                    'position_details': validation['position_details'],
                    'strategy': 'multi_strategy',
                    'reasoning': opportunity['reasoning']
                })
                print(f"✅ {symbol}: Trade approved - {validation['position_details']['quantity']} shares")
            else:
                print(f"❌ {symbol}: Trade rejected - {validation['reason']}")
        
        state['validated_trades'] = validated_trades
        state['messages'].append(f"Validated {len(validated_trades)} trades")
        
        return state
    
    def execute_trades_node(self, state: TradingState) -> TradingState:
        """Node: Execute approved trades"""
        print("⚡ [5/5] Executing trades...")
        
        executed_trades = []
        
        for trade in state['validated_trades']:
            result = self.execution_agent.execute_trade(
                symbol=trade['symbol'],
                action=trade['action'],
                position_details={
                    'quantity': trade['position_details']['quantity'],
                    'entry_price': trade['position_details'].get('entry_price', 0),
                    'stop_loss': trade['position_details'].get('stop_loss', 0)
                },
                strategy=trade['strategy']
            )
            
            if result['success']:
                executed_trades.append(result)
        
        state['executed_trades'] = executed_trades
        state['messages'].append(f"Executed {len(executed_trades)} trades")
        
        print(f"\n✅ Execution complete: {len(executed_trades)} trades executed")
        
        return state
    
    def run_trading_cycle(self, symbols: list = None) -> Dict:
        """
        Run a complete trading cycle
        
        Args:
            symbols: List of symbols to trade (uses default if None)
        
        Returns:
            Final state after workflow
        """
        print("\n" + "="*70)
        print("STARTING TRADING CYCLE")
        print("="*70)
        
        # Initialize state
        initial_state = TradingState(
            symbols=symbols or Config.STOCK_UNIVERSE,
            market_data={},
            market_analysis={},
            signals=[],
            opportunities=[],
            validated_trades=[],
            executed_trades=[],
            portfolio_value=self.portfolio_value,
            messages=[]
        )
        
        # Run the graph
        final_state = self.graph.invoke(initial_state)
        
        # Print summary
        self._print_cycle_summary(final_state)
        
        return final_state
    
    def manage_positions(self) -> Dict:
        """
        Manage existing positions
        - Check stop losses
        - Check exit signals
        - Update positions
        """
        print("\n" + "="*70)
        print("MANAGING POSITIONS")
        print("="*70)
        
        positions = self.db.get_open_positions()
        
        if not positions:
            print("No open positions to manage.\n")
            return {'positions_closed': 0}
        
        print(f"\nManaging {len(positions)} open positions...")
        
        closed_count = 0
        
        for position in positions:
            symbol = position['symbol']
            
            # Get current price
            current_price = self.data_fetcher.get_latest_price(symbol)
            
            if not current_price:
                print(f"⚠️  Could not get price for {symbol}")
                continue
            
            # Get latest signal
            df = self.data_fetcher.get_latest_bars([symbol], days=60).get(symbol)
            
            signal = None
            if df is not None and not df.empty:
                signal_result = self.strategy_agent.generate_signals(symbol, df)
                signal = signal_result.get('signal')
            
            # Check if should close
            should_close = self.risk_manager.should_close_position(
                position,
                current_price,
                signal
            )
            
            if should_close['should_close']:
                result = self.execution_agent.close_position(
                    symbol,
                    reason=should_close['reason']
                )
                
                if result['success']:
                    closed_count += 1
                    self.risk_manager.update_daily_pnl(result['pnl'])
        
        print(f"\n✅ Position management complete: {closed_count} positions closed")
        
        return {'positions_closed': closed_count}
    
    def _print_cycle_summary(self, state: Dict):
        """Print summary of trading cycle"""
        print("\n" + "="*70)
        print("TRADING CYCLE SUMMARY")
        print("="*70)
        
        for msg in state['messages']:
            print(f"  • {msg}")
        
        print("\n" + "="*70 + "\n")
        
        # Print risk summary
        self.risk_manager.print_risk_summary()
        
        # Print performance
        self.db.print_summary()


if __name__ == "__main__":
    # Test the orchestrator
    print("\n🚀 Testing Trading Orchestrator...\n")
    
    orchestrator = TradingOrchestrator(portfolio_value=10000)
    
    # Run a trading cycle
    result = orchestrator.run_trading_cycle(['TSLA', 'NVDA'])
    
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)
