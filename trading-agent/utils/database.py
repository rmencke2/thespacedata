"""
Database utilities for logging trades and performance
"""
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import pandas as pd
from utils.config import Config

class TradingDatabase:
    """SQLite database for trade logging"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or Config.DATABASE_PATH
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Trades table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                quantity REAL NOT NULL,
                entry_price REAL NOT NULL,
                exit_price REAL,
                stop_loss REAL,
                strategy TEXT NOT NULL,
                status TEXT NOT NULL,
                pnl REAL,
                pnl_percent REAL,
                exit_timestamp TEXT,
                notes TEXT
            )
        ''')
        
        # Daily performance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_performance (
                date TEXT PRIMARY KEY,
                starting_equity REAL NOT NULL,
                ending_equity REAL NOT NULL,
                daily_return REAL NOT NULL,
                num_trades INTEGER NOT NULL,
                winning_trades INTEGER NOT NULL,
                losing_trades INTEGER NOT NULL,
                total_pnl REAL NOT NULL
            )
        ''')
        
        # Positions table (current open positions)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                symbol TEXT PRIMARY KEY,
                quantity REAL NOT NULL,
                entry_price REAL NOT NULL,
                current_price REAL NOT NULL,
                stop_loss REAL NOT NULL,
                strategy TEXT NOT NULL,
                entry_timestamp TEXT NOT NULL,
                unrealized_pnl REAL NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def log_trade(self, trade: Dict) -> int:
        """Log a new trade"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO trades (
                timestamp, symbol, side, quantity, entry_price,
                stop_loss, strategy, status, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            trade.get('timestamp', datetime.now().isoformat()),
            trade['symbol'],
            trade['side'],
            trade['quantity'],
            trade['entry_price'],
            trade.get('stop_loss'),
            trade['strategy'],
            trade.get('status', 'open'),
            trade.get('notes', '')
        ))
        
        trade_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return trade_id
    
    def close_trade(self, trade_id: int, exit_price: float, exit_timestamp: str = None):
        """Close a trade and calculate P&L"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get trade details
        cursor.execute('SELECT entry_price, quantity, side FROM trades WHERE id = ?', (trade_id,))
        result = cursor.fetchone()
        
        if result:
            entry_price, quantity, side = result
            
            # Calculate P&L
            if side == 'buy':
                pnl = (exit_price - entry_price) * quantity
                pnl_percent = ((exit_price - entry_price) / entry_price) * 100
            else:  # short
                pnl = (entry_price - exit_price) * quantity
                pnl_percent = ((entry_price - exit_price) / entry_price) * 100
            
            cursor.execute('''
                UPDATE trades 
                SET exit_price = ?, exit_timestamp = ?, 
                    pnl = ?, pnl_percent = ?, status = 'closed'
                WHERE id = ?
            ''', (
                exit_price,
                exit_timestamp or datetime.now().isoformat(),
                pnl,
                pnl_percent,
                trade_id
            ))
            
            conn.commit()
        
        conn.close()
    
    def update_position(self, symbol: str, position: Dict):
        """Update current position"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO positions (
                symbol, quantity, entry_price, current_price,
                stop_loss, strategy, entry_timestamp, unrealized_pnl
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            symbol,
            position['quantity'],
            position['entry_price'],
            position['current_price'],
            position['stop_loss'],
            position['strategy'],
            position['entry_timestamp'],
            position['unrealized_pnl']
        ))
        
        conn.commit()
        conn.close()
    
    def remove_position(self, symbol: str):
        """Remove a position (when closed)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM positions WHERE symbol = ?', (symbol,))
        conn.commit()
        conn.close()
    
    def get_open_positions(self) -> List[Dict]:
        """Get all open positions"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query('SELECT * FROM positions', conn)
        conn.close()
        return df.to_dict('records') if not df.empty else []
    
    def get_open_trades(self) -> List[Dict]:
        """Get all open trades"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query('SELECT * FROM trades WHERE status = "open"', conn)
        conn.close()
        return df.to_dict('records') if not df.empty else []
    
    def log_daily_performance(self, date: str, performance: Dict):
        """Log daily performance"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO daily_performance (
                date, starting_equity, ending_equity, daily_return,
                num_trades, winning_trades, losing_trades, total_pnl
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            date,
            performance['starting_equity'],
            performance['ending_equity'],
            performance['daily_return'],
            performance['num_trades'],
            performance['winning_trades'],
            performance['losing_trades'],
            performance['total_pnl']
        ))
        
        conn.commit()
        conn.close()
    
    def get_performance_summary(self, days: int = 30) -> Dict:
        """Get performance summary"""
        conn = sqlite3.connect(self.db_path)
        
        # Get trades
        trades_df = pd.read_sql_query(
            'SELECT * FROM trades WHERE status = "closed" ORDER BY timestamp DESC LIMIT ?',
            conn,
            params=(days * 10,)  # Rough estimate of trades per day
        )
        
        # Get daily performance
        daily_df = pd.read_sql_query(
            'SELECT * FROM daily_performance ORDER BY date DESC LIMIT ?',
            conn,
            params=(days,)
        )
        
        conn.close()
        
        if trades_df.empty:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'best_trade': 0,
                'worst_trade': 0,
                'avg_pnl_percent': 0
            }
        
        winning_trades = trades_df[trades_df['pnl'] > 0]
        losing_trades = trades_df[trades_df['pnl'] < 0]
        
        return {
            'total_trades': len(trades_df),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': len(winning_trades) / len(trades_df) * 100 if len(trades_df) > 0 else 0,
            'total_pnl': trades_df['pnl'].sum(),
            'avg_win': winning_trades['pnl'].mean() if len(winning_trades) > 0 else 0,
            'avg_loss': losing_trades['pnl'].mean() if len(losing_trades) > 0 else 0,
            'best_trade': trades_df['pnl'].max(),
            'worst_trade': trades_df['pnl'].min(),
            'avg_pnl_percent': trades_df['pnl_percent'].mean()
        }
    
    def print_summary(self):
        """Print performance summary"""
        summary = self.get_performance_summary()
        positions = self.get_open_positions()
        
        print("\n" + "="*60)
        print("TRADING PERFORMANCE SUMMARY")
        print("="*60)
        print(f"Total Trades: {summary['total_trades']}")
        print(f"Winning Trades: {summary['winning_trades']}")
        print(f"Losing Trades: {summary['losing_trades']}")
        print(f"Win Rate: {summary['win_rate']:.2f}%")
        print(f"Total P&L: ${summary['total_pnl']:.2f}")
        print(f"Average Win: ${summary['avg_win']:.2f}")
        print(f"Average Loss: ${summary['avg_loss']:.2f}")
        print(f"Best Trade: ${summary['best_trade']:.2f}")
        print(f"Worst Trade: ${summary['worst_trade']:.2f}")
        print(f"\nOpen Positions: {len(positions)}")
        print("="*60 + "\n")


if __name__ == "__main__":
    # Test database
    db = TradingDatabase("test_trades.db")
    
    # Log a test trade
    trade = {
        'symbol': 'TSLA',
        'side': 'buy',
        'quantity': 10,
        'entry_price': 250.00,
        'stop_loss': 245.00,
        'strategy': 'mean_reversion'
    }
    
    trade_id = db.log_trade(trade)
    print(f"Logged trade ID: {trade_id}")
    
    # Close the trade
    db.close_trade(trade_id, 255.00)
    
    # Print summary
    db.print_summary()
