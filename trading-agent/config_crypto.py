"""
CRYPTO Trading Configuration
$20,000 allocation - 24/7 trading, high volatility
Focus: Bitcoin, Ethereum, major altcoins
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Crypto trading configuration"""
    
    # Alpaca API Configuration
    ALPACA_API_KEY = os.getenv('ALPACA_API_KEY', '')
    ALPACA_SECRET_KEY = os.getenv('ALPACA_SECRET_KEY', '')
    ALPACA_BASE_URL = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
    
    # Crypto Universe - MAJOR CRYPTOCURRENCIES
    STOCK_UNIVERSE = [
        # Blue chip crypto (most liquid, 24/7)
        'BTC/USD',   # Bitcoin - king of crypto
        'ETH/USD',   # Ethereum - #2, high volume
        
        # Large cap alts
        'SOL/USD',   # Solana - high volatility
        'AVAX/USD',  # Avalanche - trending
        
        # Popular trading coins
        'DOGE/USD',  # Dogecoin - meme volatility
        'SHIB/USD',  # Shiba - extreme volatility
        
        # DeFi/Smart contract
        'MATIC/USD', # Polygon - steady mover
        'LINK/USD',  # Chainlink - oracle leader
    ]
    
    # Crypto-Optimized Risk Management
    MAX_POSITION_SIZE = 0.30  # 30% per position (crypto is volatile)
    MAX_PORTFOLIO_RISK = 0.04  # 4% risk per trade (higher than stocks)
    MAX_POSITIONS = 5  # 5 concurrent positions
    DAILY_LOSS_LIMIT = 0.12  # 12% daily loss limit (crypto recovers fast)
    STOP_LOSS_PERCENT = 0.06  # 6% stop loss (wider for crypto volatility)
    
    # CRYPTO Strategy Parameters (tuned for 24/7 volatility)
    MEAN_REVERSION_PERIOD = 20  # Standard period
    MEAN_REVERSION_STD = 1.3  # Sensitive (crypto swings hard)
    
    MOMENTUM_FAST_PERIOD = 10
    MOMENTUM_SLOW_PERIOD = 30
    MOMENTUM_RSI_PERIOD = 14
    MOMENTUM_RSI_OVERSOLD = 35  # Crypto oversold
    MOMENTUM_RSI_OVERBOUGHT = 65  # Crypto overbought
    
    # Data Configuration
    BACKTEST_START_DATE = "2023-01-01"
    BACKTEST_END_DATE = "2024-12-31"
    DATA_INTERVAL = "1d"
    
    # Live Trading - 24/7 for CRYPTO!
    TRADING_SCHEDULE = "00:05"  # Check at 12:05 AM daily
    MARKET_OPEN = "00:00"  # Crypto never closes
    MARKET_CLOSE = "23:59"  # Crypto never closes
    
    # Database - SEPARATE DATABASE
    DATABASE_PATH = "trades_crypto.db"
    
    # Portfolio Settings
    INITIAL_CAPITAL = 20000
    STRATEGY_NAME = "CRYPTO"
    
    @classmethod
    def validate(cls) -> bool:
        if not cls.ALPACA_API_KEY or not cls.ALPACA_SECRET_KEY:
            print("⚠️  Warning: Alpaca API keys not set!")
            return False
        return True
    
    @classmethod
    def print_config(cls):
        print("\n" + "="*60)
        print(f"🪙 {cls.STRATEGY_NAME} TRADING CONFIGURATION")
        print("="*60)
        print(f"Initial Capital: ${cls.INITIAL_CAPITAL:,}")
        print(f"Trading Hours: 24/7/365 (CRYPTO NEVER SLEEPS!)")
        print(f"Trading Universe: {len(cls.STOCK_UNIVERSE)} cryptocurrencies")
        print(f"Sample Coins: BTC, ETH, SOL, DOGE")
        print(f"Max Positions: {cls.MAX_POSITIONS}")
        print(f"Risk per Trade: {cls.MAX_PORTFOLIO_RISK*100}%")
        print(f"Stop Loss: {cls.STOP_LOSS_PERCENT*100}%")
        print(f"Daily Loss Limit: {cls.DAILY_LOSS_LIMIT*100}%")
        print(f"Mean Reversion Sensitivity: {cls.MEAN_REVERSION_STD} std dev")
        print(f"Database: {cls.DATABASE_PATH}")
        print("="*60)
        print("💡 Crypto trades 24/7 - way more opportunities than stocks!")
        print("="*60 + "\n")
