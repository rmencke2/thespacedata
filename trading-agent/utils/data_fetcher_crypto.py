"""
Alpaca Crypto Data Fetcher - FIXED VERSION
Uses Alpaca API for crypto data with correct symbol format
"""
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
from utils.config import Config

class DataFetcher:
    """Fetch crypto data from Alpaca API"""
    
    def __init__(self):
        self.alpaca_crypto_client = None
        if Config.ALPACA_API_KEY:
            self.alpaca_crypto_client = CryptoHistoricalDataClient(
                Config.ALPACA_API_KEY,
                Config.ALPACA_SECRET_KEY
            )
            print("✅ Alpaca crypto data client initialized")
        else:
            print("❌ Alpaca API keys not configured")
    
    def get_historical_data(
        self, 
        symbols: List[str], 
        start_date: str, 
        end_date: str,
        interval: str = "1d"
    ) -> Dict[str, pd.DataFrame]:
        """Get historical crypto data using Alpaca Crypto API"""
        data = {}
        
        if not self.alpaca_crypto_client:
            print("❌ Alpaca crypto client not configured")
            return data
        
        for symbol in symbols:
            try:
                print(f"Fetching {symbol} from Alpaca Crypto...")
                
                # Alpaca wants the slash! BTC/USD not BTCUSD
                request_params = CryptoBarsRequest(
                    symbol_or_symbols=symbol,  # Keep the slash!
                    timeframe=TimeFrame.Day,
                    start=start_date,
                    end=end_date
                )
                
                bars = self.alpaca_crypto_client.get_crypto_bars(request_params)
                
                if bars and bars.df is not None and not bars.df.empty:
                    df = bars.df
                    if isinstance(df.index, pd.MultiIndex):
                        df = df.reset_index(level='symbol', drop=True)
                    df.columns = [col.lower() for col in df.columns]
                    data[symbol] = df
                    print(f"✅ {symbol}: {len(df)} bars")
                else:
                    print(f"⚠️  {symbol}: No data from Alpaca")
            except Exception as e:
                print(f"❌ Error fetching {symbol}: {str(e)}")
        
        return data
    
    def get_latest_price(self, symbol: str) -> float:
        """Get latest price for a crypto"""
        if not self.alpaca_crypto_client:
            return None
        try:
            request_params = CryptoBarsRequest(
                symbol_or_symbols=symbol,  # Keep the slash!
                timeframe=TimeFrame.Day,
                limit=1
            )
            bars = self.alpaca_crypto_client.get_crypto_bars(request_params)
            if bars and bars.df is not None and not bars.df.empty:
                df = bars.df
                if isinstance(df.index, pd.MultiIndex):
                    df = df.reset_index(level='symbol', drop=True)
                return df['close'].iloc[-1]
        except Exception as e:
            print(f"Error getting price for {symbol}: {e}")
        return None
    
    def get_latest_bars(self, symbols: List[str], days: int = 30) -> Dict[str, pd.DataFrame]:
        """Get recent bars for multiple cryptos"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days + 5)
        return self.get_historical_data(
            symbols,
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d"),
            "1d"
        )
    
    def calculate_returns(self, df: pd.DataFrame) -> pd.Series:
        """Calculate daily returns"""
        return df['close'].pct_change()
    
    def calculate_volatility(self, df: pd.DataFrame, window: int = 20) -> float:
        """Calculate rolling volatility"""
        returns = self.calculate_returns(df)
        vol = returns.rolling(window=window).std().iloc[-1]
        return vol if pd.notna(vol) else 0.0
    
    def get_market_data_summary(self, symbol: str, df: pd.DataFrame) -> Dict:
        """Get summary statistics for a crypto"""
        if df.empty:
            return None
        latest = df.iloc[-1]
        returns = self.calculate_returns(df)
        volatility = self.calculate_volatility(df)
        return {
            'symbol': symbol,
            'latest_price': latest['close'],
            'latest_volume': latest['volume'],
            'daily_return': returns.iloc[-1] if len(returns) > 0 else 0,
            'volatility': volatility,
            'avg_volume': df['volume'].tail(20).mean(),
            'high_52w': df['high'].tail(252).max() if len(df) > 252 else df['high'].max(),
            'low_52w': df['low'].tail(252).min() if len(df) > 252 else df['low'].min(),
        }
