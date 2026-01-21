/**
 * Message Bus - Pub/Sub event system
 * Allows modules to communicate without tight coupling
 */

const EventEmitter = require('events');

class MessageBus extends EventEmitter {
  constructor() {
    super();
    this.setMaxListeners(100); // Allow many listeners
  }

  /**
   * Publish an event
   * @param {string} topic - Topic name
   * @param {object} data - Event data
   */
  publish(topic, data) {
    console.log(`[Bus] Publishing: ${topic}`, data);
    this.emit(topic, data);
  }

  /**
   * Subscribe to an event
   * @param {string} topic - Topic name
   * @param {function} handler - Event handler
   */
  subscribe(topic, handler) {
    console.log(`[Bus] Subscribing to: ${topic}`);
    this.on(topic, handler);
    // Return unsubscribe function
    return () => this.unsubscribe(topic, handler);
  }

  /**
   * Unsubscribe from an event
   */
  unsubscribe(topic, handler) {
    this.off(topic, handler);
  }
}

// Singleton instance
const bus = new MessageBus();

module.exports = bus;
