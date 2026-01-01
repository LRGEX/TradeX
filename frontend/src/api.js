/**
 * TradeX Backend API Client
 * Purpose: Communicate with backend REST API for historical data
 */

const API_BASE_URL = 'http://localhost:8000';

/**
 * BackendAPI class
 * Handles all REST API communication with the backend
 */
export class BackendAPI {
  constructor(baseUrl = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Fetch historical OHLCV data from backend
   * @param {string} symbol - Trading symbol (e.g., "CME_MINI:MNQ1!")
   * @param {string} timeframe - Timeframe (1m, 5m, 15m, 30m, 1H, 4H, 1D, 1W, 1M)
   * @param {number} bars - Number of bars to fetch (default: 1000)
   * @returns {Promise<Object>} Response with symbol, timeframe, bars, count, cached
   */
  async fetchChartHistory(symbol, timeframe, bars = 1000) {
    const params = new URLSearchParams({
      symbol: symbol,
      timeframe: timeframe,
      bars: bars.toString()
    });

    const url = `${this.baseUrl}/api/chart/history?${params}`;

    try {
      console.log(`[API] Fetching: ${symbol} ${timeframe} ${bars} bars`);

      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      console.log(`[API] Received ${data.count} bars (cached: ${data.cached})`);

      return data;
    } catch (error) {
      console.error('[API] Fetch error:', error);
      throw error;
    }
  }

  /**
   * Get timeframe statistics
   * @param {string} symbol - Trading symbol
   * @param {string} timeframe - Timeframe
   * @returns {Promise<Object>} Stats with symbol, timeframe, bars_loaded, last_update
   */
  async getTimeframeStats(symbol, timeframe) {
    const params = new URLSearchParams({
      symbol: symbol,
      timeframe: timeframe
    });

    const url = `${this.baseUrl}/api/stats/timeframe?${params}`;

    try {
      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('[API] Stats error:', error);
      throw error;
    }
  }

  /**
   * Health check endpoint
   * @returns {Promise<Object>} Health status
   */
  async healthCheck() {
    const url = `${this.baseUrl}/api/health`;

    try {
      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('[API] Health check error:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const api = new BackendAPI();
