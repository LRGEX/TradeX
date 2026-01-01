"""
Data Cache Module

Purpose: In-memory caching layer for historical OHLCV data and aggregated bars.
Thread-safe implementation for FastAPI async operations.

Cache Structure: {(symbol, timeframe): [OHLCV bars]}
"""

from typing import List, Dict, Tuple, Optional
from threading import Lock
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class OHLCV:
    """OHLCV bar data model"""

    def __init__(self, time: float, open: float, high: float, low: float, close: float, volume: float):
        self.time = time
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "time": self.time,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume
        }

    @classmethod
    def from_dict(cls, data: dict) -> "OHLCV":
        """Create OHLCV from dictionary"""
        return cls(
            time=data["time"],
            open=data["open"],
            high=data["high"],
            low=data["low"],
            close=data["close"],
            volume=data["volume"]
        )

    def __repr__(self) -> str:
        return f"OHLCV(t={datetime.fromtimestamp(self.time).isoformat()}, O={self.open}, H={self.high}, L={self.low}, C={self.close}, V={self.volume})"


class DataCache:
    """
    Thread-safe in-memory cache for historical and aggregated OHLCV data.

    Features:
    - Cache key: (symbol, timeframe) tuple
    - Thread-safe operations with locks
    - Cache hit/miss tracking
    - Automatic timestamp tracking
    """

    def __init__(self):
        """Initialize empty cache with lock for thread safety"""
        self._cache: Dict[Tuple[str, str], List[OHLCV]] = {}
        self._lock = Lock()
        self._cache_hits = 0
        self._cache_misses = 0

    def get(self, symbol: str, timeframe: str) -> Optional[List[OHLCV]]:
        """
        Retrieve cached data for symbol and timeframe.

        Args:
            symbol: Trading symbol (e.g., "CME_MINI:MNQ1!")
            timeframe: Timeframe string (e.g., "1m", "5m", "1H", "1D")

        Returns:
            List of OHLCV bars if cached, None otherwise
        """
        key = (symbol, timeframe)

        with self._lock:
            if key in self._cache:
                self._cache_hits += 1
                logger.debug(f"Cache HIT: {symbol} {timeframe}")
                return self._cache[key]
            else:
                self._cache_misses += 1
                logger.debug(f"Cache MISS: {symbol} {timeframe}")
                return None

    def set(self, symbol: str, timeframe: str, bars: List[OHLCV]) -> None:
        """
        Store data in cache.

        Args:
            symbol: Trading symbol
            timeframe: Timeframe string
            bars: List of OHLCV bars to cache
        """
        key = (symbol, timeframe)

        with self._lock:
            self._cache[key] = bars
            logger.info(f"Cached {len(bars)} bars for {symbol} {timeframe}")

    def has(self, symbol: str, timeframe: str) -> bool:
        """
        Check if data is cached.

        Args:
            symbol: Trading symbol
            timeframe: Timeframe string

        Returns:
            True if cached, False otherwise
        """
        key = (symbol, timeframe)
        with self._lock:
            return key in self._cache

    def clear(self) -> None:
        """Clear all cached data"""
        with self._lock:
            self._cache.clear()
            logger.warning("Cache cleared")

    def get_stats(self) -> dict:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats (hits, misses, total_keys, hit_rate)
        """
        with self._lock:
            total_requests = self._cache_hits + self._cache_misses
            hit_rate = (self._cache_hits / total_requests * 100) if total_requests > 0 else 0

            return {
                "cache_hits": self._cache_hits,
                "cache_misses": self._cache_misses,
                "total_keys": len(self._cache),
                "hit_rate_percent": round(hit_rate, 2)
            }

    def list_cached_symbols(self) -> List[Tuple[str, str]]:
        """
        List all cached (symbol, timeframe) pairs.

        Returns:
            List of cached keys
        """
        with self._lock:
            return list(self._cache.keys())


# Global cache instance
_cache_instance = None


def get_cache() -> DataCache:
    """
    Get global cache instance (singleton pattern).

    Returns:
        Global DataCache instance
    """
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = DataCache()
        logger.info("Initialized global data cache")
    return _cache_instance
