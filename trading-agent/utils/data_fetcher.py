"""
Data fetching utilities for historical and live market data
FIXED VERSION with retry logic and better error handling
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict
import time
from utils.config import Config

class DataFetcher:
    """Fetch market data from various sources"""
    
    def __init__(self):
        self.alpaca_data_client = None
        if Config.ALPACA_API_KEY:
            try:
                from alpaca.data.historical import StockHistoricalDataClient
                self.alpaca_data_client = StockHistoricalDataClient(
                    Config.ALPACA_API_KEY,
                    Config.ALPACA_SECRET_KEY
                )
            except:
                pass
    
    def get_historical_data(
        self, 
        symbols: List[str], 
        start_date: str, 
        end_date: str,
        interval: str = "1d"
    ) -> Dict[str, pd.DataFrame]:
        """
        Get historical data using yfinance (free) with retry logic
        """
        data = {}
        
        for symbol in symbols:
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    print(f"Fetching {symbol}... (attempt {attempt + 1}/{max_retries})")
                    
                    # Use download instead of Ticker for better reliability
                    df = yf.download(
                        symbol,
                        start=start_date,
                        end=end_date,
                        interval=interval,
                        progress=False
                    )
                    
                    if not df.empty:
                        # Standardize column names
                        df.columns = [col.lower() if isinstance(col, str) else col[0].lower() for col in df.columns]
                        data[symbol] = df
                        print(f"✅ {symbol}: {len(df)} bars")
                        break
                    else:
                        if attempt < max_retries - 1:
                            print(f"⚠️  {symbol}: No data, retrying...")
                            time.sleep(2)
                        else:
                            print(f"⚠️  {symbol}: No data after {max_retries} attempts")
                        
                except Exception as e:
                    if attempt < max_retries - 1:
                        print(f"⚠️  {symbol}: Error, retrying...")
                        time.sleep(2)
                    else:
                        print(f"❌ Error fetching {symbol}: {str(e)[:50]}")
        
        return data
    
    def get_latest_price(self, symbol: str) -> float:
        """Get latest price for a symbol"""
        try:
            df = yf.download(symbol, period="1d", interval="1m", progress=False)
            if not df.empty:
                return df['Close'].iloc[-1]
        except:
            pass
        return None
    
    def get_latest_bars(self, symbols: List[str], days: int = 30) -> Dict[str, pd.DataFrame]:
        """Get recent bars for multiple symbols"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days + 5)  # Extra days for safety
        
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
        return vol if pd.notna(vol) else 0
    
    def get_market_data_summary(self, symbol: str, df: pd.DataFrame) -> Dict:
        """Get summary statistics for a symbol"""
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


if __name__ == "__main__":
    fetcher = DataFetcher()
    print("\n🔍 Testing Data Fetcher...\n")
    
    # Test with reliable symbols
    symbols = ['AAPL', 'MSFT']
    data = fetcher.get_latest_bars(symbols, days=30)
    
    for symbol, df in data.items():
        print(f"\n{symbol}: {len(df)} bars fetched")
        summary = fetcher.get_market_data_summary(symbol, df)
        if summary:
            print(f"  Latest Price: ${summary['latest_price']:.2f}")
