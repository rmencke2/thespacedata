"""
Alpaca Data Feed for Backtrader
Fetches historical data from Alpaca for backtesting and live trading
Supports 4-hour candles and other timeframes
"""
import backtrader as bt
import alpaca_trade_api as tradeapi
import pandas as pd
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

class AlpacaData(bt.DataBase):
    """
    Alpaca Data Feed for Backtrader
    Fetches data from Alpaca API
    """
    
    params = (
        ('api_key', os.getenv('ALPACA_API_KEY')),
        ('secret_key', os.getenv('ALPACA_SECRET_KEY')),
        ('paper', True),  # Use paper trading by default
        ('timeframe', '4H'),  # 4-hour candles
    )
    
    def __init__(self):
        super(AlpacaData, self).__init__()
        
        # Initialize Alpaca API
        base_url = 'https://paper-api.alpaca.markets' if self.p.paper else 'https://api.alpaca.markets'
        
        self.api = tradeapi.REST(
            self.p.api_key,
            self.p.secret_key,
            base_url,
            api_version='v2'
        )
        
        # Data storage
        self.data_df = None
        self.data_idx = 0
    
    def start(self):
        """Called when strategy starts"""
        super(AlpacaData, self).start()
        
        # Fetch historical data
        self._load_data()
    
    def _load_data(self):
        """Fetch data from Alpaca"""
        
        # Convert timeframe to Alpaca format
        timeframe_map = {
            '1Min': '1Min',
            '5Min': '5Min',
            '15Min': '15Min',
            '1H': '1Hour',
            '4H': '4Hour',
            '1D': '1Day',
        }
        
        alpaca_timeframe = timeframe_map.get(self.p.timeframe, '4Hour')
        
        # Get data
        try:
            bars = self.api.get_bars(
                self._dataname,
                alpaca_timeframe,
                start=self.p.fromdate.isoformat() if self.p.fromdate else None,
                end=self.p.todate.isoformat() if self.p.todate else None,
                limit=10000
            )
            
            if bars.df.empty:
                print(f"⚠️  No data returned for {self._dataname}")
                return False
            
            # Convert to pandas DataFrame
            self.data_df = bars.df
            
            # Reset index
            if isinstance(self.data_df.index, pd.MultiIndex):
                self.data_df = self.data_df.reset_index(level='symbol', drop=True)
            
            # Ensure datetime index
            if not isinstance(self.data_df.index, pd.DatetimeIndex):
                self.data_df.index = pd.to_datetime(self.data_df.index)
            
            # Sort by date
            self.data_df = self.data_df.sort_index()
            
            print(f"✅ Loaded {len(self.data_df)} bars for {self._dataname} ({self.p.timeframe})")
            
            return True
            
        except Exception as e:
            print(f"❌ Error fetching data for {self._dataname}: {e}")
            return False
    
    def _load(self):
        """Load next bar"""
        
        if self.data_df is None or self.data_idx >= len(self.data_df):
            return False
        
        # Get current bar
        bar = self.data_df.iloc[self.data_idx]
        
        # Set OHLCV data
        self.lines.datetime[0] = bt.date2num(self.data_df.index[self.data_idx])
        self.lines.open[0] = float(bar['open'])
        self.lines.high[0] = float(bar['high'])
        self.lines.low[0] = float(bar['low'])
        self.lines.close[0] = float(bar['close'])
        self.lines.volume[0] = float(bar['volume'])
        self.lines.openinterest[0] = 0
        
        # Move to next bar
        self.data_idx += 1
        
        return True


def get_alpaca_data(symbol, fromdate, todate, timeframe='4H', paper=True):
    """
    Helper function to create Alpaca data feed
    
    Args:
        symbol: Stock symbol (e.g., 'AAPL', 'SPY')
        fromdate: Start date (datetime)
        todate: End date (datetime)
        timeframe: '1Min', '5Min', '15Min', '1H', '4H', '1D'
        paper: Use paper trading (default True)
    
    Returns:
        Backtrader data feed
    """
    
    data = AlpacaData(
        dataname=symbol,
        fromdate=fromdate,
        todate=todate,
        timeframe=timeframe,
        paper=paper
    )
    
    return data


# Alternative: Use pandas data directly (for testing)
def create_data_feed_from_csv(filepath):
    """
    Create Backtrader data feed from CSV file
    Useful for testing without API calls
    """
    
    df = pd.read_csv(filepath, index_col=0, parse_dates=True)
    
    data = bt.feeds.PandasData(
        dataname=df,
        datetime=None,  # Index is datetime
        open='open',
        high='high',
        low='low',
        close='close',
        volume='volume',
        openinterest=-1
    )
    
    return data


if __name__ == '__main__':
    """Test the Alpaca data feed"""
    
    print("\n" + "="*70)
    print("🧪 Testing Alpaca Data Feed")
    print("="*70 + "\n")
    
    # Check API keys
    api_key = os.getenv('ALPACA_API_KEY')
    secret_key = os.getenv('ALPACA_SECRET_KEY')
    
    if not api_key or not secret_key:
        print("❌ Alpaca API keys not found!")
        print("Please set ALPACA_API_KEY and ALPACA_SECRET_KEY in .env file")
        exit(1)
    
    print("✅ API keys found")
    
    # Test data fetch
    try:
        api = tradeapi.REST(
            api_key,
            secret_key,
            'https://paper-api.alpaca.markets',
            api_version='v2'
        )
        
        # Fetch sample data
        symbol = 'SPY'
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        print(f"\n📊 Fetching {symbol} data...")
        print(f"   Timeframe: 4H candles")
        print(f"   Period: {start_date.date()} to {end_date.date()}")
        
        bars = api.get_bars(
            symbol,
            '4Hour',
            start=start_date.isoformat(),
            end=end_date.isoformat(),
            limit=1000
        )
        
        if not bars.df.empty:
            df = bars.df
            if isinstance(df.index, pd.MultiIndex):
                df = df.reset_index(level='symbol', drop=True)
            
            print(f"\n✅ Successfully fetched {len(df)} bars")
            print(f"\nSample data (last 5 bars):")
            print(df[['open', 'high', 'low', 'close', 'volume']].tail())
            
            print("\n" + "="*70)
            print("✅ Alpaca data feed is working!")
            print("="*70)
            print("\nYou can now run backtests with:")
            print("  python backtest_runner.py")
            
        else:
            print("❌ No data returned")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Check your API keys in .env file")
        print("  2. Make sure you're using PAPER trading keys")
        print("  3. Verify your Alpaca account is active")
