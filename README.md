# TradeX

<div align="center">
  <h3>Real-time Trading Chart Application</h3>
  <p>Professional-grade trading charts with real-time data streaming</p>
</div>

---

## Overview

**TradeX** is a modern real-time trading chart application built with Python FastAPI backend and Vite frontend, featuring TradingView Lightweight Charts for professional-grade visualization. The application provides real-time OHLCV (Open, High, Low, Close, Volume) data streaming with smart timeframe aggregation.

## Features

✅ **Real-time Data Streaming**
- WebSocket connection to InsightSentry for live 1-minute bars
- Smart aggregation: Single 1m subscription updates all 9 timeframes
- Automatic reconnection on connection loss

✅ **Multi-Timeframe Support**
- 9 timeframes: 1m, 5m, 15m, 30m, 1H, 4H, 1D, 1W, 1M
- Instant switching between timeframes
- Historical data caching for fast loading

✅ **Professional UI/UX**
- Dark theme designed for trading terminals
- Gradient branding (teal to blue)
- Real-time connection status indicator
- Stats cards showing key metrics
- Responsive design (desktop + mobile)

✅ **Smart Architecture**
- REST API with rate limiting (25 req/min)
- In-memory caching for API efficiency
- Token bucket rate limiter
- Modular, maintainable codebase

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.14+)
- **WebSocket**: `websockets` library
- **Data Provider**: InsightSentry API
- **Validation**: Pydantic v2
- **Rate Limiting**: Token bucket algorithm

### Frontend
- **Framework**: Vite + Vanilla JavaScript
- **Charting**: TradingView Lightweight Charts v5.1.0
- **Styling**: Embedded CSS (no external CSS frameworks)
- **Build Tool**: Vite

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    FRONTEND                         │
│               (Vite + Vanilla JS)                   │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  │
│  │ Chart      │  │ WebSocket  │  │ REST API   │  │
│  │ (TradingView)│  │ Client     │  │ Client     │  │
│  └────────────┘  └────────────┘  └────────────┘  │
└─────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│                    BACKEND                          │
│               (FastAPI on port 8000)               │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  │
│  │ WebSocket  │  │  REST API  │  │   Cache    │  │
│  │ Proxy      │  │  Endpoint  │  │   Layer    │  │
│  └────────────┘  └────────────┘  └────────────┘  │
│                                                       │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  │
│  │ Insight    │→ │ Aggregator │→ │ Rate       │  │
│  │ Sentry     │  │ (1m→9 TF)  │  │ Limiter    │  │
│  │ WebSocket  │  │            │  │            │  │
│  └────────────┘  └────────────┘  └────────────┘  │
└─────────────────────────────────────────────────────┘
                       ↓
              ┌──────────────────┐
              │  InsightSentry   │
              │      API         │
              └──────────────────┘
```

## Installation

### Prerequisites
- Python 3.14+
- Node.js 18+
- InsightSentry API key ([Get one here](https://insightsentry.com))

### Backend Setup

```bash
cd backend

# Install dependencies
pip install fastapi uvicorn websockets requests pydantic pydantic-settings

# Configure environment
cp .env.example .env

# Edit .env and add your API key
# INSIGHTSENTRY_API_KEY=your_api_key_here

# Start backend server (port 8000)
python main.py
```

Backend will be available at: **http://localhost:8000**

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server (port 3000)
npm run dev
```

Frontend will be available at: **http://localhost:3000**

## Usage

1. **Open the application**: Navigate to `http://localhost:3000`

2. **View real-time data**:
   - The chart loads automatically with CME_MINI:MNQ1! (Micro Nasdaq 100 futures)
   - Default timeframe: 1H
   - Real-time bars stream live

3. **Switch timeframes**: Use the dropdown to select any of 9 timeframes

4. **Change symbols**: Type a new symbol and press Enter (e.g., `CME_MINI:ES1!`)

5. **Monitor stats**: Watch the stats cards update in real-time

## API Configuration

### InsightSentry API Key

TradeX uses InsightSentry for market data. You'll need an API key:

