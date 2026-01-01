# TradeX Implementation Plan

## Overview
Building a real-time trading chart application for MNQ! (Micro Nasdaq 100 futures) using TradingView Lightweight Charts with dynamic WebSocket switching based on user-selected timeframe.

## Architecture

### Tech Stack
- **Backend**: Python with FastAPI (port 8000 per RULES.md)
- **Frontend**: HTML/JavaScript with Vite (port 3000 per RULES.md)
- **Chart Library**: TradingView Lightweight Charts
- **API**: InsightSentry REST API + WebSocket API

### Architecture Diagram
```
Frontend (Vite/JS) <--> Backend (FastAPI/Python) <--> InsightSentry API
     Port 3000              Port 8000                     (REST + WebSocket)
```

## Key Features

### 1. Smart Real-time Data Architecture
- **Only 1 WebSocket subscription** used (for 1-minute data)
- **1m WebSocket updates ALL timeframes live** by aggregating 1m bars
- All timeframes update simultaneously without switching

### 2. Timeframe Support
All 9 timeframes supported with live updates:
- 1m, 5m, 15m, 30m, 1H, 4H, 1D, 1W, 1M

### 3. Data Loading Strategy
- **Initial Load**: Fetch historical data via REST API for each timeframe (up to 20k points per PRO plan)
- **Real-time Updates**: 1m WebSocket data flows in → aggregated to update all higher timeframes live
- **Switching Timeframes**: Instant display (data already updating in background)
- **Aggregation Logic**:
  - 5m = 5 consecutive 1m bars
  - 15m = 15 consecutive 1m bars
  - 1H = 60 consecutive 1m bars
  - 4H = 240 consecutive 1m bars
  - 1D = 1440 consecutive 1m bars (market hours)
  - 1W = 5 days of 1D bars
  - 1M = Calendar month aggregation

## Current Implementation Status

### ✅ Completed
1. **Backend Setup**: Python with FastAPI using uv
2. **Configuration**: Environment variables and config management
3. **API Key Handling**: Using same API key for REST and WebSocket (per reference doc)
4. **Rate Limiting**: Token bucket algorithm implemented
5. **WebSocket Client**: Basic connection with reconnection logic
6. **Subscription Manager**: Dynamic subscription management for multiple symbols
7. **Modular Architecture**: Separated concerns across modules

### 🔄 In Progress
1. **Integration**: Connecting subscription manager with aggregator
2. **WebSocket Data Flow**: Ensuring data flows properly from InsightSentry to frontend

### ❌ Pending
1. **Frontend Implementation**: Vite + TradingView Lightweight Charts
2. **Aggregation Logic**: 1m bar aggregation to higher timeframes
3. **REST API Integration**: Historical data fetching and caching
4. **WebSocket Proxy**: Forwarding data to frontend via backend WebSocket
5. **Dynamic Symbol Management**: Adding/removing symbols on demand

## API Integration Details

### MNQ! Symbol Mapping
Per InsightSentry API documentation:
- Symbol format: `CME_MINI:MNQ1!` (continuous contract)
- Use `/v3/symbols/search` endpoint to verify exact symbol code

### REST API Usage
- **Historical Data**: `GET /v3/symbols/{symbol}/series`
  - Parameters: `bar_type` (minute/hour/day), `bar_interval` (1, 5, 15, etc.)
  - Returns: OHLCV data up to 20k points (PRO plan)

### WebSocket API Usage
- **Endpoint**: `wss://realtime.insightsentry.com/live`
- **Single Connection - 1m Bars Only**:
  ```json
  {
    "api_key": "<key>",
    "subscriptions": [
      {
        "code": "CME_MINI:MNQ1!",
        "type": "series",
        "bar_type": "minute",
        "bar_interval": 1,
        "recent_bars": true
      }
    ]
  }
  ```

## Data Flow

### Application Startup
1. Backend connects to InsightSentry WebSocket (1m data only)
2. Frontend connects to backend WebSocket
3. Backend starts receiving 1m bars and aggregating to all timeframes

### Initial Load (User Opens App)
1. Frontend requests historical data for default timeframe (e.g., 1D): `GET /api/chart/history?timeframe=1D`
2. Backend fetches from InsightSentry REST API
3. **Backend caches the historical data in memory**
4. Backend returns OHLCV bars to frontend
5. Frontend renders chart with historical data
6. **Cached data persists for entire app session** (until backend restarts)

