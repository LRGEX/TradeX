# InsightSentry API - Complete Documentation

**Version:** 3.0.5
**Last Updated:** 2026-01-02

---

## Table of Contents

1. [Overview](#overview)
2. [REST API](#rest-api)
3. [WebSocket API](#websocket-api)
4. [Enterprise/Data Package](#enterprisedata-package)
5. [Organization API](#organization-api)
6. [Scalability Options](#scalability-options)
7. [Authentication](#authentication)
8. [Rate Limiting](#rate-limiting)
9. [Code Examples](#code-examples)
10. [Proven Working Examples](#proven-working-examples)
11. [Error Handling](#error-handling)

---

## Overview

### What is InsightSentry?

InsightSentry is a **developer-friendly and cost-effective Financial Data API aggregator** providing unified access to data from **150+ global exchanges and venues** across multiple asset classes:

- **Global Equities** (+Funds)
- **Futures**
- **Foreign Exchange (FX)**
- **Bonds**
- **Cryptocurrencies**
- **Economic Data**
- **Options**
- **Screeners**
- **News Feed**

### Data Access Methods

- **REST API** – Flexible access with multiple timeframes
- **WebSocket API** – Real-time streaming data (tick, second, minute, hour, day, week, month)
- **Long Polling (via REST API)** – Real-time updates without WebSocket, enabled by passing `long_poll=true`

### Historical & Real-Time Data Coverage

- **Historical Coverage:** Over **20 years** of data for many asset classes, up to **minute-level granularity**
- **Real-Time Granularity:** Tick-level (microsecond precision), second-level, and custom intervals
- **Flexible Timeframes:** Request any interval using:
  - `bar_type` = tick, second, minute, hour, day, week, month
  - `bar_interval=<number>`
  - Developers don't need to handle manual timeframe conversions
- **Real-Time WebSocket Updates:** Data is pushed on every price or volume change, not only at interval boundaries

### API Endpoints

| Gateway | URL |
|---------|-----|
| InsightSentry API Gateway | `https://api.insightsentry.com` |
| RapidAPI Gateway | `https://insightsentry.p.rapidapi.com/` |
| WebSocket (Market Data) | `wss://realtime.insightsentry.com/live` |
| WebSocket (News Feed) | `wss://realtime.insightsentry.com/newsfeed` |

### Resources

- **OpenAPI Spec (3.0.3):** https://insightsentry.com/openapi.json
- **API Playground:** https://insightsentry.com/demo
- **Exchange & Venue List:** https://insightsentry.com/market_list.json
- **Symbol Search:** https://insightsentry.com/search

---

## Pricing Plans

All higher-tier plans include features from lower tiers.

### Free Plan
**Price:** $0
**Features:**
- Real-time data via REST API
- Recent 5k data points via REST API
- Calendar API
- Screener API (delayed, limited data)
- Options API (delayed)
- 1k requests per month

### Pro Plan
**Price:** $15/month
**Features:**
- Real-time data via WebSocket (unmetered)
- 2 WebSocket subscriptions
- Recent 20k data points via REST API
- News Feed API via REST API
- News Feed via WebSocket (unmetered)
- Document API (Transcripts, Sec-filing, Reports)
- 50k REST API quota
- 25 requests per minute

### Ultra Plan
**Price:** $25/month
**Features:**
- 5 WebSocket subscriptions
- Deep historical data via REST API (20+ years for equities)
- Recent 30k data points via REST API
- Screener API (all data, near real-time)
- Options API (near real-time)
- 120k REST API quota
- 40 requests per minute

### Mega Plan
**Price:** $50/month
**Features:**
- 12 WebSocket subscriptions
- Additional WebSocket connections
- Tick data via WebSocket and REST API (up to 30k data points)
- Faster Screener/Option API
- Recent 30k data points via WebSocket API
- Unlimited REST API quota
- 80 requests per minute

### WebSocket Subscription Details

1 WebSocket subscription allows either:
- Streaming OHLCV data (`Series`) for **1 symbol**, OR
- Level 1 Quote data (`Quote`) for **up to 10 symbols**

---

## REST API

### Base URL
```
https://api.insightsentry.com
```

### Authentication

All REST API requests require authentication using a Bearer token:

```http
Authorization: Bearer YOUR_API_KEY
```

### Key Endpoints

#### 1. Get Recent Time Series (up to 30k bars)

**Endpoint:** `GET /v3/symbols/{symbol}/series`

**Description:** Retrieve recent historical OHLCV data with real-time data option for a symbol with configurable time intervals and adjustments.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | path | Yes | Symbol in Exchange:Symbol format (e.g., NASDAQ:AAPL, NYSE:TSLA) |
| `bar_type` | query | Yes | Bar type: `second`, `minute`, `hour`, `day`, `week`, `month` |
| `bar_interval` | query | No | Number of units per bar (e.g., 1, 5, 15). Default: 1 |
| `extended` | query | No | Include extended hours (default: true) |
| `dadj` | query | No | Apply dividend adjustment (default: false) |
| `backadjust` | query | No | Apply back-adjustment for futures (default: false) |
| `data_points` | query | No | Maximum number of data points to return (default: varies by plan) |
| `realtime` | query | No | Include real-time data (default: false) |
| `currency` | query | No | Currency conversion for currency-specific data |
| `settlement` | query | No | Use settlement prices (default: false) |

**Example Request:**
```bash
curl -X GET "https://api.insightsentry.com/v3/symbols/NASDAQ:AAPL/series?bar_type=minute&bar_interval=1&data_points=1000" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Example Response:**
```json
{
  "symbol": "NASDAQ:AAPL",
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
```

#### 2. Get Deep Historical Data

**Endpoint:** `GET /v3/symbols/{symbol}/history`

**Description:** Retrieve historical data for specific time periods with deep archive access (20+ years).

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | path | Yes | Symbol in Exchange:Symbol format |
| `bar_type` | query | Yes | Bar type: `second`, `minute`, `hour` |
| `bar_interval` | query | No | Number of units per bar (e.g., 1, 5, 15) |
| `start_date` | query | Yes | Starting period in YYYY-MM format for minute/hour or YYYY-MM-DD for second intervals (UTC) |
| `extended` | query | No | Include extended hours (default: true) |
| `dadj` | query | No | Apply dividend adjustment (default: false) |
| `backadjust` | query | No | Apply back-adjustment for futures (default: false) |
| `settlement` | query | No | Use settlement prices (default: false) |

**Example Request:**
```bash
curl -X GET "https://api.insightsentry.com/v3/symbols/CME_MINI:NQH2025/history?bar_type=minute&bar_interval=1&start_date=2025-01" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

#### 3. Get Symbol Information

**Endpoint:** `GET /v3/symbols/{symbol}/info`

**Description:** Retrieve detailed information about a symbol including type, currency, market data, splits, option information, and more.

**Example Response:**
```json
{
  "code": "NASDAQ:AAPL",
  "type": "stock",
  "name": "Apple Inc.",
  "exchange": "NASDAQ",
  "currency_code": "USD",
  "timezone": "America/New_York",
  "country_code": "US",
  "sector": "Technology",
  "industry": "Consumer Electronics",
  "market_cap": 3558428648118.0,
  "status": "OPEN",
  "delay_seconds": 0,
  "price_scale": 2,
  "has_backadjustment": false
}
```

#### 4. Get Real-Time Quotes

**Endpoint:** `GET /v3/symbols/quotes`

**Description:** Retrieve real-time quote data for up to 10 symbols.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `codes` | query | Yes | Comma-separated list of symbol codes (e.g., NASDAQ:AAPL,NYSE:TSLA) |

**Example Request:**
```bash
curl -X GET "https://api.insightsentry.com/v3/symbols/quotes?codes=NASDAQ:AAPL,CME_MINI:NQ1!" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Example Response:**
```json
{
  "last_update": 1757061265540,
  "total_items": 1,
  "data": [
    {
      "code": "NASDAQ:AAPL",
      "status": "OPEN",
      "lp_time": 1757061117.0,
      "volume": 47549429.0,
      "last_price": 239.42,
      "change_percent": -0.15,
      "change": -0.36,
      "ask": 239.47,
      "bid": 239.42,
      "ask_size": 2.0,
      "bid_size": 1.0,
      "prev_close_price": 238.47,
      "open_price": 238.45,
      "low_price": 236.74,
      "high_price": 239.8999,
      "market_cap": 3558428648118.0,
      "currency_code": "USD",
      "delay_seconds": 0
    }
  ]
}
```

#### 5. Search Symbols

**Endpoint:** `GET /v3/symbols/search`

**Description:** Search for symbols. To search for a specific type or country, leave query empty. To search for all symbols from a specific exchange, use query like "NASDAQ:".

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | query | No | Search query string (e.g., "apple") |
| `type` | query | No | Filter by instrument type (crypto, stock, futures, etc.) |
| `country` | query | No | Filter by country (2-letter ISO code, e.g., US) |
| `page` | query | No | Page number (each page returns up to 50 results) |

**Example Request:**
```bash
curl -X GET "https://api.insightsentry.com/v3/symbols/search?query=apple&type=stock&country=US&page=1" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Example Response:**
```json
{
  "current_page": 1,
  "has_more": false,
  "symbols": [
    {
      "name": "Apple Inc.",
      "code": "NASDAQ:AAPL",
      "type": "stock",
      "exchange": "NASDAQ",
      "currency_code": "USD",
      "country": "US"
    }
  ]
}
```

#### 6. Get Fundamental Data

**Endpoint:** `GET /v3/symbols/{symbol}/fundamentals`

**Description:** Retrieve comprehensive fundamental data including company info, valuation ratios, profitability metrics, balance sheet, cash flow, income statement, and more.

**Example Request:**
```bash
curl -X GET "https://api.insightsentry.com/v3/symbols/NASDAQ:AAPL/fundamentals" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

#### 7. Get Futures Contracts

**Endpoint:** `GET /v3/symbols/{symbol}/contracts`

**Description:** Retrieve list of relatively recent contracts along with their settlement dates for futures symbols.

**Example Request:**
```bash
curl -X GET "https://api.insightsentry.com/v3/symbols/COMEX:GC1!/contracts" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Example Response:**
```json
{
  "base_code": "COMEX:GC",
  "contracts": [
    {
      "code": "COMEX:GCH2025",
      "settlement_date": "20250328"
    }
  ]
}
```

#### 8. Get Trading Session

**Endpoint:** `GET /v3/symbols/{symbol}/session`

**Description:** Retrieve trading session details including holidays, trading hours, timezone, and session corrections.

---

## WebSocket API

### WebSocket Endpoints

| Endpoint | Purpose |
|----------|---------|
| `wss://realtime.insightsentry.com/live` | Market data (quotes, time series, tick data) |
| `wss://realtime.insightsentry.com/newsfeed` | Latest financial news and market updates |

### Prerequisites

Before connecting to the WebSocket API, ensure you have:

1. **API Key** - Use your existing REST API key (the same key works for both REST and WebSocket)
2. **WebSocket Client Library** - Choose one that supports automatic reconnection and retry logic
3. **Connection Settings** - Configure appropriate timeouts and implement ping/pong for stability

**IMPORTANT:** Your REST API key automatically includes WebSocket access. There is NO separate WebSocket API key needed.

### Authentication

#### Market Data Authentication

Combine authentication with your subscription request:

```json
{
  "api_key": "<your_rest_api_key>",
  "subscriptions": [
    // Array of subscription objects
  ]
}
```

**Proven Working Example:**
```python
import asyncio
import websockets
import json

API_KEY = "your_rest_api_key_here"

async def connect():
    uri = "wss://realtime.insightsentry.com/live"
    async with websockets.connect(uri) as websocket:
        subscription = {
            "api_key": API_KEY,
            "subscriptions": [
                {
                    "code": "CME_MINI:MNQ1!",
                    "type": "series",
                    "bar_type": "minute",
                    "bar_interval": 1
                }
            ]
        }
        await websocket.send(json.dumps(subscription))

        # Receive data
        response = await websocket.recv()
        data = json.loads(response)
        print(data)
```

#### News Feed Authentication

Send only your API key in this simplified format:

```json
{
  "api_key": "<your_rest_api_key>"
  // No subscriptions needed for news feed
}
```

**Note:** When you connect to `/newsfeed`, the server automatically sends the 10 most recent news items.

### Subscribing to Data Feeds

#### Initial Subscription Message

After connecting to the market data endpoint, send a JSON message to authenticate and subscribe to data feeds:

```json
{
  "api_key": "<your_rest_api_key>",
  "subscriptions": [
    // Array of subscription objects
  ]
}
```

#### Subscription Parameters

Each subscription object can include:

**Required Parameters:**
- `code` - Symbol identifier (e.g., "NASDAQ:AAPL", "BINANCE:BTCUSDT", "CME_MINI:MNQ1!")

**Data Type Selection:**
- `type` - Data feed type: `"series"` (default) or `"quote"`

**Series Data Parameters (when type="series"):**
- `bar_type` - Time interval: `"minute"`, `"hour"`, `"day"`, or `"tick"`
- `bar_interval` - Number of units per bar (e.g., 1, 5, 15)
- `extended` - Include extended hours (default: true)
- `dadj` - Apply dividend adjustment (default: false)

#### Example Subscriptions

**Series Data (1-minute bars):**
```json
{
  "api_key": "<your_rest_api_key>",
  "subscriptions": [
    {
      "code": "CME_MINI:MNQ1!",
      "type": "series",
      "bar_type": "minute",
      "bar_interval": 1
    }
  ]
}
```

**Quote Data:**
```json
{
  "api_key": "<your_rest_api_key>",
  "subscriptions": [
    {
      "code": "NASDAQ:AAPL",
      "type": "quote"
    }
  ]
}
```

**Multiple Subscriptions:**
```json
{
  "api_key": "<your_rest_api_key>",
  "subscriptions": [
    {
      "code": "NASDAQ:AAPL",
      "type": "series",
      "bar_type": "minute",
      "bar_interval": 1
    },
    {
      "code": "NASDAQ:TSLA",
      "type": "quote"
    }
  ]
}
```

### Modifying Subscriptions

You can update your subscriptions without disconnecting. Send a new subscription message with your complete desired list. The server replaces all previous subscriptions with the new ones.

**Example - Updating Subscriptions:**
```json
{
  "api_key": "<your_rest_api_key>",
  "subscriptions": [
    {
      "code": "NASDAQ:AAPL",
      "type": "series",
      "bar_type": "minute",
      "bar_interval": 1
    },
    {
      "code": "NASDAQ:AAPL",
      "type": "quote"
    }
  ]
}
```

### Subscription Rules & Limits

1. **Required Authentication:** Every subscription message must include your valid `api_key`
2. **Rate Limiting:** Don't send **300 messages per 5 minutes**. If you exceed this limit, your messages will be ignored temporarily (existing data feed continues uninterrupted)
3. **Empty Subscriptions:** You cannot send an empty `subscriptions` array
4. **Multiple Symbols:** Subscribe to multiple symbols in one message (subject to your plan limits)

### Response Data Formats

#### Series Data (type: "series")

OHLCV (Open, High, Low, Close, Volume) bar information and tick data.

**Real-time Updates:** Regardless of your chosen `bar_type` and `bar_interval`, you receive updates whenever the close price or volume changes within the current bar period.

**Update Frequency:**
- **Tick Data** (`bar_type: "tick"`) - Data pushed for every individual trade
- **Second Intervals** (`bar_type: "second"`) - Data pushed only when close price or volume changes
- **Higher Timeframes** (`bar_type: "minute"` or above) - Data pushed when price/volume changes AND when new bar periods start

**Example Response:**
```json
{
  "code": "NASDAQ:AAPL",
  "bar_end": 1733432399.0,
  "last_update": 1733432399820,
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
```

#### Quote Data (type: "quote")

Real-time market information including current prices, trading volume, and bid/ask spreads.

**Example Response:**
```json
{
  "last_update": 1757061265540,
  "total_items": 1,
  "data": [
    {
      "code": "NASDAQ:AAPL",
      "status": "OPEN",
      "lp_time": 1757061117.0,
      "volume": 47549429.0,
      "last_price": 239.42,
      "change_percent": -0.15,
      "change": -0.36,
      "ask": 239.47,
      "bid": 239.42,
      "ask_size": 2.0,
      "bid_size": 1.0,
      "prev_close_price": 238.47,
      "open_price": 238.45,
      "low_price": 236.74,
      "high_price": 239.8999,
      "market_cap": 3558428648118.0,
      "currency_code": "USD",
      "delay_seconds": 0
    }
  ]
}
```

**Understanding `delay_seconds`:**
- `0` - Real-time with no artificial delay
- `900` - Data is delayed by 900 seconds (15 minutes)
- `-1` - End-of-day (EOD)

### Additional Parameters

#### Extended Market Hours (`extended`)

Applies to many US and Global stock markets.

- `extended: true` (default) - Includes pre-market and after-hours trading data
- `extended: false` - Only includes regular trading hours data

**For US Equities:**
- Pre-market: 4:00 AM - 9:30 AM ET
- After-hours: 4:00 PM - 8:00 PM ET

#### Dividend Adjustment (`dadj`)

- `dadj: true` - Adjust historical prices for dividends
- `dadj: false` (default) - No dividend adjustment

#### Back-Adjustment (`backadjust`)

For futures continuous contracts:

- `backadjust: true` - Apply back-adjustment to account for rollover gaps
- `backadjust: false` (default) - No back-adjustment

### Maintaining Connection

#### Implementing Ping-Pong

Keep connections alive and detect network issues:

```javascript
// Send ping every 15 seconds
setInterval(() => {
  if (websocket.readyState === WebSocket.OPEN) {
    websocket.send("ping");
  }
}, 15000);

// Filter out pong responses
websocket.onmessage = (event) => {
  if (event.data === "pong") {
    return; // Ignore pong messages
  }
  // Process other data
};
```

#### Reconnection Logic

Implement automatic reconnection with exponential backoff:

```javascript
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;
const baseReconnectDelay = 1000; // 1 second

function connect() {
  websocket = new WebSocket("wss://realtime.insightsentry.com/live");

  websocket.onopen = () => {
    reconnectAttempts = 0;
    // Send subscription
  };

  websocket.onclose = () => {
    reconnectAttempts++;
    if (reconnectAttempts <= maxReconnectAttempts) {
      const delay = baseReconnectDelay * Math.pow(2, reconnectAttempts - 1);
      setTimeout(connect, delay);
    }
  };
}
```

### Error Handling

#### Common WebSocket Errors

1. **Authentication Failed** - Invalid API key
2. **Rate Limit Exceeded** - Too many subscription messages
3. **Invalid Symbol** - Symbol code not recognized
4. **Connection Lost** - Network issues or server restart

#### Error Response Format

```json
{
  "error": "Error message here",
  "code": "ERROR_CODE"
}
```

### Best Practices

1. **Minimize Subscription Changes** - Cache active subscriptions to minimize changes
2. **Implement Exponential Backoff** - Use exponential backoff for reconnection attempts
3. **Monitor Connection State** - Track connection health and log state changes
4. **Filter Pong Messages** - Don't process "pong" responses as data
5. **Use Proper Error Handling** - Gracefully handle disconnections and errors
6. **Implement Rate Limiting** - Respect the 300 messages per 5 minutes limit

---

## Enterprise/Data Package

### Overview

The Enterprise Data Package provides dedicated WebSocket infrastructure for high-frequency applications requiring access to 10,000+ symbols in real-time.

### Data Delivery Options

#### WebSocket
- Direct real-time communication
- Immediate data delivery
- Lower latency

#### Pub/Sub (Message Queue)
- Better scalability for distributed architectures
- Higher reliability for high-volume data
- Supports multiple consumers

**Supported Message Queue Systems:**
- Redis Pub/Sub
- Apache Kafka
- RabbitMQ
- Amazon SQS
- Google Cloud Pub/Sub
- Azure Service Bus
- Other systems upon request

### Features

#### Dedicated WebSocket Server
- Stream 10,000+ symbols with 1-second OHLCV or Tick data
- Level 1 (L1) quote updates
- Runs on dedicated servers for maximum reliability

#### Market Coverage

**US Equities Bundle** - $1000/month
- Live streaming access to 11,000+ US equities concurrently
- Real-time data via WebSocket/PubSub
- Dedicated server infrastructure

**Crypto Bundle** - $600/month
- Live streaming access to 10,000+ global cryptocurrencies concurrently
- Real-time data via WebSocket/PubSub
- Dedicated server infrastructure

### Authentication

Enterprise uses **Azure Active Directory authentication** for enhanced security.

#### Two-Step Authentication Flow

1. **Obtain Microsoft Azure OAuth Access Token**

```bash
curl -X POST "https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id={client_id}&scope={scope}&client_secret={client_secret}&grant_type=client_credentials"
```

**Response:**
```json
{
  "token_type": "Bearer",
  "expires_in": 3599,
  "ext_expires_in": 3599,
  "access_token": "eyJ0eXAiOi...JWT_TOKEN_HERE"
}
```

2. **Authenticate with InsightSentry Server**

```bash
curl -X POST "https://{host_name}/.auth/login/aad" \
  -H "Content-Type: application/json" \
  -d '{"access_token": "JWT_TOKEN_HERE..."}'
```

**Response:**
```json
{
  "authenticationToken": "ANOTHER_JWT_TOKEN_HERE",
  "user": {
    "userId": "sid:a50f42b1481ca31efcf853fabb13e95b"
  }
}
```

### Using the Authentication Token

```javascript
const socket = new WebSocket('wss://{host_name}/ws');
socket.setRequestHeader('X-ZUMO-AUTH', authenticationToken);

// Register email after connection
socket.onopen = function() {
  socket.send(JSON.stringify({
    "email": "your-engineering-team@example.com"
  }));
};
```

**Token Management:**
- The `authenticationToken` expires after **one month**
- Store the token securely in your database
- Implement automatic token refresh before expiration (use 3-day buffer)

### Optimized Response Formats

Enterprise uses abbreviated field names to reduce bandwidth:

#### Quote Data

| Standard Field | New Format | Description |
|----------------|------------|-------------|
| code | c | Symbol identifier |
| status | ss | Session Status |
| lp_time | lt | Last price timestamp |
| volume | v | Trading volume |
| last_price | lp | Last trade price |
| ask | a | Ask price |
| bid | b | Bid price |
| ask_size | as | Size of ask orders |
| bid_size | bs | Size of bid orders |

**Example:**
```json
{
  "c": "NASDAQ:AAPL",
  "ss": "OPEN",
  "lt": 1733432340.0,
  "v": 533779.0,
  "lp": 243.08,
  "a": 243.09,
  "b": 243.08,
  "as": 520.0,
  "bs": 430.0
}
```

#### Series Data

| Standard Field | New Format | Description |
|----------------|------------|-------------|
| code | c | Symbol identifier |
| bar_end | be | Bar end timestamp |
| last_update | lu | Last update timestamp |
| bar_type | bt | Bar interval type |
| series | s | Array of OHLCV data |

**OHLCV Fields:**
| Standard Field | New Format | Description |
|----------------|------------|-------------|
| time | t | Bar timestamp |
| open | o | Opening price |
| high | h | Highest price |
| low | l | Lowest price |
| close | c | Closing price |
| volume | v | Trading volume |

**Example:**
```json
{
  "c": "NASDAQ:AAPL",
  "be": 1733432399.0,
  "lu": 1733432399820,
  "bt": "1m",
  "s": [
    {
      "t": 1733432340.0,
      "o": 242.89,
      "h": 243.09,
      "l": 242.82,
      "c": 243.08,
      "v": 533779.0
    }
  ]
}
```

#### Tick Data

**Example:**
```json
{
  "c": "NASDAQ:AAPL",
  "t": 1733432345123456789,
  "p": 243.08,
  "v": 100
}
```

Where:
- `c` = symbol code
- `t` = microsecond timestamp
- `p` = price
- `v` = volume

---

## Organization API

### Overview

The Organization API enables organization admins to programmatically manage members and their subscriptions.

**Key Features:**
- Create and manage organization members programmatically
- Assign subscription plans (Pro, Ultra, Mega) or custom plans
- Automatic proration for plan changes and upgrades
- Credit-based billing system
- Full control over member lifecycle

**Important Limitations:**
- Users created via API **cannot** log in to the dashboard
- Members are **only** manageable by the admin via API or dashboard
- Members' subscriptions **do not auto-renew** - admin must manually renew
- All operations deduct from admin's credit balance

### Authentication

All Organization API requests require authentication:

```http
Authorization: Bearer YOUR_ORGANIZATION_API_KEY
```

You can find your Organization API key in the Organization Tab in the dashboard.

### API Endpoints

#### Get Plans

**Endpoint:** `GET /api/organization/plans`

Retrieve all available plans for your organization, including both regular plans and custom plans.

**Example Request:**
```bash
curl -X GET "https://insightsentry.com/api/organization/plans" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Example Response:**
```json
{
  "success": true,
  "regular_plans": [
    {"name": "pro", "price": 15},
    {"name": "ultra", "price": 25},
    {"name": "mega", "price": 50}
  ],
  "custom_plans": [
    {
      "name": "ultra_plus",
      "price": 40,
      "feature": "ultra",
      "rate_limit": 80,
      "websocket_connections": 1,
      "websocket_symbols": 5,
      "quota": 0
    }
  ]
}
```

#### Create Member

**Endpoint:** `POST /api/organization/members/create`

Creates a new organization member with the specified subscription plan.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `uid` | string | Yes | Unique identifier from your application (max 100 characters) |
| `plan` | string | Yes | Plan ID: "pro", "ultra", "mega", or custom plan ID |
| `full_name` | string | No | Full name of the member |

**Example Request:**
```bash
curl -X POST "https://insightsentry.com/api/organization/members/create" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "uid": "john_doe",
    "plan": "pro",
    "full_name": "John Doe"
  }'
```

**Example Response:**
```json
{
  "success": true,
  "member": {
    "uid": "john_doe",
    "email": "org_john_doe@company.com",
    "full_name": "John Doe",
    "role": "member",
    "plan": "pro",
    "status": "active",
    "created_at": "2025-10-02T00:00:00.000Z",
    "plan_end_at": "2025-11-01T00:00:00.000Z",
    "api_key": "generated_api_key_here",
    "websocket_symbols": 2,
    "websocket_connections": 1,
    "newsfeed": true,
    "rate_limit": 60,
    "quota": 50000,
    "quota_exceeded": false
  }
}
```

#### List Members

**Endpoint:** `GET /api/organization/members`

Retrieves a paginated list of all organization members.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | number | 1 | Page number for pagination |
| `limit` | number | 10 | Number of members per page |

**Example Request:**
```bash
curl -X GET "https://insightsentry.com/api/organization/members?page=1&limit=10" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

#### Get Member

**Endpoint:** `GET /api/organization/members/{uid}`

Retrieves details of a specific member.

**Example Request:**
```bash
curl -X GET "https://insightsentry.com/api/organization/members/john_doe" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

#### Update Member

**Endpoint:** `POST /api/organization/members/{uid}/update`

Updates a member's subscription plan with automatic proration.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `plan` | string | Yes | New plan ID |
| `full_name` | string | No | Updated full name |

**Example Request:**
```bash
curl -X POST "https://insightsentry.com/api/organization/members/john_doe/update" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "plan": "ultra",
    "full_name": "John Doe Jr."
  }'
```

#### Cancel Member

**Endpoint:** `POST /api/organization/members/{uid}/cancel`

Cancels a member's subscription. Credits will be prorated and refunded to admin.

**Example Request:**
```bash
curl -X POST "https://insightsentry.com/api/organization/members/john_doe/cancel" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

#### Delete Member

**Endpoint:** `DELETE /api/organization/members/{uid}`

Permanently deletes a member and revokes API access.

**Example Request:**
```bash
curl -X DELETE "https://insightsentry.com/api/organization/members/john_doe" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Custom Plans

Custom plans allow organizations to create tailored subscription plans with specific limits and features.

**Configuration Properties:**

| Property | Required | Description |
|----------|----------|-------------|
| `id` | No | Custom identifier for the plan (auto-generated if not provided) |
| `feature` | Yes | Base feature tier: "pro", "ultra", or "mega" |
| `rate_limit` | No | Custom rate limit (requests per minute) |
| `websocket_connections` | No | Number of concurrent WebSocket connections |
| `websocket_symbols` | No | Number of symbols to subscribe to |
| `quota` | No | Monthly REST API request limit (0 = unlimited) |

**Contact our team** to configure custom plans for your organization.

### Proration & Billing

**How Proration Works:**

1. When upgrading, you're charged the difference between plans on a prorated basis
2. When downgrading, you receive credits based on the remaining time
3. Credits are added to your admin balance
4. Unused credits roll over to the next month
5. Credits are refundable (minus 10% transaction fee)

**Example:**
- Member on Pro plan ($15) upgrades to Ultra plan ($25) halfway through the month
- Difference: $10
- Prorated charge: $5 (50% of $10 for remaining half month)
- New plan end date: 30 days from upgrade date

---

## Scalability Options

InsightSentry offers three primary approaches to scale your financial data access:

### Option 1: Custom Plan

**Overview:** Route all API requests and WebSocket connections through your own server infrastructure.

**Use Cases:**
- Enhanced control with direct client connections to your backend
- Complex analytics requiring data aggregation across multiple symbols
- Centralized processing feeding multiple downstream applications

**Features:**
- Your existing API key with custom rate limits
- Enhanced WebSocket symbol allowances
- Priority support and dedicated account management

**Pricing:** Custom-priced based on WebSocket symbols, request rates, and additional features

### Option 2: Organization API

**Overview:** Manage individual user subscriptions programmatically with volume discounts and custom plans.

**Use Cases:**
- SaaS applications serving multiple users
- Platforms requiring per-user billing
- Applications where users need direct API access

**How It Works:**
1. **Purchase Credits:** Buy monthly credits via recurring subscription
2. **Manage Users:** Create, update, and assign plans through the API
3. **User Isolation:** Each user gets unique API key and dedicated limits
4. **Flexible Plans:** Choose standard plans or create custom plans

**Pricing & Discounts:**

| Credits Range | Discount | Effective Cost per Credit |
|---------------|----------|---------------------------|
| 1 - 500 | 0% | $1.00 |
| 501 - 1,000 | 10% | $0.90 |
| 1,001 - 1,500 | 20% | $0.80 |
| 1,501 - 2,000 | 30% | $0.70 |
| 2,001 - 2,500 | 40% | $0.60 |
| 2,501+ | 50% | $0.50 |

**Plan Costs (at base price):**
- Pro: 15 credits/month ($15.00)
- Ultra: 25 credits/month ($25.00)
- Mega: 50 credits/month ($50.00)

**With 50% discount:**
- Pro: $7.50/month
- Ultra: $12.50/month
- Mega: $25.00/month

**Benefits:**
- Easier management (no dedicated infrastructure needed)
- Direct connections to highly available infrastructure
- User isolation (no worry about plan limits)
- Flexible plans with custom limits
- Transparent billing with detailed usage tracking

### Option 3: Data Package

**Overview:** Access dedicated WebSocket servers streaming 10,000+ symbols for real-time data.

**Use Cases:**
- High-frequency trading applications
- Applications requiring massive-scale data access
- Real-time analytics across entire markets

**What's Included:**
- Dedicated WebSocket Server streaming 10,000+ symbols
- 1-second OHLCV or Tick data and quote (L1) updates
- Access to US equities (11,000+ symbols), crypto (10,000+ symbols), or global markets
- Optional PubSub infrastructure for distributed architectures

**Pricing:**
- US Equities Bundle: $1000/month
- Crypto Bundle: $600/month
- Custom packages available

### Hybrid Approach

You can combine different approaches to optimize costs and performance. For example:
- Use centralized Custom Plans for heavy processing
- Use Organization API for direct user access
- Use Data Package for high-frequency symbol monitoring

---

## Authentication

### REST API Authentication

All REST API requests require a Bearer token:

```http
Authorization: Bearer YOUR_API_KEY
```

### WebSocket Authentication

#### Standard WebSocket Authentication

Use your REST API key for WebSocket connections:

```json
{
  "api_key": "<your_rest_api_key>",
  "subscriptions": [...]
}
```

**No separate WebSocket key needed** - your existing REST API key works for both APIs.

#### Enterprise Azure AD Authentication

Two-step process:

1. Get Azure OAuth token
2. Authenticate with InsightSentry using Azure token

See the [Enterprise/Data Package](#enterprisedata-package) section for details.

### Organization API Authentication

```http
Authorization: Bearer YOUR_ORGANIZATION_API_KEY
```

### Security Best Practices

1. **Store API Keys Securely:** Use environment variables, never in code
2. **Rotate API Keys:** Periodically change keys for enhanced security
3. **Monitor Usage:** Track API usage for unusual patterns
4. **Use HTTPS:** Always use encrypted connections
5. **Implement Rate Limiting:** Respect rate limits to avoid service interruptions

---

## Rate Limiting

### REST API Rate Limits

| Plan | Requests per Minute | Monthly Quota |
|------|---------------------|---------------|
| Free | Not specified | 1,000 |
| Pro | 25 | 50,000 |
| Ultra | 40 | 120,000 |
| Mega | 80 | Unlimited |

### WebSocket Rate Limits

- **Subscription Messages:** Maximum 300 messages per 5 minutes
- **Data Received:** No rate limit or restrictions

**Note:** Only subscription messages you send count toward the limit. Data you receive is unlimited.

### Handling Rate Limits

If you exceed the rate limit:

1. **REST API:** You'll receive a `429 Too Many Requests` response
2. **WebSocket:** Your messages will be ignored temporarily

**Best Practices:**
- Implement exponential backoff
- Cache responses to minimize repeated requests
- Use WebSocket for real-time data instead of polling
- Batch requests when possible

---

## Code Examples

### Python Examples

#### REST API - Fetch Historical Data

```python
import requests

API_KEY = "your_api_key"
BASE_URL = "https://api.insightsentry.com"

def fetch_historical_data(symbol, bar_type="minute", bar_interval=1, data_points=1000):
    url = f"{BASE_URL}/v3/symbols/{symbol}/series"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    params = {
        "bar_type": bar_type,
        "bar_interval": bar_interval,
        "data_points": data_points
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

# Example usage
data = fetch_historical_data("NASDAQ:AAPL", bar_type="minute", bar_interval=1)
print(f"Fetched {len(data['series'])} data points")
```

#### REST API - Fetch Real-Time Quotes

```python
def fetch_quotes(symbols):
    url = f"{BASE_URL}/v3/symbols/quotes"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    params = {"codes": ",".join(symbols)}

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

# Example usage
quotes = fetch_quotes(["NASDAQ:AAPL", "CME_MINI:MNQ1!"])
print(quotes)
```

#### WebSocket - Connect and Subscribe

```python
import json
import websocket

def on_message(ws, message):
    data = json.loads(message)
    if message == "pong":
        return  # Ignore pong messages
    print(f"Received: {data}")

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("Connection closed")

def on_open(ws):
    print("Connection opened")
    # Send subscription message
    subscription = {
        "api_key": "your_rest_api_key",  # Use your REST API key
        "subscriptions": [
            {
                "code": "CME_MINI:MNQ1!",
                "type": "series",
                "bar_type": "minute",
                "bar_interval": 1
            }
        ]
    }
    ws.send(json.dumps(subscription))

# Connect to WebSocket
ws = websocket.WebSocketApp(
    "wss://realtime.insightsentry.com/live",
    on_open=on_open,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close
)

ws.run_forever()
```

#### WebSocket - Reconnection Logic

```python
import time
import json
import websocket

class WebSocketClient:
    def __init__(self, url, api_key):
        self.url = url
        self.api_key = api_key  # Pass your REST API key here
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.base_reconnect_delay = 1  # seconds

    def connect(self):
        ws = websocket.WebSocketApp(
            self.url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        self.ws = ws
        ws.run_forever()

    def on_open(self, ws):
        print("Connection opened")
        self.reconnect_attempts = 0
        subscription = {
            "api_key": self.api_key,  # Uses your REST API key
            "subscriptions": [
                {
                    "code": "CME_MINI:MNQ1!",
                    "type": "series",
                    "bar_type": "minute",
                    "bar_interval": 1
                }
            ]
        }
        ws.send(json.dumps(subscription))

    def on_message(self, ws, message):
        if message == "pong":
            return
        data = json.loads(message)
        print(f"Received: {data}")

    def on_error(self, ws, error):
        print(f"Error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print("Connection closed")
        self.reconnect_attempts += 1
        if self.reconnect_attempts <= self.max_reconnect_attempts:
            delay = self.base_reconnect_delay * (2 ** (self.reconnect_attempts - 1))
            print(f"Reconnecting in {delay} seconds...")
            time.sleep(delay)
            self.connect()

# Usage
client = WebSocketClient(
    "wss://realtime.insightsentry.com/live",
    "your_rest_api_key"  # Use your REST API key
)
client.connect()
```

### JavaScript Examples

#### REST API - Fetch Historical Data

```javascript
const API_KEY = "your_api_key";
const BASE_URL = "https://api.insightsentry.com";

async function fetchHistoricalData(symbol, barType = "minute", barInterval = 1, dataPoints = 1000) {
  const url = `${BASE_URL}/v3/symbols/${symbol}/series`;
  const params = new URLSearchParams({
    bar_type: barType,
    bar_interval: barInterval,
    data_points: dataPoints
  });

  const response = await fetch(`${url}?${params}`, {
    headers: {
      "Authorization": `Bearer ${API_KEY}`
    }
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
}

// Example usage
fetchHistoricalData("NASDAQ:AAPL", "minute", 1)
  .then(data => console.log(`Fetched ${data.series.length} data points`))
  .catch(error => console.error(error));
```

#### WebSocket - Connect and Subscribe

```javascript
const api_key = "your_rest_api_key";  // Use your REST API key
const ws_url = "wss://realtime.insightsentry.com/live";

const ws = new WebSocket(ws_url);

ws.onopen = () => {
  console.log("Connection opened");

  // Send subscription message
  const subscription = {
    api_key: api_key,
    subscriptions: [
      {
        code: "CME_MINI:MNQ1!",
        type: "series",
        bar_type: "minute",
        bar_interval: 1
      }
    ]
  };

  ws.send(JSON.stringify(subscription));

  // Start ping interval
  setInterval(() => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send("ping");
    }
  }, 15000);
};

ws.onmessage = (event) => {
  if (event.data === "pong") {
    return; // Ignore pong messages
  }

  const data = JSON.parse(event.data);
  console.log("Received:", data);
};

ws.onerror = (error) => {
  console.error("WebSocket error:", error);
};

ws.onclose = () => {
  console.log("Connection closed");
};
```

#### WebSocket - Reconnection Logic

```javascript
class WebSocketClient {
  constructor(url, apiKey) {
    this.url = url;
    this.apiKey = apiKey;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.baseReconnectDelay = 1000; // milliseconds
  }

  connect() {
    this.ws = new WebSocket(this.url);

    this.ws.onopen = () => {
      console.log("Connection opened");
      this.reconnectAttempts = 0;

      const subscription = {
        api_key: this.apiKey,
        subscriptions: [
          {
            code: "CME_MINI:MNQ1!",
            type: "series",
            bar_type: "minute",
            bar_interval: 1
          }
        ]
      };

      this.ws.send(JSON.stringify(subscription));

      // Start ping interval
      this.pingInterval = setInterval(() => {
        if (this.ws.readyState === WebSocket.OPEN) {
          this.ws.send("ping");
        }
      }, 15000);
    };

    this.ws.onmessage = (event) => {
      if (event.data === "pong") {
        return;
      }

      const data = JSON.parse(event.data);
      console.log("Received:", data);
    };

    this.ws.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    this.ws.onclose = () => {
      console.log("Connection closed");
      clearInterval(this.pingInterval);

      this.reconnectAttempts++;
      if (this.reconnectAttempts <= this.maxReconnectAttempts) {
        const delay = this.baseReconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
        console.log(`Reconnecting in ${delay / 1000} seconds...`);
        setTimeout(() => this.connect(), delay);
      }
    };
  }
}

// Usage
const client = new WebSocketClient(
  "wss://realtime.insightsentry.com/live",
  "your_rest_api_key"  // Use your REST API key
);
client.connect();
```

---

## Proven Working Examples

These examples have been **tested and verified** to work with a Pro plan subscription. They represent the core functionality needed for building real-time trading applications.

### Example 1: REST API - Fetch Historical Candles

**Test Date:** 2026-01-02
**Plan:** Pro ($15/month)
**Symbol:** CME_MINI:MNQ1! (Micro Nasdaq 100 Futures)
**Endpoint:** `/v3/symbols/{symbol}/series`

**Purpose:** Load historical OHLCV data for chart initialization

#### Using curl (Command Line)

```bash
curl -X GET \
  "https://api.insightsentry.com/v3/symbols/CME_MINI:MNQ1!/series?bar_type=minute&bar_interval=1&data_points=100" \
  -H "Authorization: Bearer YOUR_REST_API_KEY"
```

#### Using Python

```python
import requests

API_KEY = "your_rest_api_key"
symbol = "CME_MINI:MNQ1!"

def fetch_historical_candles(symbol, bars=100):
    """Fetch historical OHLCV candles"""
    url = f"https://api.insightsentry.com/v3/symbols/{symbol}/series"
    params = {
        "bar_type": "minute",      # minute, hour, day, week, month
        "bar_interval": 1,         # 1, 5, 15, 30, 60, etc.
        "data_points": bars,       # Pro plan: up to 20,000
        "extended": True           # Include extended hours
    }
    headers = {"Authorization": f"Bearer {API_KEY}"}

    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    return response.json()

# Example usage
data = fetch_historical_candles(symbol, bars=100)
print(f"Symbol: {data['symbol']}")
print(f"Bars: {len(data['series'])}")
print(f"Latest: {data['series'][-1]}")
```

**Actual Response (Truncated):**
```json
{
  "code": "CME_MINI:MNQ1!",
  "bar_type": "1m",
  "bar_end": 1767218399.0,
  "last_update": 1767302846127,
  "series": [
    {
      "time": 1767031080.0,
      "open": 25702.5,
      "high": 25704.5,
      "low": 25699.75,
      "close": 25703.0,
      "volume": 790.0
    }
    // ... hundreds more bars
  ]
}
```

**Key Features:**
- ✅ Returns up to **20,000 candles** (Pro plan)
- ✅ **OHLCV format** (Open, High, Low, Close, Volume)
- ✅ Multiple timeframes supported
- ✅ Real-time data included in response
- ✅ **Rate limit:** 25 requests/minute (Pro plan)

---

### Example 2: WebSocket - Real-Time Data Streaming

**Test Date:** 2026-01-02
**Plan:** Pro ($15/month)
**Symbol:** CME_MINI:MNQ1!
**Endpoint:** `wss://realtime.insightsentry.com/live`

**Purpose:** Stream real-time OHLCV updates for live chart

#### Complete Working Example (Python)

```python
import asyncio
import websockets
import json

API_KEY = "your_rest_api_key"  # Same key as REST API!
WS_URL = "wss://realtime.insightsentry.com/live"

async def stream_realtime_data():
    """Connect and stream real-time candles"""
    print(f"Connecting to {WS_URL}...")

    async with websockets.connect(WS_URL) as websocket:
        print("[OK] Connected!")

        # Send subscription
        subscription = {
            "api_key": API_KEY,
            "subscriptions": [
                {
                    "code": "CME_MINI:MNQ1!",
                    "type": "series",
                    "bar_type": "minute",
                    "bar_interval": 1
                }
            ]
        }

        await websocket.send(json.dumps(subscription))
        print("[OK] Subscribed to MNQ1!")

        # Receive data stream
        message_count = 0
        while message_count < 5:  # Receive 5 messages
            response = await websocket.recv()

            if response == "pong":
                continue

            data = json.loads(response)

            # Skip status messages
            if "message" in data:
                print(f"Status: {data['message']}")
                continue

            # Process OHLCV data
            if "series" in data and len(data["series"]) > 0:
                print(f"\n[DATA] {data['code']} - {data['bar_type']}")
                print(f"Bars received: {len(data['series'])}")

                # Show latest candle
                latest = data['series'][-1]
                print(f"Latest: O={latest['open']} H={latest['high']} "
                      f"L={latest['low']} C={latest['close']} V={latest['volume']}")

                message_count += 1

        print("\n[OK] Successfully received real-time data!")

# Run the stream
asyncio.run(stream_realtime_data())
```

**Actual Console Output:**
```
Connecting to wss://realtime.insightsentry.com/live...
[OK] Connected!
[OK] Subscribed to MNQ1!
Status: Connecting...
Status: Connected to W:ASIA-SOUTHEAST

[DATA] CME_MINI:MNQ1! - 1m
Bars received: 120
Latest: O=25505.75 H=25505.75 L=25489.5 C=25490.75 V=3494.0

[OK] Successfully received real-time data!
```

**Key Features:**
- ✅ **Same API key** works for WebSocket (no separate key needed!)
- ✅ **Real-time streaming** with millisecond updates
- ✅ **100+ candles** in initial message
- ✅ **Live updates** as price/volume changes
- ✅ **Unlimited data** via WebSocket (Pro plan)
- ✅ **Rate limit:** 300 subscription messages/5 minutes

---

## Summary for Trading Applications

**For a trading chart application (like TradeX), you need:**

### ✅ Phase 1: Load Historical Data (REST API)
```python
# Load 1000 historical 1-minute candles
historical_data = fetch_historical_candles("CME_MINI:MNQ1!", bars=1000)
# Initialize your chart with this data
```

### ✅ Phase 2: Stream Real-Time Updates (WebSocket)
```python
# Connect to WebSocket for live updates
# Real-time candles will stream in automatically
# Update your chart as new data arrives
```

### 📊 Data Flow:
1. **Initial load:** REST API fetches 1000 historical candles
2. **Chart display:** Show candles on TradingView Lightweight Charts
3. **Live updates:** WebSocket pushes new candles in real-time
4. **Chart updates:** Append new candles to existing data

### 🎯 Perfect for:
- ✅ Real-time trading charts
- ✅ Candlestick charts with multiple timeframes
- ✅ Live price feeds
- ✅ Volume tracking
- ✅ Multi-symbol dashboards (up to 2 symbols with Pro plan)

**These two examples are all you need to build a complete real-time trading chart application!**

---

## Error Handling

### Common HTTP Status Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Invalid or missing API key |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Invalid endpoint or symbol |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

### REST API Error Response Format

```json
{
  "error": "Error message here",
  "code": "ERROR_CODE",
  "details": {}
}
```

### WebSocket Error Handling

1. **Connection Errors** - Implement reconnection logic
2. **Authentication Errors** - Verify API key
3. **Subscription Errors** - Validate subscription parameters
4. **Rate Limit Errors** - Reduce subscription update frequency

### Best Practices

1. **Always Check Status Codes:** Verify response status before processing
2. **Implement Retry Logic:** Use exponential backoff for failed requests
3. **Log Errors:** Track errors for debugging and monitoring
4. **Handle Timeouts:** Set appropriate timeout values for requests
5. **Validate Input:** Check parameters before sending requests

---

## Additional Resources

### Official Documentation
- **OpenAPI Spec:** https://insightsentry.com/openapi.json
- **API Playground:** https://insightsentry.com/demo
- **Market List:** https://insightsentry.com/market_list.json
- **Symbol Search:** https://insightsentry.com/search

### Support
- **Email:** support@insightsentry.com
- **Documentation:** https://insightsentry.com/docs
- **LLM-Friendly Docs:** https://insightsentry.com/llms.txt

### Symbol Code Format

Symbols use the format: `EXCHANGE:SYMBOL`

**Examples:**
- Stocks: `NASDAQ:AAPL`, `NYSE:TSLA`
- Futures: `CME_MINI:MNQ1!`, `COMEX:GC1!`
- Crypto: `BINANCE:BTCUSDT`, `COINBASE:BTC-USD`
- Forex: `FX:EURUSD`

### Continuous Futures (1! suffix)

For futures continuous contracts:
- `CME_MINI:NQ1!` - NASDAQ 100 continuous
- `CME_MINI:ES1!` - S&P 500 continuous
- `COMEX:GC1!` - Gold continuous

**Note:** Continuous futures do not support more than 1 year of historical data. Use specific contracts for longer history.

---

## Changelog

### Version 3.0.5
- Current API version
- WebSocket API enhancements
- Organization API updates
- New Enterprise/Data Package features

---

**End of Documentation**

For the most up-to-date information, always refer to the official InsightSentry documentation at https://insightsentry.com/docs
