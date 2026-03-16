"""
Alpaca Data Feed for Backtrader - FIXED VERSION
Fetches historical data from Alpaca for backtesting and live trading
"""
import backtrader as bt
import alpaca_trade_api as tradeapi
import pandas as pd
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

class AlpacaData(bt.DataBase):
    """Alpaca Data Feed for Backtrader"""
    
    params = (
        ('api_key', os.getenv('ALPACA_API_KEY')),
        ('secret_key', os.getenv('ALPACA_SECRET_KEY')),
        ('paper', True),
        ('bar_timeframe', '4Hour'),  # Alpaca format
    )
    
    def __init__(self):
        super(AlpacaData, self).__init__()
        
        # Set Backtrader timeframe properly
        self._timeframe = bt.TimeFrame.Minutes
        self._compression = 240  # 240 minutes = 4 hours
        
        # Initialize Alpaca API
        base_url = 'https://paper-api.alpaca.markets' if self.p.paper else 'https://api.alpaca.markets'
        
        self.api = tradeapi.REST(
            self.p.api_key,
            self.p.secret_key,
            base_url,
            api_version='v2'
        )
        
        self.data_df = None
        self.data_idx = 0
    
    def start(self):
        super(AlpacaData, self).start()
        self._load_data()
    
    def _load_data(self):
        """Fetch data from Alpaca"""
        
        try:
            # Format dates properly (date only, no time)
            start_date = self.p.fromdate.strftime('%Y-%m-%d') if self.p.fromdate else None
            end_date = self.p.todate.strftime('%Y-%m-%d') if self.p.todate else None
            
            print(f"   Fetching from {start_date} to {end_date}...")
            
            bars = self.api.get_bars(
                self._dataname,
                self.p.bar_timeframe,
                start=start_date,
                end=end_date,
                limit=10000
            )
            
            if bars.df.empty:
                print(f"⚠️  No data returned for {self._dataname}")
                return False
            
            # Convert to DataFrame
            self.data_df = bars.df
            
            # Handle multi-index
            if isinstance(self.data_df.index, pd.MultiIndex):
                self.data_df = self.data_df.reset_index(level='symbol', drop=True)
            
            # Ensure datetime index
            if not isinstance(self.data_df.index, pd.DatetimeIndex):
                self.data_df.index = pd.to_datetime(self.data_df.index)
            
            # Sort
            self.data_df = self.data_df.sort_index()
            
            print(f"✅ Loaded {len(self.data_df)} bars for {self._dataname}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error fetching data: {e}")
            return False
    
    def _load(self):
        """Load next bar"""
        
        if self.data_df is None or self.data_idx >= len(self.data_df):
            return False
        
        bar = self.data_df.iloc[self.data_idx]
        
        # Set OHLCV
        self.lines.datetime[0] = bt.date2num(self.data_df.index[self.data_idx])
        self.lines.open[0] = float(bar['open'])
        self.lines.high[0] = float(bar['high'])
        self.lines.low[0] = float(bar['low'])
        self.lines.close[0] = float(bar['close'])
        self.lines.volume[0] = float(bar['volume'])
        self.lines.openinterest[0] = 0
        
        self.data_idx += 1
        
        return True


def get_alpaca_data(symbol, fromdate, todate, timeframe='4H', paper=True):
    """
    Helper to create Alpaca data feed
    
    Args:
        symbol: Stock symbol
        fromdate: Start date (datetime)
        todate: End date (datetime)
        timeframe: '1H', '4H', '1D', etc.
        paper: Use paper trading
    """
    
    # Convert timeframe to Alpaca format
    timeframe_map = {
        '1Min': '1Min',
        '5Min': '5Min',
        '15Min': '15Min',
        '1H': '1Hour',
        '4H': '4Hour',
        '1D': '1Day',
    }
    
    alpaca_tf = timeframe_map.get(timeframe, '4Hour')
    
    data = AlpacaData(
        dataname=symbol,
        fromdate=fromdate,
        todate=todate,
        bar_timeframe=alpaca_tf,
        paper=paper
    )
    
    return data


if __name__ == '__main__':
    """Test the data feed"""
    
    print("\n" + "="*70)
    print("🧪 Testing Alpaca Data Feed")
    print("="*70 + "\n")
    
    api_key = os.getenv('ALPACA_API_KEY')
    secret_key = os.getenv('ALPACA_SECRET_KEY')
    
    if not api_key or not secret_key:
        print("❌ Alpaca API keys not found!")
        print("Please set ALPACA_API_KEY and ALPACA_SECRET_KEY in .env file")
        exit(1)
    
    print("✅ API keys found")
    
    try:
        api = tradeapi.REST(
            api_key,
            secret_key,
            'https://paper-api.alpaca.markets',
            api_version='v2'
        )
        
        symbol = 'SPY'
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        print(f"\n📊 Fetching {symbol} data...")
        print(f"   Period: {start_date.date()} to {end_date.date()}")
        
        bars = api.get_bars(
            symbol,
            '4Hour',
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d'),
            limit=1000
        )
        
        if not bars.df.empty:
            df = bars.df
            if isinstance(df.index, pd.MultiIndex):
                df = df.reset_index(level='symbol', drop=True)
            
            print(f"\n✅ Successfully fetched {len(df)} bars")
            print(f"\nSample (last 5):")
            print(df[['open', 'high', 'low', 'close', 'volume']].tail())
            
            print("\n" + "="*70)
            print("✅ Data feed working! Run backtest with:")
            print("  cd backtrader && python backtest_runner.py")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
