"""
Configuration management for the trading system
"""
import os
from dotenv import load_dotenv
from typing import List

load_dotenv()

class Config:
    """System configuration"""
    
    # Alpaca API Configuration
    ALPACA_API_KEY = os.getenv('ALPACA_API_KEY', '')
    ALPACA_SECRET_KEY = os.getenv('ALPACA_SECRET_KEY', '')
    ALPACA_BASE_URL = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
    
    # Trading Universe
    STOCK_UNIVERSE = [
        # EV / Energy
        'TSLA', 'RIVN', 'LCID', 'ENPH', 'SEDG', 'FSLR', 'CHPT', 'BLNK',

        # Cybersecurity
        'CRWD', 'PANW', 'ZS', 'S', 'OKTA', 'NET', 'FTNT',

        # AI / Semis
        'NVDA', 'AMD', 'AVGO', 'ARM', 'SMCI', 'MU',

        # Software / Platforms
        'MSFT', 'NOW', 'DDOG', 'SNOW', 'MDB', 'CRM',

        # Fintech
        'COIN', 'SQ', 'PYPL', 'AFRM',

        # Speculative momentum
        'PLTR', 'RKLB', 'IONQ',
    ]

    
    # Risk Management
    MAX_POSITION_SIZE = 0.2  # Max 20% of portfolio per position
    MAX_PORTFOLIO_RISK = 0.02  # Max 2% risk per trade
    MAX_POSITIONS = 5  # Maximum concurrent positions
    DAILY_LOSS_LIMIT = 0.05  # Stop trading if down 5% in a day
    STOP_LOSS_PERCENT = 0.02  # 2% stop loss on each position
    
    # Strategy Parameters
    MEAN_REVERSION_PERIOD = 20  # Moving average period
    #MEAN_REVERSION_STD = 2.0  # Standard deviations for entry
    # Change to (more aggressive):
    MEAN_REVERSION_STD = 1.5  # Triggers more easily

    MOMENTUM_FAST_PERIOD = 10
    MOMENTUM_SLOW_PERIOD = 30
    MOMENTUM_RSI_PERIOD = 14
    MOMENTUM_RSI_OVERSOLD = 40 # Instead of 30
    MOMENTUM_RSI_OVERBOUGHT = 60 # Instead of 70
    
    # Data Configuration
    BACKTEST_START_DATE = "2023-01-01"
    BACKTEST_END_DATE = "2024-12-31"
    DATA_INTERVAL = "1d"  # Daily data
    
    # Live Trading
    TRADING_SCHEDULE = "09:35"  # Trade at 9:35 AM ET (after market open)
    MARKET_OPEN = "09:30"
    MARKET_CLOSE = "16:00"
    
    # Database
    DATABASE_PATH = "trades.db"
    
    # OpenAI (optional - for LangGraph agents)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration"""
        if not cls.ALPACA_API_KEY or not cls.ALPACA_SECRET_KEY:
            print("⚠️  Warning: Alpaca API keys not set!")
            print("Please create a .env file with ALPACA_API_KEY and ALPACA_SECRET_KEY")
            return False
        return True
    
    @classmethod
    def print_config(cls):
        """Print current configuration"""
        print("\n" + "="*50)
        print("TRADING SYSTEM CONFIGURATION")
        print("="*50)
        print(f"Trading Universe: {', '.join(cls.STOCK_UNIVERSE)}")
        print(f"Max Positions: {cls.MAX_POSITIONS}")
        print(f"Risk per Trade: {cls.MAX_PORTFOLIO_RISK*100}%")
        print(f"Stop Loss: {cls.STOP_LOSS_PERCENT*100}%")
        print(f"Daily Loss Limit: {cls.DAILY_LOSS_LIMIT*100}%")
        print(f"Alpaca URL: {cls.ALPACA_BASE_URL}")
        print("="*50 + "\n")

if __name__ == "__main__":
    Config.print_config()
    if Config.validate():
        print("✅ Configuration is valid!")
    else:
        print("❌ Configuration is invalid!")
