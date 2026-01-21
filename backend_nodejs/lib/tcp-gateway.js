/**
 * TCP Gateway Client - Connects to ESP32 Gateway
 * Handles TCP communication with IoT devices
 */

const net = require('net');
const EventEmitter = require('events');

class TCPGateway extends EventEmitter {
  constructor(host, port) {
    super();
    this.host = host;
    this.port = port;
    this.client = null;
    this.connected = false;
    this.retryCount = 0;
    this.maxRetries = 10;
    this.retryDelay = 1000; // ms
  }

  connect() {
    return new Promise((resolve, reject) => {
      this.retryCount++;
      console.log(`[TCP] Gateway connection attempt #${this.retryCount}, retry_delay=${this.retryDelay}ms`);

      const client = net.createConnection({ host: this.host, port: this.port });

      client.on('connect', () => {
        this.client = client;
        this.connected = true;
        this.retryCount = 0;
        this.retryDelay = 1000;
        console.log(`[TCP] Connected to gateway at ${this.host}:${this.port}`);
        this.emit('connected');
        resolve();
      });

      client.on('data', (data) => {
        console.log(`[TCP] Rx data: ${data.length} bytes`);
        this.emit('data', data);
      });

      client.on('error', (err) => {
        console.error(`[TCP] Error: ${err.message}`);
        this.emit('error', err);
        this.reconnect();
      });

      client.on('close', () => {
        console.log('[TCP] Connection closed');
        this.connected = false;
        this.client = null;
        this.emit('closed');
        this.reconnect();
      });

      setTimeout(() => {
        if (!this.connected && this.retryCount <= this.maxRetries) {
          client.destroy();
          this.reconnect();
        }
      }, 5000);
    });
  }

  reconnect() {
    if (this.retryCount >= this.maxRetries) {
      console.log('[TCP] Max retries reached');
      return;
    }

    setTimeout(() => {
      this.connect().catch(err => {
        console.error('[TCP] Reconnect failed:', err.message);
      });
    }, this.retryDelay);

    this.retryDelay = Math.min(this.retryDelay * 1.5, 30000);
  }

  send(data) {
    if (!this.client || !this.connected) {
      console.warn('[TCP] Not connected, cannot send data');
      return false;
    }
    try {
      this.client.write(data);
      console.log(`[TCP] Tx data: ${data.length} bytes`);
      return true;
    } catch (err) {
      console.error('[TCP] Send error:', err.message);
      return false;
    }
  }

  disconnect() {
    if (this.client) {
      this.client.destroy();
      this.client = null;
      this.connected = false;
    }
  }
}

module.exports = TCPGateway;