### Real-time Updates (Continuous)
1. New 1m bar arrives from WebSocket
2. Backend aggregates to all higher timeframes:
   - Updates current 1m bar
   - Updates current 5m bar (after 5 bars)
   - Updates current 15m bar (after 15 bars)
   - Updates current 30m bar (after 30 bars)
   - Updates current 1H bar (after 60 bars)
   - Updates current 4H bar (after 240 bars)
   - Updates current 1D bar (after day closes)
3. Backend sends ALL updated timeframe bars to frontend
4. Frontend updates its cached data for all timeframes
5. If user is viewing a timeframe, chart updates automatically

### Timeframe Switch (Instant)
1. User clicks different timeframe (e.g., switches from 1D to 5m)
2. Backend checks cache for 5m historical data
   - **If cached**: Return cached data instantly
   - **If not cached**: Fetch from REST API once, cache it, then return
3. Frontend displays data immediately
4. No WebSocket reconnection needed (already receiving updates)
5. **Historical data fetched once per timeframe, cached for entire session**

## Rate Limiting (CRITICAL)

### PRO Plan Limits
- REST API: 25 requests per minute
- REST API: 50k requests per month
- WebSocket: 300 subscription messages per 5 minutes

### Rate Limiting Strategy
1. **Token Bucket Algorithm** for REST API rate limiting
   - Maximum 25 requests per minute = ~1 request every 2.4 seconds
   - Implement burst allowance with gradual refill
   - Track usage metrics to prevent monthly quota exhaustion

2. **WebSocket Subscription Rate Limiting**
   - Maximum 300 subscription messages per 5 minutes
   - Implement backoff if limit approached
   - Cache active subscriptions to minimize changes

3. **Caching to Minimize API Calls**
   - All historical data cached after first fetch
   - No repeated REST API calls for same timeframe
   - Aggregation uses cached data, not API calls

## Configuration

### Environment Variables
```bash
# Backend
INSIGHTSENTRY_API_KEY=your_api_key_here
INSIGHTSENTRY_WS_API_KEY=your_ws_api_key  # For RapidAPI users (same as REST for direct)
BACKEND_PORT=8000
FRONTEND_PORT=3000

# Frontend (in .env)
VITE_API_URL=http://localhost:8000
```

## File Structure

### Backend
```
backend/
├── main.py                 # FastAPI app entry point
├── run.py                  # Entry point for uvicorn
├── api/
│   ├── insight_api.py     # REST API client
│   ├── websocket_client.py # WebSocket connection manager
│   ├── aggregator.py       # 1m → higher timeframe aggregation
│   ├── subscription_manager.py # Dynamic subscription management
│   └── rate_limiter.py     # Rate limiting to prevent API bans
├── models/
│   └── schemas.py          # Pydantic models for API data
├── config.py              # Configuration management
├── .env                   # Environment variables
└── requirements.txt       # Python dependencies
```

### Frontend (To be created)
```
frontend/
├── index.html
├── src/
│   ├── main.js             # Vite entry point
│   ├── chart.js            # TradingView chart setup
│   ├── api.js              # Backend API client
│   └── websocket.js        # WebSocket connection handler
├── package.json
└── vite.config.js
```

## Next Steps

1. **Complete WebSocket Integration**
   - Fix current connection issues
   - Ensure data flows from InsightSentry to subscription manager
   - Test with actual MNQ! data

2. **Implement Aggregation Logic**
   - Create bar aggregation from 1m to all higher timeframes
   - Ensure real-time updates work correctly
   - Add caching for aggregated data

3. **Build Frontend**
   - Initialize Vite project
   - Set up TradingView Lightweight Charts
   - Implement WebSocket client for backend connection
   - Create timeframe selector UI

4. **Connect Frontend to Backend**
   - Implement REST API calls for historical data
   - Connect to backend WebSocket for real-time updates
   - Handle dynamic data updates for all timeframes

5. **Testing & Optimization**
   - Test with multiple symbols
   - Verify rate limiting works
   - Optimize performance and memory usage
   - Add error handling and logging