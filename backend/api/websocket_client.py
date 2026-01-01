"""
InsightSentry WebSocket Client

Purpose: Maintain WebSocket connection to InsightSentry for real-time 1m bars.
Broadcasts aggregated bars to frontend clients via backend WebSocket.

From PLAN.md (Tested & Working):
- Endpoint: wss://realtime.insightsentry.com/live
- Same API key works for WebSocket (no separate key needed!)
- Initial message: Status "Connecting..." → "Connected to W:ASIA-SOUTHEAST"
- Initial data burst: 100+ historical bars
- Continuous streaming: Real-time OHLCV updates
"""

import asyncio
import websockets
import json
import logging
from typing import Callable, Optional, Set
from datetime import datetime

from .cache import OHLCV, get_cache
from .aggregator import TimeframeAggregator, aggregate_historical_1m_to_timeframe

logger = logging.getLogger(__name__)


class InsightSentryWebSocketClient:
    """
    WebSocket client for InsightSentry real-time data.

    Features:
    - Auto-reconnection with exponential backoff
    - Aggregates 1m bars to all 9 timeframes
    - Broadcasts updates to connected frontend clients
    - Heartbeat/ping for connection health
    """

    WS_URL = "wss://realtime.insightsentry.com/live"

    def __init__(self, api_key: str, symbol: str = "CME_MINI:MNQ1!"):
        """
        Initialize WebSocket client.

        Args:
            api_key: InsightSentry API key (same as REST API key)
            symbol: Symbol to subscribe to (default: CME_MINI:MNQ1!)
        """
        self.api_key = api_key
        self.symbol = symbol
        self.aggregator = TimeframeAggregator()
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.is_connected = False

        # Callbacks for broadcasting to frontend clients
        self.on_bar_update: Optional[Callable[[str, list[OHLCV]], None]] = None

        # Reconnection settings
        self.max_reconnect_attempts = 5
        self.base_reconnect_delay = 1  # seconds
        self.reconnect_attempts = 0

        logger.info(f"Initialized WebSocket client for {symbol}")

    async def connect(self) -> None:
        """
        Connect to InsightSentry WebSocket and start streaming.

        Handles:
        - Connection with subscription
        - Status messages
        - Real-time bar updates
        - Aggregation to all timeframes
        - Auto-reconnection on disconnect
        """
        while self.reconnect_attempts < self.max_reconnect_attempts:
            try:
                logger.info(f"Connecting to {self.WS_URL} (attempt {self.reconnect_attempts + 1})...")

                self.websocket = await websockets.connect(self.WS_URL)
                self.is_connected = True
                self.reconnect_attempts = 0  # Reset on successful connection

                # Send subscription
                await self._subscribe()

                # Start message loop
                await self._message_loop()

            except websockets.exceptions.ConnectionClosed as e:
                logger.error(f"WebSocket connection closed: {e}")
                self.is_connected = False

                # Reconnect with exponential backoff
                self.reconnect_attempts += 1
                if self.reconnect_attempts < self.max_reconnect_attempts:
                    delay = self.base_reconnect_delay * (2 ** (self.reconnect_attempts - 1))
                    logger.info(f"Reconnecting in {delay} seconds...")
                    await asyncio.sleep(delay)

            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                self.is_connected = False
                break

    async def _subscribe(self, symbol: str = None) -> None:
        """Send subscription message to WebSocket."""
        target_symbol = symbol or self.symbol
        subscription = {
            "api_key": self.api_key,
            "subscriptions": [
                {
                    "code": target_symbol,
                    "type": "series",
                    "bar_type": "minute",
                    "bar_interval": 1
                }
            ]
        }

        await self.websocket.send(json.dumps(subscription))
        logger.info(f"Sent subscription for {target_symbol}")

    async def _unsubscribe(self, symbol: str) -> None:
        """Send unsubscribe message to WebSocket."""
        unsubscription = {
            "api_key": self.api_key,
            "action": "unsubscribe",
            "subscriptions": [
                {
                    "code": symbol,
                    "type": "series",
                    "bar_type": "minute",
                    "bar_interval": 1
                }
            ]
        }

        await self.websocket.send(json.dumps(unsubscription))
        logger.info(f"Sent unsubscription for {symbol}")

    async def _message_loop(self) -> None:
        """
        Main message loop - receives and processes WebSocket messages.

        Message types:
        - Status messages: {"message": "Connecting...", "Connected to W:..."}
        - Data messages: {"code": "...", "series": [...]}
        - Pong responses: "pong"
        """
        async for message in self.websocket:
            try:
                # Handle pong messages
                if message == "pong":
                    logger.debug("Received pong")
                    continue

                # Parse JSON
                data = json.loads(message)

                # Handle status messages
                if "message" in data:
                    logger.info(f"Status: {data['message']}")
                    continue

                # Handle bar data
                if "series" in data and len(data["series"]) > 0:
                    await self._process_bars(data["series"])

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse message: {e}")
                continue
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                continue

    async def _process_bars(self, bars_data: list) -> None:
        """
        Process incoming bar data.

        For initial burst (100+ bars):
        - Aggregate and cache for all timeframes

        For real-time updates:
        - Aggregate to all timeframes
        - Broadcast to frontend clients

        Args:
            bars_data: List of bar dictionaries from WebSocket
        """
        # Convert to OHLCV objects
        bars = [
            OHLCV(
                time=bar["time"],
                open=bar["open"],
                high=bar["high"],
                low=bar["low"],
                close=bar["close"],
                volume=bar["volume"]
            )
            for bar in bars_data
        ]

        logger.debug(f"Processing {len(bars)} bars from WebSocket")

        # Add each bar to aggregator (triggers aggregation to all timeframes)
        for bar in bars:
            aggregated = self.aggregator.add_1m_bar(bar)

            # Broadcast to frontend clients if callback registered
            if self.on_bar_update:
                for timeframe, timeframe_bars in aggregated.items():
                    if timeframe_bars:
                        await self.on_bar_update(timeframe, timeframe_bars)

    async def send_ping(self) -> None:
        """Send ping message to keep connection alive."""
        if self.websocket and self.is_connected:
            try:
                await self.websocket.send("ping")
                logger.debug("Sent ping")
            except Exception as e:
                logger.error(f"Error sending ping: {e}")

    async def close(self) -> None:
        """Close WebSocket connection."""
        if self.websocket:
            await self.websocket.close()
            self.is_connected = False
            logger.info("WebSocket connection closed")

    async def switch_symbol(self, new_symbol: str) -> None:
        """
        Switch WebSocket subscription to a different symbol.

        Unsubscribes from current symbol and subscribes to new symbol.
        Resets aggregator to start fresh data for new symbol.

        Args:
            new_symbol: New symbol to subscribe to
        """
        if not self.is_connected or not self.websocket:
            logger.error("Cannot switch symbol: WebSocket not connected")
            raise RuntimeError("WebSocket not connected")

        if new_symbol == self.symbol:
            logger.info(f"Already subscribed to {new_symbol}, skipping switch")
            return

        logger.info(f"Switching symbol from {self.symbol} to {new_symbol}")

        # Unsubscribe from old symbol
        await self._unsubscribe(self.symbol)

        # Update current symbol
        old_symbol = self.symbol
        self.symbol = new_symbol

        # Subscribe to new symbol
        await self._subscribe(new_symbol)

        # Reset aggregator for new symbol
        self.aggregator = TimeframeAggregator()
        logger.info(f"Aggregator reset for {new_symbol}")

        logger.info(f"Successfully switched from {old_symbol} to {new_symbol}")

    def set_bar_update_callback(self, callback: Callable[[str, list[OHLCV]], None]) -> None:
        """
        Set callback for bar updates (for broadcasting to frontend).

        Args:
            callback: Async function taking (timeframe, bars) arguments
        """
        self.on_bar_update = callback
        logger.info("Bar update callback registered")


async def heartbeat(websocket_client: InsightSentryWebSocketClient, interval: int = 15):
    """
    Send periodic pings to keep WebSocket connection alive.

    Args:
        websocket_client: WebSocket client instance
        interval: Ping interval in seconds (default: 15)
    """
    while websocket_client.is_connected:
        try:
            await asyncio.sleep(interval)
            await websocket_client.send_ping()
        except asyncio.CancelledError:
            logger.info("Heartbeat cancelled")
            break
        except Exception as e:
            logger.error(f"Heartbeat error: {e}")
            break
