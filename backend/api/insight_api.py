"""
InsightSentry REST API Client

Purpose: Fetch historical OHLCV data from InsightSentry REST API.
Implements caching to minimize API calls and respect rate limits.

Tested & Working (from PLAN.md):
- Endpoint: GET /v3/symbols/{symbol}/series
- Successfully fetched 1000+ bars for CME_MINI:MNQ1!
- Returns up to 20,000 bars (Pro plan)
"""

import os
import logging
import requests
from typing import List, Optional
import time
from datetime import datetime

from .cache import OHLCV, get_cache
from .rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


class InsightSentryAPI:
    """
    Client for InsightSentry REST API with caching and rate limiting.
    """

    BASE_URL = "https://api.insightsentry.com"

    # Timeframe mapping: UI string → API parameters
    TIMEFRAME_MAP = {
        "1m": ("minute", 1),
        "5m": ("minute", 5),
        "15m": ("minute", 15),
        "30m": ("minute", 30),
        "1H": ("minute", 60),
        "4H": ("minute", 240),
        "1D": ("day", 1),
        "1W": ("day", 7),     # This might need adjustment based on API support
        "1M": ("day", 30)     # This might need adjustment based on API support
    }

    def __init__(self, api_key: str):
        """
        Initialize API client.

        Args:
            api_key: InsightSentry API key (works for both REST and WebSocket)
        """
        self.api_key = api_key
        self.cache = get_cache()
        self.rate_limiter = RateLimiter(rate_limit=25, period=60)  # 25 requests/minute (Pro plan)
        logger.info("Initialized InsightSentryAPI client")

    def fetch_historical_data(
        self,
        symbol: str,
        timeframe: str,
        bars: int = 1000
    ) -> List[OHLCV]:
        """
        Fetch historical OHLCV data for symbol and timeframe.

        Implements caching:
        - Checks cache first
        - Fetches from API if cache miss
        - Stores in cache after fetching

        Args:
            symbol: Trading symbol (e.g., "CME_MINI:MNQ1!")
            timeframe: Timeframe string (1m, 5m, 15m, 30m, 1H, 4H, 1D, 1W, 1M)
            bars: Number of bars to fetch (max 20,000 for Pro plan)

        Returns:
            List of OHLCV bars

        Raises:
            ValueError: Invalid timeframe
            requests.HTTPError: API request failed
        """
        if timeframe not in self.TIMEFRAME_MAP:
            raise ValueError(f"Invalid timeframe: {timeframe}")

        # Check cache first
        cached = self.cache.get(symbol, timeframe)
        if cached is not None:
            logger.info(f"Cache hit for {symbol} {timeframe}, returning {len(cached)} bars")
            return cached[-bars:]  # Return requested number of bars

        # Cache miss - fetch from API
        logger.info(f"Cache miss for {symbol} {timeframe}, fetching from API")

        # Respect rate limit
        self.rate_limiter.wait_if_needed()

        # Convert timeframe to API parameters
        bar_type, bar_interval = self.TIMEFRAME_MAP[timeframe]

        # Build request
        url = f"{self.BASE_URL}/v3/symbols/{symbol}/series"
        params = {
            "bar_type": bar_type,
            "bar_interval": bar_interval,
            "data_points": bars,
            "extended": True
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        try:
            # Make request
            logger.debug(f"Requesting: {url} with params {params}")
            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()
            logger.info(f"Received response from API: {len(data.get('series', []))} bars")

            # Parse response
            ohlcv_bars = self._parse_response(data)

            # Store in cache
            self.cache.set(symbol, timeframe, ohlcv_bars)

            return ohlcv_bars

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error fetching data: {e}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise

    def _parse_response(self, data: dict) -> List[OHLCV]:
        """
        Parse API response into OHLCV objects.

        Args:
            data: Response JSON from API

        Returns:
            List of OHLCV bars

        Expected format:
        {
          "code": "CME_MINI:MNQ1!",
          "bar_type": "1m",
          "series": [
            {
              "time": 1733432340.0,
              "open": 242.89,
              "high": 243.09,
              "low": 242.82,
              "close": 243.08,
              "volume": 533779.0
            }
          ]
        }
        """
        if "series" not in data:
            raise ValueError(f"Invalid response format: 'series' key missing")

        bars = []
        for bar_data in data["series"]:
            bar = OHLCV(
                time=bar_data["time"],
                open=bar_data["open"],
                high=bar_data["high"],
                low=bar_data["low"],
                close=bar_data["close"],
                volume=bar_data["volume"]
            )
            bars.append(bar)

        return bars

    def fetch_real_time_quote(self, symbol: str) -> dict:
        """
        Fetch real-time quote data for a symbol.

        Args:
            symbol: Trading symbol

        Returns:
            Quote data dictionary

        Raises:
            requests.HTTPError: API request failed
        """
        logger.debug(f"Fetching real-time quote for {symbol}")

        # Respect rate limit
        self.rate_limiter.wait_if_needed()

        url = f"{self.BASE_URL}/v3/symbols/quotes"
        params = {"codes": symbol}
        headers = {"Authorization": f"Bearer {self.api_key}"}

        try:
            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()
            logger.debug(f"Received quote data: {data.get('last_update')}")

            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching quote: {e}")
            raise

    def get_symbol_info(self, symbol: str) -> dict:
        """
        Fetch detailed symbol information.

        Args:
            symbol: Trading symbol

        Returns:
            Symbol information dictionary

        Raises:
            requests.HTTPError: API request failed
        """
        logger.debug(f"Fetching symbol info for {symbol}")

        # Respect rate limit
        self.rate_limiter.wait_if_needed()

        url = f"{self.BASE_URL}/v3/symbols/{symbol}/info"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()
            logger.debug(f"Received symbol info: {data.get('name')}")

            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching symbol info: {e}")
            raise


def get_api_client() -> InsightSentryAPI:
    """
    Get global API client instance (singleton pattern).

    Reads API key from environment variable: INSIGHTSENTRY_API_KEY

    Returns:
        InsightSentryAPI instance

    Raises:
        ValueError: API key not found in environment
    """
    from config import get_settings
    settings = get_settings()
    api_key = settings.INSIGHTSENTRY_API_KEY

    return InsightSentryAPI(api_key)
