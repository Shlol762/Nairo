# For future database logic
import aiosqlite

class Database:
    def __init__(self, db_path):
        self.db_path = db_path

    async def initialize(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT NOT NULL UNIQUE,
                    value TEXT NOT NULL
                )
            """)
            await db.commit()

    async def set_value(self, key, value):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO memory (key, value) VALUES (?, ?)",
                (key, value)
            )
            await db.commit()

    async def get_value(self, key):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT value FROM memory WHERE key = ?", (key,)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None
