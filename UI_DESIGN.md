# TradeX UI Design Documentation

## Overview
A modern, dark-themed real-time trading chart interface with professional styling and smooth animations.

---

## Color Palette

### Primary Colors
- **Background (Dark)**: `#0f0f23`
- **Card Background**: `#1a1a2e`
- **Secondary Background**: `#2a2a3e`
- **Border Color**: `#3a3a4e`

### Accent Colors
- **Primary Accent (Teal)**: `#26a69a`
- **Secondary Accent (Blue)**: `#42a5f5`
- **Success Green**: `#26a69a`
- **Error Red**: `#ef5350`

### Text Colors
- **Primary Text**: `#d9d9d9`
- **Secondary Text**: `#888`

---

## Layout Structure

```
┌─────────────────────────────────────────────────────┐
│                    HEADER                           │
│  TradeX    [Timeframe▼] [Symbol Input] [●Status]  │
├─────────────────────────────────────────────────────┤
│                  STATS CARDS                        │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐             │
│  │Symbol│ │Time  │ │ Bars │ │Update│             │
│  └──────┘ └──────┘ └──────┘ └──────┘             │
├─────────────────────────────────────────────────────┤
│                  CHART AREA                         │
│  ┌───────────────────────────────────────────────┐ │
│  │                                               │ │
│  │          Candlestick Chart                    │ │
│  │                                               │ │
│  │                                               │ │
│  │                                               │ │
│  └───────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. Header Bar
- **Height**: Auto (padding: 12px 20px)
- **Background**: `#1a1a2e`
- **Box Shadow**: `0 2px 10px rgba(0, 0, 0, 0.3)`
- **Layout**: Flexbox (space-between)
- **Z-index**: 100

#### Header Components

**Title "TradeX"**
- **Font Size**: 24px
- **Font Weight**: Bold
- **Style**: Gradient text
  - Gradient: `linear-gradient(45deg, #26a69a, #42a5f5)`
  - Effect: Text gradient with webkit clip

**Controls Container**
- **Display**: Flex
- **Gap**: 15px
- **Alignment**: Center

---

### 2. Controls

#### Timeframe Selector (Dropdown)
- **Padding**: 8px 12px
- **Background**: `#2a2a3e`
- **Border**: `1px solid #3a3a4e`
- **Border Radius**: 6px
- **Color**: `#d9d9d9`
- **Font Size**: 14px
- **Min Width**: 120px
- **Transition**: all 0.3s ease

**Focus State:**
- **Border Color**: `#26a69a`
- **Box Shadow**: `0 0 0 2px rgba(38, 166, 154, 0.2)`

**Options:**
- 1m, 5m, 15m, 30m
- 1H (default selected)
- 4H, 1D, 1W, 1M

#### Symbol Input
- **Type**: Text input
- **Padding**: 8px 12px
- **Background**: `#2a2a3e`
- **Border**: `1px solid #3a3a4e`
- **Border Radius**: 6px
- **Color**: `#d9d9d9`
- **Font Size**: 14px
- **Default Value**: "CME_MINI:MNQ1!"
- **Transition**: all 0.3s ease

**Focus State:** Same as Timeframe Selector

#### Status Indicator
- **Display**: Flex
- **Gap**: 8px
- **Padding**: 6px 12px
- **Background**: `#2a2a3e`
- **Border Radius**: 20px (pill shape)
- **Font Size**: 12px

**Status Dot:**
- **Size**: 8px × 8px
- **Border Radius**: 50% (circle)
- **Default Color**: `#ef5350` (red - disconnected)
- **Connected Color**: `#26a69a` (green)
- **Animation**: Pulse (2s infinite)

**Pulse Animation:**
```css
@keyframes pulse {
  0%   { opacity: 1; }
  50%  { opacity: 0.5; }
  100% { opacity: 1; }
}
```

---

### 3. Stats Cards Section
- **Display**: CSS Grid
- **Grid Template**: `repeat(auto-fit, minmax(200px, 1fr))`
- **Gap**: 20px
- **Margin Bottom**: 20px
- **Initial State**: Hidden (display: none)
- **Show**: When chart loads

#### Individual Stat Card
- **Background**: `#1a1a2e`
- **Padding**: 15px
- **Border Radius**: 8px
- **Border Left**: `4px solid #26a69a` (accent stripe)

**Stat Label:**
- **Font Size**: 12px
- **Color**: `#888`
- **Margin Bottom**: 5px

**Stat Value:**
- **Font Size**: 18px
- **Font Weight**: Bold
- **Color**: `#d9d9d9`

**Cards:**
1. Symbol (displays current symbol)
2. Timeframe (displays current timeframe)
3. Bars Loaded (count of loaded candles)
4. Last Update (timestamp of last data update)

---

### 4. Chart Container
- **Flex**: 1 (takes remaining height)
- **Padding**: 20px
- **Overflow**: Auto

