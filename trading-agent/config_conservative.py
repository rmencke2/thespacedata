"""
CONSERVATIVE Trading Configuration
$30,000 allocation - Lower risk, steady growth
Focus: Large caps, stable trends, quality setups
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Conservative trading configuration"""
    
    # Alpaca API Configuration
    ALPACA_API_KEY = os.getenv('ALPACA_API_KEY', '')
    ALPACA_SECRET_KEY = os.getenv('ALPACA_SECRET_KEY', '')
    ALPACA_BASE_URL = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
    
    # Trading Universe - STABLE LARGE CAPS
    STOCK_UNIVERSE = [
        # Mega cap tech (stable)
        'MSFT', 'AAPL', 'GOOGL', 'META',
        
        # Large cap cybersecurity
        'CRWD', 'PANW', 'FTNT',
        
        # Established AI/semis
        'NVDA', 'AMD', 'AVGO', 'MU',
        
        # Enterprise software
        'NOW', 'CRM', 'SNOW',
        
        # Diversification
        'TSLA', 'DIS',
    ]
    
    # Conservative Risk Management
    MAX_POSITION_SIZE = 0.15  # 15% per position (smaller)
    MAX_PORTFOLIO_RISK = 0.015  # 1.5% risk per trade (lower)
    MAX_POSITIONS = 4  # Fewer positions
    DAILY_LOSS_LIMIT = 0.04  # 4% daily loss limit (tighter)
    STOP_LOSS_PERCENT = 0.02  # 2% stop loss (tight)
    
    # CONSERVATIVE Strategy Parameters
    MEAN_REVERSION_PERIOD = 20  # Standard period
    MEAN_REVERSION_STD = 1.8  # Less sensitive (higher threshold)
    
    MOMENTUM_FAST_PERIOD = 10  # Standard
    MOMENTUM_SLOW_PERIOD = 30  # Standard
    MOMENTUM_RSI_PERIOD = 14
    MOMENTUM_RSI_OVERSOLD = 35  # More conservative
    MOMENTUM_RSI_OVERBOUGHT = 65  # More conservative
    
    # Data Configuration
    BACKTEST_START_DATE = "2023-01-01"
    BACKTEST_END_DATE = "2024-12-31"
    DATA_INTERVAL = "1d"
    
    # Live Trading
    TRADING_SCHEDULE = "09:35"
    MARKET_OPEN = "09:30"
    MARKET_CLOSE = "16:00"
    
    # Database - SEPARATE DATABASE
    DATABASE_PATH = "trades_conservative.db"
    
    # Portfolio Settings
    INITIAL_CAPITAL = 30000
    STRATEGY_NAME = "CONSERVATIVE"
    
    @classmethod
    def validate(cls) -> bool:
        if not cls.ALPACA_API_KEY or not cls.ALPACA_SECRET_KEY:
            print("⚠️  Warning: Alpaca API keys not set!")
            return False
        return True
    
    @classmethod
    def print_config(cls):
        print("\n" + "="*60)
        print(f"🛡️  {cls.STRATEGY_NAME} TRADING CONFIGURATION")
        print("="*60)
        print(f"Initial Capital: ${cls.INITIAL_CAPITAL:,}")
        print(f"Trading Universe: {len(cls.STOCK_UNIVERSE)} stable stocks")
        print(f"Sample Stocks: {', '.join(cls.STOCK_UNIVERSE[:5])}")
        print(f"Max Positions: {cls.MAX_POSITIONS}")
        print(f"Risk per Trade: {cls.MAX_PORTFOLIO_RISK*100}%")
        print(f"Stop Loss: {cls.STOP_LOSS_PERCENT*100}%")
        print(f"Daily Loss Limit: {cls.DAILY_LOSS_LIMIT*100}%")
        print(f"Mean Reversion Sensitivity: {cls.MEAN_REVERSION_STD} std dev")
        print(f"Database: {cls.DATABASE_PATH}")
        print("="*60 + "\n")
