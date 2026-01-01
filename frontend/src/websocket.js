/**
 * TradeX WebSocket Client
 * Purpose: Connect to backend WebSocket for real-time chart updates
 */

const WS_URL = 'ws://localhost:8000/ws/chart';

/**
 * WebSocketClient class
 * Manages WebSocket connection to backend and handles real-time updates
 */
export class WebSocketClient {
  constructor(url = WS_URL) {
    this.url = url;
    this.ws = null;
    this.connected = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000; // Start with 1 second
    this.onBarUpdate = null;
    this.onConnectionChange = null;
    this.onSymbolChange = null;
  }

  /**
   * Connect to backend WebSocket
   */
  connect() {
    try {
      console.log(`[WS] Connecting to ${this.url}...`);

      this.ws = new WebSocket(this.url);

      // Connection opened
      this.ws.addEventListener('open', () => {
        console.log('[WS] Connected');
        this.connected = true;
        this.reconnectAttempts = 0;
        this.reconnectDelay = 1000;

        // Notify connection change
        if (this.onConnectionChange) {
          this.onConnectionChange('connected');
        }
      });

      // Connection closed
      this.ws.addEventListener('close', (event) => {
        console.log(`[WS] Disconnected: ${event.code} ${event.reason}`);
        this.connected = false;

        // Notify connection change
        if (this.onConnectionChange) {
          this.onConnectionChange('disconnected');
        }

        // Attempt to reconnect
        this.attemptReconnect();
      });

      // Connection error
      this.ws.addEventListener('error', (error) => {
        console.error('[WS] Error:', error);

        // Notify connection change
        if (this.onConnectionChange) {
          this.onConnectionChange('error');
        }
      });

      // Message received
      this.ws.addEventListener('message', (event) => {
        this.handleMessage(event.data);
      });

    } catch (error) {
      console.error('[WS] Connection error:', error);
      this.attemptReconnect();
    }
  }

  /**
   * Handle incoming WebSocket message
   * @param {string} data - Message data (JSON or text)
   */
  handleMessage(data) {
    try {
      const message = JSON.parse(data);

      // Handle connection status message
      if (message.type === 'connection_status') {
        console.log(`[WS] Status: ${message.status} - ${message.message}`);
        return;
      }

      // Handle symbol changed message
      if (message.type === 'symbol_changed') {
        console.log(`[WS] Symbol changed to: ${message.symbol}`);
        // Notify callback
        if (this.onSymbolChange) {
          this.onSymbolChange(message.symbol);
        }
        return;
      }

      // Handle bar update message
      if (message.type === 'bar_update') {
        console.log(`[WS] Bar update: ${message.timeframe} (${message.bars.length} bars)`);

        // Notify callback
        if (this.onBarUpdate) {
          this.onBarUpdate(message.timeframe, message.bars);
        }
      }

    } catch (error) {
      console.error('[WS] Message parse error:', error);
    }
  }

  /**
   * Attempt to reconnect to WebSocket
   */
  attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('[WS] Max reconnect attempts reached');
      return;
    }

    this.reconnectAttempts++;

    console.log(`[WS] Reconnecting in ${this.reconnectDelay / 1000}s (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);

    setTimeout(() => {
      this.reconnectDelay *= 2; // Exponential backoff
      this.connect();
    }, this.reconnectDelay);
  }

  /**
   * Disconnect from WebSocket
   */
  disconnect() {
    if (this.ws) {
      console.log('[WS] Disconnecting...');
      this.ws.close();
      this.ws = null;
      this.connected = false;
    }
  }

  /**
   * Set callback for bar updates
   * @param {Function} callback - Callback function (timeframe, bars) => void
   */
  setOnBarUpdate(callback) {
    this.onBarUpdate = callback;
  }

  /**
   * Set callback for connection state changes
   * @param {Function} callback - Callback function (status) => void
   */
  setOnConnectionChange(callback) {
    this.onConnectionChange = callback;
  }

  /**
   * Set callback for symbol changes
   * @param {Function} callback - Callback function (symbol) => void
   */
  setOnSymbolChange(callback) {
    this.onSymbolChange = callback;
  }

  /**
   * Check if connected
   * @returns {boolean} Connection status
   */
  isConnected() {
    return this.connected;
  }
}
