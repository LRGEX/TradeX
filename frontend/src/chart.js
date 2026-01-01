/**
 * TradeX Chart Module
 * Purpose: Initialize and manage TradingView Lightweight Charts
 */

import { createChart, CandlestickSeries } from 'lightweight-charts';

/**
 * ChartManager class
 * Handles chart creation, updates, and timeframe switching
 */
export class ChartManager {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.chart = null;
    this.candlestickSeries = null;
    this.currentSymbol = null;
    this.currentTimeframe = null;
  }

  /**
   * Initialize chart with TradingView Lightweight Charts
   * Configuration per UI_DESIGN.md
   */
  initialize() {
    if (!this.container) {
      throw new Error(`Chart container not found: ${this.containerId}`);
    }

    // Create chart with dark theme configuration
    this.chart = createChart(this.container, {
      width: this.container.clientWidth,
      height: 600,
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
      crosshair: {
        mode: 1,
      },
    });

    // Add candlestick series
    this.candlestickSeries = this.chart.addSeries(CandlestickSeries, {
      upColor: '#26a69a',
      downColor: '#ef5350',
      borderUpColor: '#26a69a',
      borderDownColor: '#ef5350',
      wickUpColor: '#26a69a',
      wickDownColor: '#ef5350',
    });

    // Handle resize
    window.addEventListener('resize', () => this.handleResize());

    console.log('[Chart] Initialized');
  }

  /**
   * Load historical data onto the chart
   * @param {Array} bars - Array of OHLCV bars
   */
  loadData(bars) {
    if (!this.candlestickSeries) {
      console.error('[Chart] Candlestick series not initialized');
      return;
    }

    // Convert backend format to TradingView format
    const chartData = bars.map(bar => ({
      time: bar.time,
      open: bar.open,
      high: bar.high,
      low: bar.low,
      close: bar.close,
    }));

    this.candlestickSeries.setData(chartData);

    // Fit content to show all data
    this.chart.timeScale().fitContent();

    console.log(`[Chart] Loaded ${chartData.length} bars`);
  }

  /**
   * Update chart with new real-time bar
   * @param {Object} bar - OHLCV bar
   */
  updateBar(bar) {
    if (!this.candlestickSeries) {
      console.error('[Chart] Candlestick series not initialized');
      return;
    }

    // Update or add new bar
    this.candlestickSeries.update({
      time: bar.time,
      open: bar.open,
      high: bar.high,
      low: bar.low,
      close: bar.close,
    });

    console.log(`[Chart] Updated bar: ${new Date(bar.time * 1000).toISOString()}`);
  }

  /**
   * Clear all data from chart
   */
  clear() {
    if (!this.candlestickSeries) {
      return;
    }

    this.candlestickSeries.setData([]);
    console.log('[Chart] Cleared');
  }

  /**
   * Handle window resize
   */
  handleResize() {
    if (!this.chart || !this.container) {
      return;
    }

    this.chart.applyOptions({
      width: this.container.clientWidth,
    });
  }

  /**
   * Destroy chart and cleanup
   */
  destroy() {
    if (this.chart) {
      this.chart.remove();
      this.chart = null;
      this.candlestickSeries = null;
      console.log('[Chart] Destroyed');
    }
  }

  /**
   * Set chart options (for timeframe switches)
   * @param {Object} options - Chart options
   */
  setOptions(options) {
    if (!this.chart) {
      return;
    }

    this.chart.applyOptions(options);
  }

  /**
   * Get chart instance (for advanced usage)
   */
  getChart() {
    return this.chart;
  }

  /**
   * Get candlestick series (for advanced usage)
   */
  getSeries() {
    return this.candlestickSeries;
  }
}
