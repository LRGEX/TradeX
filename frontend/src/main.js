/**
 * TradeX Main Application
 * Purpose: Orchestrate all components and handle user interactions
 */

import { ChartManager } from './chart.js';
import { api } from './api.js';
import { WebSocketClient } from './websocket.js';

/**
 * TradeXApp class
 * Main application controller
 */
class TradeXApp {
  constructor() {
    this.chartManager = new ChartManager('chartContainer');
    this.wsClient = new WebSocketClient();
    this.currentSymbol = 'CME_MINI:MNQ1!';
    this.currentTimeframe = '1H';

    // UI elements
    this.elements = {
      symbolSelect: document.getElementById('symbolSelect'),
      timeframeSelect: document.getElementById('timeframeSelect'),
      symbolInput: document.getElementById('symbolInput'),
      statusDot: document.getElementById('statusDot'),
      statusText: document.getElementById('statusText'),
      loadingMessage: document.getElementById('loadingMessage'),
      errorMessage: document.getElementById('errorMessage'),
      statsContainer: document.getElementById('statsContainer'),
      statSymbol: document.getElementById('statSymbol'),
      statTimeframe: document.getElementById('statTimeframe'),
      statBars: document.getElementById('statBars'),
      statUpdate: document.getElementById('statUpdate')
    };
  }

  /**
   * Initialize application
   */
  async initialize() {
    console.log('[App] Initializing TradeX...');

    try {
      // Initialize chart
      this.chartManager.initialize();
      console.log('[App] Chart initialized');

      // Setup WebSocket callbacks
      this.wsClient.setOnBarUpdate((timeframe, bars) => {
        this.handleBarUpdate(timeframe, bars);
      });

      this.wsClient.setOnConnectionChange((status) => {
        this.handleConnectionChange(status);
      });

      // Connect to backend WebSocket
      this.wsClient.connect();

      // Setup event listeners
      this.setupEventListeners();

      // Fetch initial data
      await this.loadInitialData();

      console.log('[App] Initialization complete');

    } catch (error) {
      console.error('[App] Initialization error:', error);
      this.showError(`Failed to initialize: ${error.message}`);
    }
  }

  /**
   * Setup event listeners
   */
  setupEventListeners() {
    // Symbol dropdown change
    this.elements.symbolSelect.addEventListener('change', async (e) => {
      const newSymbol = e.target.value;
      if (newSymbol && newSymbol !== this.currentSymbol) {
        this.currentSymbol = newSymbol;
        this.elements.symbolInput.value = newSymbol; // Sync input field
        console.log(`[App] Symbol changed to: ${this.currentSymbol}`);
        await this.loadChartData();
      }
    });

    // Timeframe change
    this.elements.timeframeSelect.addEventListener('change', async (e) => {
      this.currentTimeframe = e.target.value;
      console.log(`[App] Timeframe changed to: ${this.currentTimeframe}`);
      await this.loadChartData();
    });

    // Symbol change (on Enter key)
    this.elements.symbolInput.addEventListener('keypress', async (e) => {
      if (e.key === 'Enter') {
        const newSymbol = e.target.value.trim();
        if (newSymbol && newSymbol !== this.currentSymbol) {
          this.currentSymbol = newSymbol;
          console.log(`[App] Symbol changed to: ${this.currentSymbol}`);
          await this.loadChartData();
        }
      }
    });
  }

  /**
   * Load initial data for default timeframe
   */
  async loadInitialData() {
    try {
      this.showLoading('Fetching historical data...');

      const data = await api.fetchChartHistory(
        this.currentSymbol,
        this.currentTimeframe,
        1000
      );

      // Load data into chart
      this.chartManager.loadData(data.bars);

      // Update stats
      this.updateStats(data);

      // Hide loading, show stats
      this.elements.loadingMessage.classList.add('hidden');
      this.elements.statsContainer.classList.add('visible');

    } catch (error) {
      console.error('[App] Failed to load initial data:', error);
      this.showError(`Failed to load data: ${error.message}`);
    }
  }

  /**
   * Load chart data for current symbol and timeframe
   */
  async loadChartData() {
    try {
      this.showLoading('Switching symbol...');

      // Switch WebSocket subscription to new symbol
      try {
        await api.subscribeSymbol(this.currentSymbol);
        console.log(`[App] WebSocket switched to ${this.currentSymbol}`);
      } catch (wsError) {
        console.warn('[App] WebSocket switch failed, continuing with data fetch:', wsError);
        // Don't fail the whole operation if WebSocket switch fails
      }

      this.showLoading('Loading chart data...');

      const data = await api.fetchChartHistory(
        this.currentSymbol,
        this.currentTimeframe,
        1000
      );

      // Clear and reload chart
      this.chartManager.clear();
      this.chartManager.loadData(data.bars);

      // Update stats
      this.updateStats(data);

      // Hide loading, show stats
      this.elements.loadingMessage.classList.add('hidden');
      this.elements.statsContainer.classList.add('visible');

      // Clear error if any
      this.elements.errorMessage.classList.remove('visible');

    } catch (error) {
      console.error('[App] Failed to load chart data:', error);
      this.showError(`Failed to load chart data: ${error.message}`);
    }
  }

  /**
   * Handle real-time bar update from WebSocket
   * @param {string} timeframe - Timeframe of the update
   * @param {Array} bars - Array of bars (usually 1 bar)
   */
  handleBarUpdate(timeframe, bars) {
    // Only update if matches current timeframe
    if (timeframe !== this.currentTimeframe) {
      return;
    }

    console.log(`[App] Received ${bars.length} bar(s) for ${timeframe}`);

    // Update chart with new bar
    if (bars.length > 0) {
      this.chartManager.updateBar(bars[0]);

      // Update last update time
      const now = new Date();
      this.elements.statUpdate.textContent = now.toLocaleTimeString();
    }
  }

  /**
   * Handle WebSocket connection state change
   * @param {string} status - Connection status (connected, disconnected, error)
   */
  handleConnectionChange(status) {
    console.log(`[App] Connection status: ${status}`);

    switch (status) {
      case 'connected':
        this.elements.statusDot.classList.add('connected');
        this.elements.statusText.textContent = 'Connected';
        break;
      case 'disconnected':
        this.elements.statusDot.classList.remove('connected');
        this.elements.statusText.textContent = 'Disconnected';
        break;
      case 'error':
        this.elements.statusDot.classList.remove('connected');
        this.elements.statusText.textContent = 'Error';
        break;
    }
  }

  /**
   * Update stats cards
   * @param {Object} data - Chart history response data
   */
  updateStats(data) {
    this.elements.statSymbol.textContent = data.symbol;
    this.elements.statTimeframe.textContent = data.timeframe;
    this.elements.statBars.textContent = data.count;

    const lastBar = data.bars[data.bars.length - 1];
    if (lastBar) {
      const timestamp = new Date(lastBar.time * 1000);
      this.elements.statUpdate.textContent = timestamp.toLocaleString();
    }
  }

  /**
   * Show loading message
   * @param {string} message - Loading message
   */
  showLoading(message) {
    this.elements.loadingMessage.textContent = message;
    this.elements.loadingMessage.classList.remove('hidden');
    this.elements.errorMessage.classList.remove('visible');
  }

  /**
   * Show error message
   * @param {string} message - Error message
   */
  showError(message) {
    this.elements.errorMessage.textContent = message;
    this.elements.errorMessage.classList.add('visible');
    this.elements.loadingMessage.classList.add('hidden');
  }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  console.log('[App] DOM ready, starting application...');

  const app = new TradeXApp();
  app.initialize();
});
