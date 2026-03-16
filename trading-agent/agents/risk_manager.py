"""
Risk Manager Agent
Manages position sizing, risk limits, and portfolio exposure
"""
from typing import Dict, List, Optional
from utils.config import Config
from utils.database import TradingDatabase

class RiskManagerAgent:
    """
    Risk management functions:
    - Position sizing based on volatility
    - Portfolio risk limits
    - Daily loss limits
    - Maximum positions
    - Stop-loss validation
    """
    
    def __init__(self, portfolio_value: float = 10000):
        self.portfolio_value = portfolio_value
        self.db = TradingDatabase()
        self.name = "risk_manager"
        self.daily_pnl = 0
    
    def calculate_position_size(
        self,
        symbol: str,
        entry_price: float,
        stop_loss: float,
        volatility: float = None
    ) -> Dict:
        """
        Calculate appropriate position size
        
        Uses:
        - Maximum risk per trade (2% of portfolio)
        - Maximum position size (20% of portfolio)
        - Volatility adjustment
        
        Returns:
            Dict with quantity, risk_amount, position_value
        """
        # Calculate risk per share
        risk_per_share = abs(entry_price - stop_loss)
        
        if risk_per_share == 0:
            return {
                'approved': False,
                'reason': 'Stop loss too close to entry price'
            }
        
        # Max risk amount (2% of portfolio)
        max_risk = self.portfolio_value * Config.MAX_PORTFOLIO_RISK
        
        # Calculate quantity based on risk
        quantity = int(max_risk / risk_per_share)
        
        # Check position size limit (20% of portfolio)
        position_value = quantity * entry_price
        max_position_value = self.portfolio_value * Config.MAX_POSITION_SIZE
        
        if position_value > max_position_value:
            # Reduce quantity to meet position size limit
            quantity = int(max_position_value / entry_price)
            position_value = quantity * entry_price
        
        # Adjust for volatility if provided
        if volatility and volatility > 3:  # High volatility
            quantity = int(quantity * 0.5)  # Reduce by 50%
            position_value = quantity * entry_price
        
        return {
            'approved': True,
            'quantity': quantity,
            'position_value': position_value,
            'risk_per_share': risk_per_share,
            'risk_amount': quantity * risk_per_share,
            'risk_percent': (quantity * risk_per_share / self.portfolio_value) * 100,
            'position_percent': (position_value / self.portfolio_value) * 100
        }
    
    def validate_trade(
        self,
        symbol: str,
        action: str,
        entry_price: float,
        stop_loss: float,
        confidence: float,
        volatility: float = None
    ) -> Dict:
        """
        Validate if a trade should be executed
        
        Checks:
        - Daily loss limit
        - Maximum concurrent positions
        - Position size limits
        - Stop loss requirements
        - Confidence threshold
        
        Returns:
            Dict with approved boolean and details
        """
        validations = []
        
        # Check daily loss limit
        if self.daily_pnl < -(self.portfolio_value * Config.DAILY_LOSS_LIMIT):
            return {
                'approved': False,
                'reason': f'Daily loss limit exceeded. Current P&L: ${self.daily_pnl:.2f}',
                'validations': ['daily_loss_limit_exceeded']
            }
        validations.append('daily_loss_limit_ok')
        
        # Check maximum positions
        open_positions = self.db.get_open_positions()
        if len(open_positions) >= Config.MAX_POSITIONS:
            return {
                'approved': False,
                'reason': f'Maximum positions ({Config.MAX_POSITIONS}) already open',
                'validations': validations + ['max_positions_exceeded']
            }
        validations.append('position_limit_ok')
        
        # Check if already have position in this symbol
        if any(p['symbol'] == symbol for p in open_positions):
            return {
                'approved': False,
                'reason': f'Already have position in {symbol}',
                'validations': validations + ['duplicate_position']
            }
        validations.append('no_duplicate_position')
        
        # Check confidence threshold
        if confidence < 0.3:
            return {
                'approved': False,
                'reason': f'Confidence too low: {confidence*100:.1f}%',
                'validations': validations + ['low_confidence']
            }
        validations.append('confidence_ok')
        
        # Calculate position size
        position_calc = self.calculate_position_size(symbol, entry_price, stop_loss, volatility)
        
        if not position_calc.get('approved'):
            return {
                'approved': False,
                'reason': position_calc.get('reason'),
                'validations': validations + ['position_size_invalid']
            }
        validations.append('position_size_ok')
        
        # Check if we have enough capital
        if position_calc['position_value'] > self.portfolio_value * 0.9:
            return {
                'approved': False,
                'reason': 'Insufficient capital for position',
                'validations': validations + ['insufficient_capital']
            }
        validations.append('capital_sufficient')
        
        # All checks passed
        return {
            'approved': True,
            'reason': 'All risk checks passed',
            'validations': validations,
            'position_details': position_calc
        }
    
    def should_close_position(
        self,
        position: Dict,
        current_price: float,
        signal: str = None
    ) -> Dict:
        """
        Determine if position should be closed
        
        Checks:
        - Stop loss hit
        - Target price reached
        - Exit signal from strategy
        
        Returns:
            Dict with should_close boolean and reason
        """
        entry_price = position['entry_price']
        stop_loss = position['stop_loss']
        
        # Check stop loss
        if current_price <= stop_loss:
            return {
                'should_close': True,
                'reason': 'Stop loss hit',
                'exit_type': 'stop_loss'
            }
        
        # Check if exit signal
        if signal == 'close':
            return {
                'should_close': True,
                'reason': 'Strategy exit signal',
                'exit_type': 'signal'
            }
        
        # Check if opposite signal (e.g., sell signal when holding long)
        if signal == 'sell' and position['quantity'] > 0:
            return {
                'should_close': True,
                'reason': 'Opposite signal received',
                'exit_type': 'signal'
            }
        
        if signal == 'buy' and position['quantity'] < 0:
            return {
                'should_close': True,
                'reason': 'Opposite signal received',
                'exit_type': 'signal'
            }
        
        return {
            'should_close': False,
            'reason': 'Position within parameters'
        }
    
    def update_portfolio_value(self, new_value: float):
        """Update portfolio value"""
        self.portfolio_value = new_value
    
    def update_daily_pnl(self, pnl: float):
        """Update daily P&L"""
        self.daily_pnl += pnl
    
    def reset_daily_pnl(self):
        """Reset daily P&L (call at start of each day)"""
        self.daily_pnl = 0
    
    def get_risk_summary(self) -> Dict:
        """Get current risk metrics"""
        open_positions = self.db.get_open_positions()
        
        total_exposure = sum(
            abs(p['quantity'] * p['current_price']) 
            for p in open_positions
        )
        
        total_risk = sum(
            abs(p['quantity'] * (p['entry_price'] - p['stop_loss']))
            for p in open_positions
        )
        
        return {
            'portfolio_value': self.portfolio_value,
            'daily_pnl': self.daily_pnl,
            'daily_pnl_percent': (self.daily_pnl / self.portfolio_value) * 100,
            'open_positions': len(open_positions),
            'total_exposure': total_exposure,
            'exposure_percent': (total_exposure / self.portfolio_value) * 100,
            'total_risk': total_risk,
            'risk_percent': (total_risk / self.portfolio_value) * 100,
            'daily_loss_limit': self.portfolio_value * Config.DAILY_LOSS_LIMIT,
            'remaining_daily_risk': (self.portfolio_value * Config.DAILY_LOSS_LIMIT) + self.daily_pnl
        }
    
    def print_risk_summary(self):
        """Pretty print risk summary"""
        summary = self.get_risk_summary()
        
        print("\n" + "="*70)
        print("RISK MANAGEMENT SUMMARY")
        print("="*70)
        print(f"Portfolio Value: ${summary['portfolio_value']:,.2f}")
        print(f"Daily P&L: ${summary['daily_pnl']:,.2f} ({summary['daily_pnl_percent']:+.2f}%)")
        print(f"Daily Loss Limit: ${summary['daily_loss_limit']:,.2f}")
        print(f"Remaining Daily Risk: ${summary['remaining_daily_risk']:,.2f}")
        print(f"\nOpen Positions: {summary['open_positions']}/{Config.MAX_POSITIONS}")
        print(f"Total Exposure: ${summary['total_exposure']:,.2f} ({summary['exposure_percent']:.1f}%)")
        print(f"Total Risk: ${summary['total_risk']:,.2f} ({summary['risk_percent']:.1f}%)")
        print("="*70 + "\n")


if __name__ == "__main__":
    # Test risk manager
    risk_manager = RiskManagerAgent(portfolio_value=10000)
    
    print("\n🛡️  Testing Risk Manager...\n")
    
    # Test position sizing
    position = risk_manager.calculate_position_size(
        symbol='TSLA',
        entry_price=250.00,
        stop_loss=245.00,
        volatility=2.5
    )
    
    print("Position Sizing:")
    print(f"  Quantity: {position['quantity']}")
    print(f"  Position Value: ${position['position_value']:.2f}")
    print(f"  Risk Amount: ${position['risk_amount']:.2f}")
    print(f"  Risk %: {position['risk_percent']:.2f}%")
    
    # Test trade validation
    validation = risk_manager.validate_trade(
        symbol='TSLA',
        action='buy',
        entry_price=250.00,
        stop_loss=245.00,
        confidence=0.75,
        volatility=2.5
    )
    
    print(f"\nTrade Validation:")
    print(f"  Approved: {validation['approved']}")
    print(f"  Reason: {validation['reason']}")
    
    # Risk summary
    risk_manager.print_risk_summary()
