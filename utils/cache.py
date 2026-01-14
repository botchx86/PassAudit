"""
HIBP Cache System
SQLite-based caching for Have I Been Pwned API results
"""

import sqlite3
import hashlib
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Tuple


class HIBPCache:
    """Cache for Have I Been Pwned API results"""

    def __init__(self, cache_dir: Optional[str] = None, expiration_days: int = 30):
        """
        Initialize HIBP cache

        Args:
            cache_dir: Directory for cache database (default: ~/.passaudit/)
            expiration_days: Days before cache entries expire (default: 30)
        """
        if cache_dir is None:
            cache_dir = str(Path.home() / ".passaudit")

        os.makedirs(cache_dir, exist_ok=True)
        self.db_path = os.path.join(cache_dir, "cache.db")
        self.expiration_days = expiration_days
        self._initialize_database()

    def _initialize_database(self):
        """Create database table if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hibp_cache (
                hash_prefix TEXT NOT NULL,
                hash_suffix TEXT NOT NULL,
                breach_count INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                PRIMARY KEY (hash_prefix, hash_suffix)
            )
        """)

        # Create index for faster lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp
            ON hibp_cache(timestamp)
        """)

        conn.commit()
        conn.close()

    def get(self, password: str) -> Optional[Tuple[bool, int]]:
        """
        Get cached HIBP result for password

        Args:
            password: Password to check

        Returns:
            Tuple of (is_pwned, breach_count) if cached and not expired, None otherwise
        """
        # Calculate hash
        sha1_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        hash_prefix = sha1_hash[:5]
        hash_suffix = sha1_hash[5:]

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check cache
        cursor.execute("""
            SELECT breach_count, timestamp
            FROM hibp_cache
            WHERE hash_prefix = ? AND hash_suffix = ?
        """, (hash_prefix, hash_suffix))

        result = cursor.fetchone()
        conn.close()

        if result is None:
            return None

        breach_count, timestamp_str = result

        # Check if expired
        timestamp = datetime.fromisoformat(timestamp_str)
        if datetime.now() - timestamp > timedelta(days=self.expiration_days):
            return None  # Expired

        # Return cached result
        is_pwned = breach_count > 0
        return (is_pwned, breach_count)

    def set(self, password: str, is_pwned: bool, breach_count: int):
        """
        Cache HIBP result for password

        Args:
            password: Password that was checked
            is_pwned: Whether password was found in breaches
            breach_count: Number of times password was breached
        """
        # Calculate hash
        sha1_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        hash_prefix = sha1_hash[:5]
        hash_suffix = sha1_hash[5:]

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Insert or replace cache entry
        cursor.execute("""
            INSERT OR REPLACE INTO hibp_cache
            (hash_prefix, hash_suffix, breach_count, timestamp)
            VALUES (?, ?, ?, ?)
        """, (hash_prefix, hash_suffix, breach_count, datetime.now().isoformat()))

        conn.commit()
        conn.close()

    def clear(self):
        """Clear all cache entries"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM hibp_cache")
        conn.commit()
        conn.close()

    def clear_expired(self):
        """Clear expired cache entries"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        expiration_date = datetime.now() - timedelta(days=self.expiration_days)

        cursor.execute("""
            DELETE FROM hibp_cache
            WHERE timestamp < ?
        """, (expiration_date.isoformat(),))

        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()

        return deleted_count

    def get_stats(self) -> dict:
        """
        Get cache statistics

        Returns:
            Dictionary with cache statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Total entries
        cursor.execute("SELECT COUNT(*) FROM hibp_cache")
        total_entries = cursor.fetchone()[0]

        # Expired entries
        expiration_date = datetime.now() - timedelta(days=self.expiration_days)
        cursor.execute("""
            SELECT COUNT(*) FROM hibp_cache
            WHERE timestamp < ?
        """, (expiration_date.isoformat(),))
        expired_entries = cursor.fetchone()[0]

        # Breached entries
        cursor.execute("""
            SELECT COUNT(*) FROM hibp_cache
            WHERE breach_count > 0
        """)
        breached_entries = cursor.fetchone()[0]

        conn.close()

        return {
            'total_entries': total_entries,
            'expired_entries': expired_entries,
            'breached_entries': breached_entries,
            'active_entries': total_entries - expired_entries
        }


# Global cache instance
_cache_instance = None


def get_cache(expiration_days: int = 30) -> HIBPCache:
    """
    Get global cache instance

    Args:
        expiration_days: Days before cache entries expire

    Returns:
        HIBPCache instance
    """
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = HIBPCache(expiration_days=expiration_days)
    return _cache_instance
