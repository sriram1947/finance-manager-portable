📄 FILE 4: database_sqlite.py
Click "Add file" → "Create new file" → Name it: database_sqlite.py → Paste this entire code:

"""SQLite database layer for desktop application."""
import aiosqlite
import os
from datetime import datetime, timezone
from typing import Optional, List, Dict
from pathlib import Path

# Database will be stored in user's AppData folder for Windows
DB_DIR = Path(os.environ.get('APPDATA', '.')) / 'FinanceManager'
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / 'finance.db'

class Database:
    def __init__(self):
        self.db_path = str(DB_PATH)
        self.connection = None
    
    async def connect(self):
        """Initialize database connection and create tables."""
        self.connection = await aiosqlite.connect(self.db_path)
        self.connection.row_factory = aiosqlite.Row
        await self.create_tables()
    
    async def create_tables(self):
        """Create all necessary tables."""
        async with self.connection.cursor() as cursor:
            # Users table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    name TEXT NOT NULL,
                    phone TEXT,
                    role TEXT DEFAULT 'user',
                    onboarded INTEGER DEFAULT 0,
                    initial_goal TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Transactions table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    type TEXT NOT NULL,
                    category TEXT NOT NULL,
                    amount REAL NOT NULL,
                    description TEXT,
                    date TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # Investments table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS investments (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    institution_type TEXT NOT NULL,
                    institution_name TEXT NOT NULL,
                    investment_amount REAL NOT NULL,
                    start_date TEXT NOT NULL,
                    maturity_date TEXT NOT NULL,
                    maturity_amount REAL NOT NULL,
                    notes TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # Custom institutions table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS custom_institutions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # Password reset tokens table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS password_reset_tokens (
                    id TEXT PRIMARY KEY,
                    token TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    used INTEGER DEFAULT 0,
                    expires_at TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # Notifications table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    message TEXT NOT NULL,
                    type TEXT NOT NULL,
                    read INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # Create indexes
            await cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
            await cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_user ON transactions(user_id, date DESC)")
            await cursor.execute("CREATE INDEX IF NOT EXISTS idx_investments_user ON investments(user_id, start_date DESC)")
            await cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id, created_at DESC)")
            await cursor.execute("CREATE INDEX IF NOT EXISTS idx_custom_inst_user ON custom_institutions(user_id, type)")
            
            await self.connection.commit()
    
    async def close(self):
        """Close database connection."""
        if self.connection:
            await self.connection.close()
    
    # Helper methods for common operations
    async def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict]:
        """Fetch single row."""
        async with self.connection.cursor() as cursor:
            await cursor.execute(query, params)
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def fetch_all(self, query: str, params: tuple = ()) -> List[Dict]:
        """Fetch all rows."""
        async with self.connection.cursor() as cursor:
            await cursor.execute(query, params)
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def execute(self, query: str, params: tuple = ()) -> int:
        """Execute query and return last row id."""
        async with self.connection.cursor() as cursor:
            await cursor.execute(query, params)
            await self.connection.commit()
            return cursor.lastrowid
    
    async def execute_many(self, query: str, params_list: List[tuple]) -> None:
        """Execute multiple queries."""
        async with self.connection.cursor() as cursor:
            await cursor.executemany(query, params_list)
            await self.connection.commit()

# Global database instance
db = Database()
