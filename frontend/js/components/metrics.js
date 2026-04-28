/**
 * Sports Media Sentinel — KPI Metrics Component
 */
import { formatNumber, el } from '../utils/helpers.js';

export class MetricsPanel {
  constructor(container) {
    this.container = container;
    this.cards = {};
  }

  init(definitions) {
    this.container.innerHTML = '';
    this.container.className = 'kpi-row';
    for (const def of definitions) {
      const card = el('div', { className: `kpi-card ${def.variant || 'info'}`, id: `kpi-${def.key}` },
        el('div', { className: 'kpi-label' }, def.label),
        el('div', { className: `kpi-value ${def.variant || ''}`, id: `kpi-val-${def.key}` }, def.initial || '0'),
        el('div', { className: 'kpi-sub', id: `kpi-sub-${def.key}` }, def.sub || ''),
      );
      this.container.appendChild(card);
      this.cards[def.key] = {
        valueEl: card.querySelector(`#kpi-val-${def.key}`),
        subEl: card.querySelector(`#kpi-sub-${def.key}`),
        format: def.format || 'number',
      };
    }
  }

  update(key, value, sub) {
    const card = this.cards[key];
    if (!card) return;
    let display;
    switch (card.format) {
      case 'number': display = formatNumber(value); break;
      case 'percent': display = value.toFixed(1) + '%'; break;
      case 'seconds': display = value.toFixed(1) + 's'; break;
      case 'currency': display = '$' + formatNumber(value); break;
      default: display = String(value);
    }
    card.valueEl.textContent = display;
    if (sub !== undefined) card.subEl.textContent = sub;
  }

  updateAll(data) {
    for (const [key, val] of Object.entries(data)) {
      if (this.cards[key]) {
        this.update(key, typeof val === 'object' ? val.value : val, typeof val === 'object' ? val.sub : undefined);
      }
    }
  }
}
