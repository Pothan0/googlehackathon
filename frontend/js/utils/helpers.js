/**
 * Sports Media Sentinel — Utility Helpers
 */
export function formatTime(ts) {
  const d = new Date(ts * 1000);
  return d.toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

export function formatNumber(n) {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + 'M';
  if (n >= 1_000) return (n / 1_000).toFixed(1) + 'K';
  return String(n);
}

export function formatCurrency(n) {
  return '$' + n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

export function shortHash(hash) {
  if (!hash) return '';
  return hash.slice(0, 6) + '…' + hash.slice(-4);
}

export function randomId() {
  return Math.random().toString(36).slice(2, 10);
}

export function clamp(val, min, max) {
  return Math.max(min, Math.min(max, val));
}

export function lerp(a, b, t) {
  return a + (b - a) * t;
}

export function el(tag, attrs = {}, ...children) {
  const element = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === 'className') element.className = v;
    else if (k === 'style' && typeof v === 'object') Object.assign(element.style, v);
    else if (k.startsWith('on')) element.addEventListener(k.slice(2).toLowerCase(), v);
    else element.setAttribute(k, v);
  }
  for (const child of children) {
    if (typeof child === 'string') element.appendChild(document.createTextNode(child));
    else if (child) element.appendChild(child);
  }
  return element;
}

export function severityColor(severity) {
  const map = {
    critical: 'var(--accent2)',
    high: '#ff9500',
    medium: '#ffd60a',
    low: 'var(--muted)',
  };
  return map[severity] || 'var(--muted)';
}