1. Sign up at [insightsentry.com](https://insightsentry.com)
2. Get your API key from the dashboard
3. Add it to `backend/.env`:
   ```
   INSIGHTSENTRY_API_KEY=your_api_key_here
   ```

**Note**: The same API key works for both REST API and WebSocket (tested and verified).

### Rate Limits

- **Pro Plan**: 25 requests per minute
- **WebSocket**: 2 concurrent subscriptions
- **Data Points**: Up to 20,000 bars per request

TradeX implements caching and rate limiting to stay within these limits.

## Project Structure

```
TradeX/
├── backend/
│   ├── main.py                 # FastAPI app + WebSocket proxy
│   ├── config.py               # Environment configuration
│   ├── requirements.txt        # Python dependencies
│   ├── .env                    # API keys (not in git)
│   ├── .env.example            # Configuration template
│   ├── models/
│   │   └── schemas.py          # Pydantic data models
│   └── api/
│       ├── cache.py            # In-memory data cache
│       ├── aggregator.py      # 1m → 9 timeframe aggregation
│       ├── insight_api.py      # InsightSentry REST client
│       ├── websocket_client.py # InsightSentry WebSocket client
│       └── rate_limiter.py     # Token bucket rate limiter
│
├── frontend/
│   ├── index.html              # Complete UI with embedded CSS
│   ├── package.json            # Node.js dependencies
│   ├── vite.config.js          # Vite configuration
│   └── src/
│       ├── main.js             # Main orchestration
│       ├── chart.js            # TradingView chart manager
│       ├── api.js              # Backend REST client
│       └── websocket.js        # Backend WebSocket client
│
├── docs/                       # Reference documentation
├── PLAN.md                     # Technical architecture
├── UI_DESIGN.md                # UI/UX specifications
├── RULES.md                    # Development guidelines
└── README.md                   # This file
```

## Key Features Explained

### Smart Aggregation
TradeX subscribes to only **1-minute bars** via WebSocket and aggregates them in real-time to all 9 timeframes:
- 5m = 5 consecutive 1m bars
- 15m = 15 consecutive 1m bars
- 30m = 30 consecutive 1m bars
- 1H = 60 consecutive 1m bars
- 4H = 240 consecutive 1m bars
- 1D = 1440 consecutive 1m bars (market hours)
- 1W = 5 daily bars
- 1M = Calendar month aggregation

This approach minimizes API usage and provides consistent data across timeframes.

### WebSocket Proxy Architecture
```
Frontend ←→ Backend WebSocket (port 8000)
                      ↓
         InsightSentry WebSocket (port 443)
```

The backend acts as a WebSocket proxy, maintaining one connection to InsightSentry and broadcasting updates to all connected frontend clients.

### Caching Strategy
- **Cache Hit**: Returns data from memory (instant)
- **Cache Miss**: Fetches from API, stores in cache
- **Cache Key**: `(symbol, timeframe)` tuple

## Development

### Backend Development
```bash
cd backend
# Install with uv (recommended)
uv pip install -r requirements.txt
# Or with pip
pip install -r requirements.txt
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev     # Start dev server
npm run build   # Build for production
```

### Code Style
- Backend: Black formatter, Ruff linter
- Frontend: ESLint, Prettier (in package.json)

## Testing

### Manual Testing Checklist
- [ ] Backend connects to InsightSentry WebSocket
- [ ] Frontend connects to backend WebSocket
- [ ] Historical data loads for all 9 timeframes
- [ ] Real-time bars update live
- [ ] Timeframe switching works instantly
- [ ] Symbol change fetches new data
- [ ] Connection status indicator shows correct state
- [ ] Stats cards display accurate metrics
- [ ] Rate limiter prevents API ban
- [ ] WebSocket reconnection works on disconnect

## Roadmap

### Current Release (v1.0)
- ✅ Real-time data streaming
- ✅ 9 timeframe support
- ✅ Smart aggregation
- ✅ Historical data caching
- ✅ Professional trading UI
- ✅ WebSocket proxy architecture

### Future Enhancements
- 🔜 Multiple symbol support
- 🔜 Technical indicators (MA, EMA, RSI, MACD)
- 🔜 Drawing tools (trendlines, support/resistance)
- 🔜 Chart screenshots
- 🔜 Export historical data
- 🔜 Mobile app (React Native)
- 🔜 TradeX Pro with premium features

## Contributing

Contributions are welcome! Please follow these guidelines:

1. **Code Style**: Follow existing patterns (see RULES.md)
2. **Modular Architecture**: Each feature in its own file
3. **Documentation**: Update docs for new features
4. **Testing**: Test thoroughly before submitting PR
5. **No Auto-commits**: Ask user before committing

## Troubleshooting

### Backend Issues

**Port 8000 already in use**:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

**API key error**:
- Verify `.env` file exists in `backend/`
- Check API key is correct
- Ensure no extra spaces in `.env`

### Frontend Issues

**Port 3000 already in use**:
```bash
# Find and kill process on port 3000
# Vite will auto-select next available port if needed
```

**Chart not displaying**:
- Check browser console for errors
- Verify backend is running
- Check WebSocket connection status

## License

MIT License - Free to use, modify, and distribute.

See [LICENSE](LICENSE) file for details.

## Credits

Built by **LRGEX** 🚀

- **Data Provider**: [InsightSentry](https://insightsentry.com)
- **Charting Library**: [TradingView Lightweight Charts](https://www.tradingview.com/lightweight-charts/)
- **Backend Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Frontend Build Tool**: [Vite](https://vitejs.dev/)

---

<div align="center">
  <p><strong>TradeX</strong> - Professional Trading Charts</p>
  <p>Built with ❤️ by LRGEX</p>
</div>
