"""
Pydantic Data Models

Purpose: Data validation and serialization schemas for API requests/responses.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class OHLCVModel(BaseModel):
    """OHLCV bar model for API responses"""

    time: float = Field(..., description="Unix timestamp")
    open: float = Field(..., description="Open price")
    high: float = Field(..., description="High price")
    low: float = Field(..., description="Low price")
    close: float = Field(..., description="Close price")
    volume: float = Field(..., description="Volume")

    class Config:
        json_schema_extra = {
            "example": {
                "time": 1733432340.0,
                "open": 242.89,
                "high": 243.09,
                "low": 242.82,
                "close": 243.08,
                "volume": 533779.0
            }
        }


class ChartHistoryRequest(BaseModel):
    """Request model for historical chart data"""

    symbol: str = Field(..., description="Trading symbol (e.g., CME_MINI:MNQ1!)")
    timeframe: str = Field(..., description="Timeframe (1m, 5m, 15m, 30m, 1H, 4H, 1D, 1W, 1M)")
    bars: int = Field(default=1000, ge=1, le=20000, description="Number of bars to fetch")

    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "CME_MINI:MNQ1!",
                "timeframe": "1H",
                "bars": 1000
            }
        }


class ChartHistoryResponse(BaseModel):
    """Response model for historical chart data"""

    symbol: str
    timeframe: str
    bars: List[OHLCVModel]
    count: int
    cached: bool = Field(description="Whether data was retrieved from cache")


class TimeframeStats(BaseModel):
    """Statistics for a timeframe"""

    symbol: str
    timeframe: str
    bars_loaded: int
    last_update: Optional[float] = Field(None, description="Unix timestamp of last update")


class ConnectionStatus(BaseModel):
    """WebSocket connection status"""

    status: str = Field(..., description="Connection status: connected, connecting, disconnected, error")
    symbol: Optional[str] = None
    message: Optional[str] = None
