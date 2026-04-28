/**
 * Sports Media Sentinel — WebSocket Manager
 */
export class WebSocketManager {
  constructor() {
    this.ws = null;
    this.handlers = new Map();
    this.connected = false;
    this.reconnectDelay = 1000;
    this.maxReconnect = 10;
    this.attempts = 0;
    this.messageQueue = [];
  }

  connect(url) {
    try {
      this.ws = new WebSocket(url);

      this.ws.onopen = () => {
        this.connected = true;
        this.attempts = 0;
        this.reconnectDelay = 1000;
        this._flush();
        this._dispatch('_connected', {});
      };

      this.ws.onmessage = (e) => {
        try {
          const msg = JSON.parse(e.data);
          const topic = msg.topic || '_default';
          this._dispatch(topic, msg);
          this._dispatch('_all', msg);
        } catch (err) { /* ignore malformed */ }
      };

      this.ws.onclose = () => {
        this.connected = false;
        this._dispatch('_disconnected', {});
        this._reconnect(url);
      };

      this.ws.onerror = () => {
        this.connected = false;
      };
    } catch (err) {
      this._reconnect(url);
    }
  }

  _reconnect(url) {
    if (this.attempts >= this.maxReconnect) return;
    this.attempts++;
    setTimeout(() => this.connect(url), this.reconnectDelay);
    this.reconnectDelay = Math.min(this.reconnectDelay * 1.5, 10000);
  }

  on(topic, handler) {
    if (!this.handlers.has(topic)) this.handlers.set(topic, []);
    this.handlers.get(topic).push(handler);
  }

  off(topic, handler) {
    const list = this.handlers.get(topic);
    if (list) {
      const idx = list.indexOf(handler);
      if (idx >= 0) list.splice(idx, 1);
    }
  }

  _dispatch(topic, data) {
    const list = this.handlers.get(topic) || [];
    for (const h of list) {
      try { h(data); } catch (e) { /* handler error */ }
    }
  }

  send(data) {
    const msg = typeof data === 'string' ? data : JSON.stringify(data);
    if (this.connected && this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(msg);
    } else {
      this.messageQueue.push(msg);
    }
  }

  _flush() {
    while (this.messageQueue.length > 0) {
      const msg = this.messageQueue.shift();
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.ws.send(msg);
      }
    }
  }

  destroy() {
    this.maxReconnect = 0;
    this.ws?.close();
  }
}

export const wsManager = new WebSocketManager();
