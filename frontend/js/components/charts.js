/**
 * Sports Media Sentinel — Canvas Charts
 */
export class RollingLineChart {
  constructor(canvas, opts = {}) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.data = [];
    this.maxPoints = opts.maxPoints || 60;
    this.lineColor = opts.lineColor || '#00e5ff';
    this.fillColor = opts.fillColor || 'rgba(0,229,255,.08)';
    this.gridColor = opts.gridColor || 'rgba(30,45,61,.5)';
    this.label = opts.label || '';
    this.maxValue = opts.maxValue || 0;
    this._resize();
    window.addEventListener('resize', () => this._resize());
  }

  _resize() {
    const rect = this.canvas.parentElement.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    this.canvas.width = rect.width * dpr;
    this.canvas.height = rect.height * dpr;
    this.ctx.scale(dpr, dpr);
    this.w = rect.width;
    this.h = rect.height;
  }

  push(value) {
    this.data.push(value);
    if (this.data.length > this.maxPoints) this.data.shift();
    if (this.maxValue === 0 || value > this.maxValue) {
      this.maxValue = Math.max(value * 1.2, 1);
    }
  }

  render() {
    const { ctx, w, h, data, maxValue } = this;
    ctx.clearRect(0, 0, w, h);
    if (data.length < 2) return;

    const padTop = 20, padBot = 24, padLeft = 40, padRight = 8;
    const cw = w - padLeft - padRight;
    const ch = h - padTop - padBot;

    // Grid
    ctx.strokeStyle = this.gridColor;
    ctx.lineWidth = 0.5;
    for (let i = 0; i <= 4; i++) {
      const y = padTop + (ch / 4) * i;
      ctx.beginPath();
      ctx.moveTo(padLeft, y);
      ctx.lineTo(w - padRight, y);
      ctx.stroke();
      // labels
      const val = maxValue - (maxValue / 4) * i;
      ctx.fillStyle = '#4a6070';
      ctx.font = '9px IBM Plex Mono';
      ctx.textAlign = 'right';
      ctx.fillText(Math.round(val), padLeft - 6, y + 3);
    }

    // Line
    const step = cw / (this.maxPoints - 1);
    const startIdx = this.maxPoints - data.length;

    ctx.beginPath();
    for (let i = 0; i < data.length; i++) {
      const x = padLeft + (startIdx + i) * step;
      const y = padTop + ch - (data[i] / maxValue) * ch;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }

    ctx.strokeStyle = this.lineColor;
    ctx.lineWidth = 2;
    ctx.lineJoin = 'round';
    ctx.stroke();

    // Fill
    const lastX = padLeft + (startIdx + data.length - 1) * step;
    ctx.lineTo(lastX, padTop + ch);
    ctx.lineTo(padLeft + startIdx * step, padTop + ch);
    ctx.closePath();

    const grad = ctx.createLinearGradient(0, padTop, 0, padTop + ch);
    grad.addColorStop(0, this.fillColor);
    grad.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = grad;
    ctx.fill();

    // Label
    if (this.label) {
      ctx.fillStyle = '#4a6070';
      ctx.font = '9px IBM Plex Mono';
      ctx.textAlign = 'left';
      ctx.fillText(this.label.toUpperCase(), padLeft, h - 4);
    }

    // Current value
    if (data.length > 0) {
      const cur = data[data.length - 1];
      ctx.fillStyle = this.lineColor;
      ctx.font = 'bold 12px IBM Plex Sans';
      ctx.textAlign = 'right';
      ctx.fillText(Math.round(cur), w - padRight, padTop - 6);
    }
  }
}

export class BarChart {
  constructor(canvas, opts = {}) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.data = {};
    this.colors = opts.colors || {};
    this.label = opts.label || '';
    this._resize();
    window.addEventListener('resize', () => this._resize());
  }

  _resize() {
    const rect = this.canvas.parentElement.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    this.canvas.width = rect.width * dpr;
    this.canvas.height = rect.height * dpr;
    this.ctx.scale(dpr, dpr);
    this.w = rect.width;
    this.h = rect.height;
  }

  update(data) { this.data = data; }

  render() {
    const { ctx, w, h, data } = this;
    ctx.clearRect(0, 0, w, h);

    const keys = Object.keys(data);
    if (keys.length === 0) return;

    const padTop = 16, padBot = 28, padLeft = 8, padRight = 8;
    const cw = w - padLeft - padRight;
    const ch = h - padTop - padBot;
    const maxVal = Math.max(...Object.values(data), 1);
    const barW = Math.min((cw / keys.length) - 8, 40);
    const gap = (cw - barW * keys.length) / (keys.length + 1);

    keys.forEach((key, i) => {
      const x = padLeft + gap + i * (barW + gap);
      const barH = (data[key] / maxVal) * ch;
      const y = padTop + ch - barH;
      const color = this.colors[key] || '#00e5ff';

      // Bar
      ctx.fillStyle = color;
      ctx.fillRect(x, y, barW, barH);

      // Glow
      ctx.fillStyle = color.replace(')', ',.15)').replace('rgb', 'rgba');
      ctx.fillRect(x - 2, y - 2, barW + 4, barH + 4);
      ctx.fillStyle = color;
      ctx.fillRect(x, y, barW, barH);

      // Label
      ctx.fillStyle = '#4a6070';
      ctx.font = '8px IBM Plex Mono';
      ctx.textAlign = 'center';
      ctx.fillText(key.slice(0, 6).toUpperCase(), x + barW / 2, h - 6);

      // Value
      ctx.fillStyle = '#f0f6ff';
      ctx.font = '10px IBM Plex Mono';
      ctx.fillText(data[key], x + barW / 2, y - 4);
    });
  }
}
