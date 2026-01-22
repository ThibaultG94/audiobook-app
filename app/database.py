"""
Database module for storing conversion history.
"""

import sqlite3
import aiosqlite
from typing import List, Dict, Any

DATABASE_URL = "audiobook.db"

async def init_db():
    """Initialize the database."""
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS conversions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.commit()

async def save_conversion(filename: str, status: str = "pending") -> int:
    """Save a conversion record."""
    async with aiosqlite.connect(DATABASE_URL) as db:
        cursor = await db.execute(
            "INSERT INTO conversions (filename, status) VALUES (?, ?)",
            (filename, status)
        )
        await db.commit()
        return cursor.lastrowid

async def update_conversion_status(conversion_id: int, status: str):
    """Update conversion status."""
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute(
            "UPDATE conversions SET status = ? WHERE id = ?",
            (status, conversion_id)
        )
        await db.commit()

async def get_conversions() -> List[Dict[str, Any]]:
    """Get all conversions."""
    async with aiosqlite.connect(DATABASE_URL) as db:
        async with db.execute("SELECT * FROM conversions ORDER BY created_at DESC") as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
