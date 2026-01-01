"""
TradeX Backend Server

Purpose: FastAPI application that provides REST API and WebSocket proxy for real-time trading data.
Architecture: Single 1m WebSocket subscription → Aggregation to all 9 timeframes → Broadcast to frontend

Startup Sequence:
1. Load environment variables (.env)
2. Initialize data cache
3. Connect to InsightSentry WebSocket (1m bars)
4. Start aggregation loop
5. Start FastAPI server on port 8000
"""

import asyncio
import logging
from typing import Set
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import get_settings
from api.cache import get_cache, OHLCV
from api.insight_api import get_api_client, InsightSentryAPI
from api.websocket_client import InsightSentryWebSocketClient, heartbeat
from api.aggregator import aggregate_historical_1m_to_timeframe
from models.schemas import (
    ChartHistoryRequest,
    ChartHistoryResponse,
    OHLCVModel,
    TimeframeStats,
    ConnectionStatus
)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global state
cache = get_cache()
api_client: InsightSentryAPI = None
ws_client: InsightSentryWebSocketClient = None
frontend_clients: Set[WebSocket] = set()
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("=" * 60)
    logger.info("TradeX Backend Starting")
    logger.info("=" * 60)

    global api_client, ws_client

    try:
        # Initialize API client
        logger.info("Initializing InsightSentry API client...")
        api_client = get_api_client()
        logger.info(f"[OK] API client initialized")

        # Start InsightSentry WebSocket client
        logger.info("Starting InsightSentry WebSocket client...")
        ws_client = InsightSentryWebSocketClient(
            api_key=settings.INSIGHTSENTRY_API_KEY,
            symbol="CME_MINI:MNQ1!"
        )

        # Register callback for broadcasting to frontend
        async def broadcast_bar_update(timeframe: str, bars: list[OHLCV]):
            """Broadcast aggregated bars to all connected frontend clients."""
            if not frontend_clients:
                return

            message = {
                "type": "bar_update",
                "timeframe": timeframe,
                "bars": [bar.to_dict() for bar in bars]
            }

            # Send to all connected clients
            disconnected_clients = set()
            for client in frontend_clients:
                try:
                    await client.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending to client: {e}")
                    disconnected_clients.add(client)

            # Remove disconnected clients
            frontend_clients.difference_update(disconnected_clients)

        ws_client.set_bar_update_callback(broadcast_bar_update)

        # Start WebSocket client and heartbeat in background
        async def run_ws_client():
            """Run WebSocket client with auto-reconnection."""
            try:
                await ws_client.connect()
            except Exception as e:
                logger.error(f"WebSocket client error: {e}")

        async def run_heartbeat():
            """Run heartbeat to keep connection alive."""
            try:
                await heartbeat(ws_client, interval=15)
            except Exception as e:
                logger.error(f"Heartbeat error: {e}")

        # Start background tasks
        asyncio.create_task(run_ws_client())
        asyncio.create_task(run_heartbeat())

        logger.info(f"[OK] WebSocket client started for CME_MINI:MNQ1!")
        logger.info("=" * 60)
        logger.info("TradeX Backend Ready")
        logger.info(f"Server: http://localhost:{settings.BACKEND_PORT}")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Failed to start backend: {e}")
        raise

    yield

    # Shutdown
    logger.info("TradeX Backend shutting down...")
    if ws_client:
        await ws_client.close()
    logger.info("Backend shutdown complete")


