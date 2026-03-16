"""
Execution Agent
Handles order execution with Alpaca API
"""
from typing import Dict, Optional
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from utils.config import Config
from utils.database import TradingDatabase
from datetime import datetime

class ExecutionAgent:
    """
    Executes trades through Alpaca API:
    - Market orders
    - Limit orders
    - Order status tracking
    - Position management
    """
    
    def __init__(self):
        self.name = "execution_agent"
        self.db = TradingDatabase()
        
        # Initialize Alpaca client
        if Config.ALPACA_API_KEY:
            self.client = TradingClient(
                Config.ALPACA_API_KEY,
                Config.ALPACA_SECRET_KEY,
                paper=True  # Always use paper trading
            )
        else:
            self.client = None
            print("⚠️  Alpaca API keys not configured. Running in simulation mode.")
    
    def get_account_info(self) -> Dict:
        """Get account information"""
        if not self.client:
            return {
                'status': 'simulated',
                'equity': 10000,
                'cash': 10000,
                'buying_power': 10000
            }
        
        try:
            account = self.client.get_account()
            return {
                'status': 'connected',
                'equity': float(account.equity),
                'cash': float(account.cash),
                'buying_power': float(account.buying_power),
                'portfolio_value': float(account.portfolio_value),
                'day_trade_count': account.daytrade_count
            }
        except Exception as e:
            print(f"❌ Error getting account info: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def place_order(
        self,
        symbol: str,
        side: str,
        quantity: int,
        order_type: str = 'market',
        limit_price: float = None
    ) -> Dict:
        """
        Place an order
        
        Args:
            symbol: Stock symbol
            side: 'buy' or 'sell'
            quantity: Number of shares
            order_type: 'market' or 'limit'
            limit_price: Price for limit orders
        
        Returns:
            Dict with order details
        """
        if quantity <= 0:
            return {
                'success': False,
                'message': 'Invalid quantity'
            }
        
        # Convert side to Alpaca enum
        order_side = OrderSide.BUY if side == 'buy' else OrderSide.SELL
        
        # Simulation mode
        if not self.client:
            print(f"📝 [SIMULATION] {side.upper()} {quantity} shares of {symbol}")
            return {
                'success': True,
                'simulated': True,
                'order_id': f"SIM-{datetime.now().timestamp()}",
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'filled_price': limit_price if limit_price else 0
            }
        
        try:
            # Create order request
            if order_type == 'market':
                order_data = MarketOrderRequest(
                    symbol=symbol,
                    qty=quantity,
                    side=order_side,
                    time_in_force=TimeInForce.DAY
                )
            else:  # limit order
                order_data = LimitOrderRequest(
                    symbol=symbol,
                    qty=quantity,
                    side=order_side,
                    time_in_force=TimeInForce.DAY,
                    limit_price=limit_price
                )
            
            # Submit order
            order = self.client.submit_order(order_data)
            
            print(f"✅ Order placed: {side.upper()} {quantity} {symbol}")
            
            return {
                'success': True,
                'order_id': order.id,
                'symbol': order.symbol,
                'side': side,
                'quantity': quantity,
                'status': order.status,
                'submitted_at': order.submitted_at
            }
            
        except Exception as e:
            print(f"❌ Error placing order: {e}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def execute_trade(
        self,
        symbol: str,
        action: str,
        position_details: Dict,
        strategy: str
    ) -> Dict:
        """
        Execute a trade with full workflow
        
        Args:
            symbol: Stock symbol
            action: 'buy' or 'sell'
            position_details: From RiskManager
            strategy: Strategy name
        
        Returns:
            Dict with execution results
        """
        quantity = position_details['quantity']
        entry_price = position_details.get('entry_price', 0)
        stop_loss = position_details.get('stop_loss', 0)
        
        # Place the order
        order_result = self.place_order(
            symbol=symbol,
            side=action,
            quantity=quantity,
            order_type='market'
        )
        
        if not order_result['success']:
            return {
                'success': False,
                'message': f"Failed to place order: {order_result.get('message')}"
            }
        
        # Log trade to database
        trade_data = {
            'symbol': symbol,
            'side': action,
            'quantity': quantity,
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'strategy': strategy,
            'status': 'open',
            'notes': f"Order ID: {order_result['order_id']}"
        }
        
        trade_id = self.db.log_trade(trade_data)
        
        # Update positions table
        position_data = {
            'quantity': quantity if action == 'buy' else -quantity,
            'entry_price': entry_price,
            'current_price': entry_price,
            'stop_loss': stop_loss,
            'strategy': strategy,
            'entry_timestamp': datetime.now().isoformat(),
            'unrealized_pnl': 0
        }
        
        self.db.update_position(symbol, position_data)
        
        print(f"✅ Trade executed: {action.upper()} {quantity} {symbol} @ ${entry_price:.2f}")
        
        return {
            'success': True,
            'trade_id': trade_id,
            'order_result': order_result,
            'trade_data': trade_data
        }
    
    def close_position(self, symbol: str, reason: str = '') -> Dict:
        """
        Close an open position
        
        Args:
            symbol: Stock symbol
            reason: Reason for closing
        
        Returns:
            Dict with closing results
        """
        # Get current position
        positions = self.db.get_open_positions()
        position = next((p for p in positions if p['symbol'] == symbol), None)
        
        if not position:
            return {
                'success': False,
                'message': f'No open position for {symbol}'
            }
        
        quantity = abs(position['quantity'])
        side = 'sell' if position['quantity'] > 0 else 'buy'
        
        # Get current price (for simulation)
        from utils.data_fetcher import DataFetcher
        fetcher = DataFetcher()
        current_price = fetcher.get_latest_price(symbol) or position['current_price']
        
        # Place closing order
        order_result = self.place_order(
            symbol=symbol,
            side=side,
            quantity=quantity,
            order_type='market'
        )
        
        if not order_result['success']:
            return {
                'success': False,
                'message': f"Failed to close position: {order_result.get('message')}"
            }
        
        # Update trade in database
        open_trades = self.db.get_open_trades()
        trade = next((t for t in open_trades if t['symbol'] == symbol), None)
        
        if trade:
            self.db.close_trade(
                trade_id=trade['id'],
                exit_price=current_price
            )
        
        # Remove from positions
        self.db.remove_position(symbol)
        
        # Calculate P&L
        if position['quantity'] > 0:  # Long position
            pnl = (current_price - position['entry_price']) * quantity
        else:  # Short position
            pnl = (position['entry_price'] - current_price) * quantity
        
        pnl_percent = (pnl / (position['entry_price'] * quantity)) * 100
        
        print(f"✅ Position closed: {symbol} | P&L: ${pnl:.2f} ({pnl_percent:+.2f}%)")
        print(f"   Reason: {reason}")
        
        return {
            'success': True,
            'symbol': symbol,
            'pnl': pnl,
            'pnl_percent': pnl_percent,
            'exit_price': current_price,
            'reason': reason
        }
    
    def get_positions(self) -> Dict:
        """Get all current positions"""
        if not self.client:
            return self.db.get_open_positions()
        
        try:
            positions = self.client.get_all_positions()
            return [{
                'symbol': p.symbol,
                'quantity': float(p.qty),
                'entry_price': float(p.avg_entry_price),
                'current_price': float(p.current_price),
                'unrealized_pnl': float(p.unrealized_pl)
            } for p in positions]
        except Exception as e:
            print(f"❌ Error getting positions: {e}")
            return []
    
    def cancel_all_orders(self) -> Dict:
        """Cancel all open orders"""
        if not self.client:
            return {'success': True, 'message': 'Simulation mode'}
        
        try:
            self.client.cancel_orders()
            print("✅ All orders cancelled")
            return {'success': True}
        except Exception as e:
            print(f"❌ Error cancelling orders: {e}")
            return {'success': False, 'message': str(e)}


if __name__ == "__main__":
    # Test execution agent
    executor = ExecutionAgent()
    
    print("\n⚡ Testing Execution Agent...\n")
    
    # Get account info
    account = executor.get_account_info()
    print("Account Info:")
    print(f"  Status: {account['status']}")
    print(f"  Equity: ${account['equity']:,.2f}")
    print(f"  Cash: ${account['cash']:,.2f}")
    
    # Test simulated order
    position_details = {
        'quantity': 10,
        'entry_price': 250.00,
        'stop_loss': 245.00
    }
    
    result = executor.execute_trade(
        symbol='TSLA',
        action='buy',
        position_details=position_details,
        strategy='mean_reversion'
    )
    
    print(f"\nTrade Result:")
    print(f"  Success: {result['success']}")