#### Chart Wrapper
- **Background**: `#1a1a2e`
- **Border Radius**: 8px
- **Padding**: 20px
- **Box Shadow**: `0 4px 20px rgba(0, 0, 0, 0.3)`
- **Min Height**: calc(100vh - 100px)

#### Loading State
- **Display**: Flex (centered)
- **Height**: 400px
- **Font Size**: 18px
- **Color**: `#888`
- **Text**: "Initializing..."

#### Error State
- **Background**: `#3a1a1e` (dark red)
- **Color**: `#ff6b6b` (light red)
- **Padding**: 20px
- **Border Radius**: 8px
- **Margin**: 20px
- **Text Align**: Center

---

### 5. Chart Configuration
Using TradingView Lightweight Charts library

#### Chart Options
```javascript
{
  width: 800,
  height: 400,
  layout: {
    background: { color: '#0f0f23' },
    textColor: '#d9d9d9',
  },
  grid: {
    vertLines: { color: '#2B2B43' },
    horzLines: { color: '#2B2B43' },
  },
  timeScale: {
    borderColor: '#2B2B43',
    timeVisible: true,
    secondsVisible: false,
  },
}
```

#### Candlestick Colors
```javascript
{
  upColor: '#26a69a',        // Bullish candles (teal)
  downColor: '#ef5350',       // Bearish candles (red)
  borderUpColor: '#26a69a',
  borderDownColor: '#ef5350',
  wickUpColor: '#26a69a',
  wickDownColor: '#ef5350',
}
```

---

## Responsive Design

### Mobile (max-width: 768px)

**Header:**
- **Flex Direction**: Column
- **Gap**: 10px
- **Padding**: 10px

**Controls:**
- **Width**: 100%
- **Justify Content**: Stretch
- **Flex Wrap**: Wrap

**Symbol Input & Timeframe Select:**
- **Flex**: 1 (equal width)

**Chart Container:**
- **Padding**: 10px

---

## Typography

### Font Family
```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI',
             Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
```

### Font Sizes
- **Title**: 24px (bold)
- **Stat Value**: 18px (bold)
- **Loading/Error**: 18px
- **Controls**: 14px
- **Stat Label**: 12px
- **Status Text**: 12px

---

## Interactions & States

### Input Focus
- **Remove default outline**
- **Border Color**: Changes to accent (`#26a69a`)
- **Box Shadow**: `0 0 0 2px rgba(38, 166, 154, 0.2)` (glow effect)
- **Transition**: All 0.3s ease

### Status Indicator States
1. **Connecting**: Red dot pulsing + "Connecting..."
2. **Connected**: Green dot pulsing + "Connected"
3. **Disconnected**: Red dot pulsing + "Disconnected"
4. **Error**: Red dot pulsing + "Error"

---

## Shadows & Depth

### Header Shadow
```css
box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
```

### Chart Wrapper Shadow
```css
box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
```

---

## Key Features

1. **Dark Theme**: Professional trading terminal aesthetic
2. **Gradient Branding**: Modern gradient logo
3. **Real-time Status**: Animated connection indicator
4. **Responsive Layout**: Adapts to mobile and desktop
5. **Smooth Transitions**: 0.3s ease on interactive elements
6. **Stats Dashboard**: Key metrics at a glance
7. **Clean Spacing**: Consistent padding and gaps
8. **Professional Chart**: TradingView-style candlestick chart

---

## HTML Structure

```html
<div class="app-container">
  <header class="header">
    <h1 class="title">TradeX</h1>
    <div class="controls">
      <select class="timeframe-select" id="timeframeSelect">
        <option value="1H" selected>1H</option>
        <!-- More options -->
      </select>
      <input
        type="text"
        class="symbol-input"
        id="symbolInput"
        value="CME_MINI:MNQ1!"
      />
      <div class="status-indicator">
        <div class="status-dot" id="statusDot"></div>
        <span id="statusText">Connecting...</span>
      </div>
    </div>
  </header>

  <div class="chart-container">
    <div class="stats" id="statsContainer">
      <!-- 4 stat cards here -->
    </div>
    <div class="chart-wrapper">
      <div class="loading" id="loadingMessage">Initializing...</div>
      <div id="chartContainer"></div>
    </div>
  </div>
</div>
```

---

## Dependencies

### External Libraries
- **TradingView Lightweight Charts v5.1.0**
  - Import: `import { createChart, CandlestickSeries } from 'lightweight-charts'`

### Browser Support
- Modern browsers (Chrome, Firefox, Safari, Edge)
- CSS Grid and Flexbox support required
- WebSocket support required

---

## Implementation Notes

1. All styles are embedded in `<style>` tag in index.html
2. Chart is dynamically created and rendered in `#chartContainer`
3. Stats cards are hidden by default, shown when data loads
4. Loading message is hidden when chart initializes
5. Status indicator updates via JavaScript based on WebSocket state

---

**Design Philosophy**: Clean, professional, and focused on data visualization with minimal distractions.
