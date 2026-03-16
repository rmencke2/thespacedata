"""
AGGRESSIVE Trading Configuration
$30,000 allocation - High risk, high reward
Focus: Volatile small caps, quick trades, momentum plays
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Aggressive trading configuration"""
    
    # Alpaca API Configuration
    ALPACA_API_KEY = os.getenv('ALPACA_API_KEY', '')
    ALPACA_SECRET_KEY = os.getenv('ALPACA_SECRET_KEY', '')
    ALPACA_BASE_URL = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
    
    # Trading Universe - HIGH VOLATILITY STOCKS
    STOCK_UNIVERSE = [
        # Ultra volatile EVs (5-10% daily moves)
        'RIVN', 'LCID', 'CHPT', 'BLNK',
        
        # Volatile crypto/fintech
        'COIN', 'MARA', 'RIOT', 'SQ',
        
        # High beta tech
        'PLTR', 'RKLB', 'IONQ', 'SMCI',
        
        # Volatile AI/semis
        'ARM', 'AVGO',
        
        # Momentum plays
        'TSLA', 'AMD', 'NVDA',
    ]
    
    # Aggressive Risk Management
    MAX_POSITION_SIZE = 0.25  # 25% per position (vs 20% conservative)
    MAX_PORTFOLIO_RISK = 0.03  # 3% risk per trade (vs 2% conservative)
    MAX_POSITIONS = 6  # More positions (vs 5 conservative)
    DAILY_LOSS_LIMIT = 0.08  # 8% daily loss limit (vs 5% conservative)
    STOP_LOSS_PERCENT = 0.04  # 4% stop loss (wider for volatility)
    
    # AGGRESSIVE Strategy Parameters
    MEAN_REVERSION_PERIOD = 15  # Shorter period = more responsive
    MEAN_REVERSION_STD = 1.2  # VERY sensitive (vs 1.5 conservative)
    
    MOMENTUM_FAST_PERIOD = 8  # Faster (vs 10 conservative)
    MOMENTUM_SLOW_PERIOD = 21  # Faster (vs 30 conservative)
    MOMENTUM_RSI_PERIOD = 14
    MOMENTUM_RSI_OVERSOLD = 45  # More sensitive (vs 40)
    MOMENTUM_RSI_OVERBOUGHT = 55  # More sensitive (vs 60)
    
    # Data Configuration
    BACKTEST_START_DATE = "2023-01-01"
    BACKTEST_END_DATE = "2024-12-31"
    DATA_INTERVAL = "1d"
    
    # Live Trading
    TRADING_SCHEDULE = "09:35"
    MARKET_OPEN = "09:30"
    MARKET_CLOSE = "16:00"
    
    # Database - SEPARATE DATABASE
    DATABASE_PATH = "trades_aggressive.db"
    
    # Portfolio Settings
    INITIAL_CAPITAL = 30000
    STRATEGY_NAME = "AGGRESSIVE"
    
    @classmethod
    def validate(cls) -> bool:
        if not cls.ALPACA_API_KEY or not cls.ALPACA_SECRET_KEY:
            print("⚠️  Warning: Alpaca API keys not set!")
            return False
        return True
    
    @classmethod
    def print_config(cls):
        print("\n" + "="*60)
        print(f"🔥 {cls.STRATEGY_NAME} TRADING CONFIGURATION")
        print("="*60)
        print(f"Initial Capital: ${cls.INITIAL_CAPITAL:,}")
        print(f"Trading Universe: {len(cls.STOCK_UNIVERSE)} volatile stocks")
        print(f"Sample Stocks: {', '.join(cls.STOCK_UNIVERSE[:5])}")
        print(f"Max Positions: {cls.MAX_POSITIONS}")
        print(f"Risk per Trade: {cls.MAX_PORTFOLIO_RISK*100}%")
        print(f"Stop Loss: {cls.STOP_LOSS_PERCENT*100}%")
        print(f"Daily Loss Limit: {cls.DAILY_LOSS_LIMIT*100}%")
        print(f"Mean Reversion Sensitivity: {cls.MEAN_REVERSION_STD} std dev")
        print(f"Database: {cls.DATABASE_PATH}")
        print("="*60 + "\n")