# Initialize FastAPI app
app = FastAPI(
    title="TradeX Backend",
    description="Real-time trading chart API with WebSocket proxy",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== REST API Endpoints ====================

@app.get("/api/health")
async def health_check():
    """
    Health check endpoint.
    Returns backend status and connection info.
    """
    return {
        "status": "ok",
        "backend_port": settings.BACKEND_PORT,
        "frontend_port": settings.FRONTEND_PORT,
        "websocket_connected": ws_client.is_connected if ws_client else False,
        "cache_stats": cache.get_stats(),
        "connected_clients": len(frontend_clients)
    }


@app.get("/api/chart/history", response_model=ChartHistoryResponse)
async def get_chart_history(
    symbol: str = Query(..., description="Trading symbol (e.g., CME_MINI:MNQ1!)"),
    timeframe: str = Query(..., description="Timeframe (1m, 5m, 15m, 30m, 1H, 4H, 1D, 1W, 1M)"),
    bars: int = Query(default=1000, ge=1, le=20000, description="Number of bars to fetch")
):
    """
    Get historical OHLCV data for a symbol and timeframe.

    Implements caching:
    - Returns cached data if available
    - Fetches from InsightSentry API if cache miss
    - Aggregates 1m data to higher timeframes if needed
    """
    logger.info(f"Fetching history: {symbol} {timeframe} {bars} bars")

    try:
        # Check cache first
        cached = cache.get(symbol, timeframe)
        if cached is not None:
            logger.info(f"Cache hit for {symbol} {timeframe}")
            return ChartHistoryResponse(
                symbol=symbol,
                timeframe=timeframe,
                bars=[OHLCVModel(**bar.to_dict()) for bar in cached[-bars:]],
                count=len(cached[-bars:]),
                cached=True
            )

        # Cache miss - fetch from API
        logger.info(f"Cache miss for {symbol} {timeframe}, fetching from API")

        # Special handling for higher timeframes
        # For 1D, 1W, 1M: fetch 1m data and aggregate
        if timeframe in ["1D", "1W", "1M"]:
            logger.info(f"Fetching 1m data to aggregate to {timeframe}")
            bars_1m = api_client.fetch_historical_data(symbol, "1m", bars=bars * 1440)
            aggregated = aggregate_historical_1m_to_timeframe(bars_1m, timeframe)

            # Cache the aggregated result
            cache.set(symbol, timeframe, aggregated)

            return ChartHistoryResponse(
                symbol=symbol,
                timeframe=timeframe,
                bars=[OHLCVModel(**bar.to_dict()) for bar in aggregated[-bars:]],
                count=len(aggregated[-bars:]),
                cached=False
            )

        # For 1m - 4H: fetch directly from API
        ohlcv_bars = api_client.fetch_historical_data(symbol, timeframe, bars)

        return ChartHistoryResponse(
            symbol=symbol,
            timeframe=timeframe,
            bars=[OHLCVModel(**bar.to_dict()) for bar in ohlcv_bars],
            count=len(ohlcv_bars),
            cached=False
        )

    except ValueError as e:
        logger.error(f"Invalid request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching chart history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats/timeframe", response_model=TimeframeStats)
async def get_timeframe_stats(
    symbol: str = Query(..., description="Trading symbol"),
    timeframe: str = Query(..., description="Timeframe")
):
    """
    Get statistics for a cached timeframe.
    """
    has_data = cache.has(symbol, timeframe)
    bars = cache.get(symbol, timeframe)

    return TimeframeStats(
        symbol=symbol,
        timeframe=timeframe,
        bars_loaded=len(bars) if bars else 0,
        last_update=bars[-1].time if bars else None
    )


# ==================== WebSocket Endpoint ====================

@app.websocket("/ws/chart")
async def websocket_chart(websocket: WebSocket):
    """
    WebSocket endpoint for real-time chart updates.

    Broadcasts aggregated bar data for all timeframes to connected clients.
    Message format:
    {
        "type": "bar_update",
        "timeframe": "1H",
        "bars": [OHLCV...]
    }
    """
    await websocket.accept()
    frontend_clients.add(websocket)

    logger.info(f"Frontend client connected. Total clients: {len(frontend_clients)}")

    # Send connection status
    try:
        await websocket.send_json({
            "type": "connection_status",
            "status": "connected" if ws_client and ws_client.is_connected else "connecting",
            "symbol": "CME_MINI:MNQ1!",
            "message": "Connected to TradeX backend"
        })
    except Exception as e:
        logger.error(f"Error sending status: {e}")

    try:
        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive()

            # Handle client messages (if any)
            if "text" in data:
                message = data["text"]
                logger.debug(f"Received from client: {message}")

            # Handle ping/pong for connection health
            if "bytes" in data:
                # Echo back bytes for ping/pong
                await websocket.send_bytes(data["bytes"])

    except WebSocketDisconnect:
        logger.info("Frontend client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        frontend_clients.remove(websocket)
        logger.info(f"Client removed. Total clients: {len(frontend_clients)}")


# ==================== Error Handlers ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions with JSON response."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )


# ==================== Main Entry Point ====================

if __name__ == "__main__":
    import uvicorn

    logger.info("Starting TradeX backend server...")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.BACKEND_PORT,
        log_level=settings.LOG_LEVEL.lower(),
        reload=False  # Disable auto-reload in production
    )
