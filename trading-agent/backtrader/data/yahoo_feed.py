"""
Yahoo Finance Data Feed for Backtrader - FIXED
"""
import backtrader as bt
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

class YahooFinanceData(bt.DataBase):
    """Yahoo Finance Data Feed for Backtrader"""
    
    params = (
        ('timeframe', '1h'),
        ('aggregate_to', '4h'),
    )
    
    def __init__(self):
        super(YahooFinanceData, self).__init__()
        
        # CRITICAL: Set timeframe as Backtrader constant, not string
        if self.p.aggregate_to == '4h':
            self.lines.datetime._settz(None)
            # Don't set _timeframe at all - let Backtrader handle it
        
        self.data_df = None
        self.data_idx = 0
    
    def start(self):
        super(YahooFinanceData, self).start()
        self._load_data()
    
    def _load_data(self):
        """Fetch data from Yahoo Finance"""
        
        try:
            if self.p.fromdate and self.p.todate:
                start_date = self.p.fromdate
                end_date = self.p.todate
            else:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=365)
            
            print(f"   Fetching from Yahoo Finance...")
            print(f"   {start_date.date()} to {end_date.date()}")
            
            ticker = yf.Ticker(self._dataname)
            
            df = ticker.history(
                start=start_date,
                end=end_date,
                interval=self.p.timeframe,
                auto_adjust=True
            )
            
            if df.empty:
                print(f"⚠️  No data returned for {self._dataname}")
                return False
            
            df.columns = df.columns.str.lower()
            
            # Aggregate to 4h if requested
            if self.p.aggregate_to == '4h' and self.p.timeframe == '1h':
                print(f"   Aggregating 1H → 4H candles...")
                df = df.resample('4h').agg({
                    'open': 'first',
                    'high': 'max',
                    'low': 'min',
                    'close': 'last',
                    'volume': 'sum'
                }).dropna()
            
            self.data_df = df
            
            print(f"✅ Loaded {len(self.data_df)} bars for {self._dataname}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error fetching data: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _load(self):
        """Load next bar"""
        
        if self.data_df is None or self.data_idx >= len(self.data_df):
            return False
        
        bar = self.data_df.iloc[self.data_idx]
        
        self.lines.datetime[0] = bt.date2num(self.data_df.index[self.data_idx])
        self.lines.open[0] = float(bar['open'])
        self.lines.high[0] = float(bar['high'])
        self.lines.low[0] = float(bar['low'])
        self.lines.close[0] = float(bar['close'])
        self.lines.volume[0] = float(bar['volume'])
        self.lines.openinterest[0] = 0
        
        self.data_idx += 1
        
        return True


if __name__ == '__main__':
    """Test the data feed"""
    
    print("\n" + "="*70)
    print("🧪 Testing Yahoo Finance Data Feed")
    print("="*70 + "\n")
    
    symbol = 'SPY'
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    print(f"📊 Fetching {symbol} data...")
    print(f"   Period: {start_date.date()} to {end_date.date()}")
    
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(
            start=start_date,
            end=end_date,
            interval='1h'
        )
        
        if not df.empty:
            df.columns = df.columns.str.lower()
            df_4h = df.resample('4h').agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum'
            }).dropna()
            
            print(f"\n✅ Successfully fetched {len(df)} 1H bars")
            print(f"✅ Aggregated to {len(df_4h)} 4H bars")
            
            print(f"\nSample (last 5):")
            print(df_4h[['open', 'high', 'low', 'close', 'volume']].tail())
            
            print("\n" + "="*70)
            print("✅ Yahoo Finance working!")
            print("Run: python backtest_runner_yahoo.py")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
