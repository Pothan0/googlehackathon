/**
 * Sports Media Sentinel — Pipeline Visualization
 */
import { formatNumber, el } from '../utils/helpers.js';

const STAGES = [
  { key: 'capture',    name: 'Capture',    num: '01', tech: 'C2PA / Sony SDK' },
  { key: 'ingest',     name: 'Ingest',     num: '02', tech: 'FFmpeg / Kafka' },
  { key: 'watermark',  name: 'Watermark',  num: '03', tech: 'DCT Encoder' },
  { key: 'distribute', name: 'Distribute', num: '04', tech: 'CDN / DRM' },
  { key: 'crawl',      name: 'Crawl',      num: '05', tech: 'Storm / Redis' },
  { key: 'detect',     name: 'Detect',     num: '06', tech: 'MMD-Agent' },
  { key: 'enforce',    name: 'Enforce',     num: '07', tech: 'Story Protocol' },
];

export class PipelineViz {
  constructor(container) {
    this.container = container;
    this.stageEls = {};
    this._build();
  }

  _build() {
    this.container.innerHTML = '';
    this.container.className = 'pipeline-flow';

    for (const stage of STAGES) {
      const stageEl = el('div', { className: 'pipe-stage', id: `pipe-${stage.key}` },
        el('div', { className: 'pipe-stage-num' }, `STEP ${stage.num}`),
        el('div', { className: 'pipe-stage-name' }, stage.name),
        el('div', { className: 'pipe-stage-count', id: `pipe-count-${stage.key}` }, '0'),
        el('div', { className: 'pipe-stage-rate', id: `pipe-rate-${stage.key}` }, `0/min • ${stage.tech}`),
      );
      this.container.appendChild(stageEl);
      this.stageEls[stage.key] = stageEl;
    }
  }

  update(stageCounts, throughput) {
    for (const stage of STAGES) {
      const countEl = document.getElementById(`pipe-count-${stage.key}`);
      const rateEl = document.getElementById(`pipe-rate-${stage.key}`);
      if (countEl) countEl.textContent = formatNumber(stageCounts[stage.key] || 0);
      if (rateEl) rateEl.textContent = `${throughput[stage.key] || 0}/min • ${stage.tech}`;
    }
  }

  highlightStage(stageKey, type = 'active') {
    const el = this.stageEls[stageKey];
    if (!el) return;
    el.classList.add(type);
    setTimeout(() => el.classList.remove(type), 1500);
  }
}
