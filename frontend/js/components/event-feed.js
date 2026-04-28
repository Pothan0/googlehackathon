/**
 * Sports Media Sentinel — Real-Time Event Feed
 */
import { formatTime, el, severityColor } from '../utils/helpers.js';

export class EventFeed {
  constructor(container, maxItems = 80) {
    this.container = container;
    this.maxItems = maxItems;
    this.events = [];
  }

  addEvent(event) {
    this.events.unshift(event);
    if (this.events.length > this.maxItems) this.events.pop();
    this._renderItem(event);

    // Remove old DOM nodes
    while (this.container.children.length > this.maxItems) {
      this.container.removeChild(this.container.lastChild);
    }
  }

  _renderItem(event) {
    const data = event.data || event;
    const topic = event.topic || '';

    let dotClass = 'info';
    let badgeClass = 'stream';
    let badgeText = 'STREAM';
    let title = data.subscriber_id || data.id || '';
    let detail = data.event_name || '';

    if (topic === 'piracy.detected' || data.type === 'piracy_detection') {
      dotClass = data.severity || 'high';
      badgeClass = 'detection';
      badgeText = data.piracy_label || data.piracy_type || 'DETECTION';
      title = `${data.platform || 'Unknown'} — ${data.piracy_label || data.piracy_type || ''}`;
      detail = `${data.event_name || ''} • Confidence: ${((data.confidence || 0) * 100).toFixed(1)}% • ${data.region || ''}`;
    } else if (topic === 'enforcement.executed' || data.type === 'enforcement_action') {
      dotClass = 'success';
      badgeClass = 'enforcement';
      badgeText = 'ENFORCED';
      title = `${data.platform || ''} — ${data.piracy_type || ''}`;
      const actions = data.actions_taken || [];
      detail = actions.join(' → ') || `Latency: ${data.latency_seconds}s`;
    }

    const ts = data.timestamp || event.timestamp || (Date.now() / 1000);

    const item = el('div', { className: 'event-item' },
      el('div', { className: `event-dot ${dotClass}` }),
      el('div', { className: 'event-time' }, formatTime(ts)),
      el('div', { className: 'event-content' },
        el('div', { className: 'event-title' }, title),
        el('div', { className: 'event-detail' }, detail),
      ),
      el('div', { className: `event-badge ${badgeClass}` }, badgeText),
    );

    this.container.insertBefore(item, this.container.firstChild);
  }

  clear() {
    this.events = [];
    this.container.innerHTML = '';
  }
}
