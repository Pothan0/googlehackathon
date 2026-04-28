/**
 * Sports Media Sentinel — Real-Time SOC Dashboard
 */
import { RollingLineChart, BarChart } from '../components/charts.js';
import { EventFeed } from '../components/event-feed.js';
import { WorldMap } from '../components/world-map.js';
import { MetricsPanel } from '../components/metrics.js';
import { PipelineViz } from '../components/pipeline-viz.js';

let detectionChart, latencyChart, severityChart, eventFeed, worldMap, metricsPanel, pipelineViz;
let chartInterval;

export function renderDashboard(container) {
  container.innerHTML = `
    <div class="page-content">
      <!-- KPI Row -->
      <div class="section" style="padding-top:24px;">
        <div id="dash-kpis"></div>
      </div>

      <!-- Pipeline -->
      <div class="section" style="padding-top:0;">
        <div class="panel-header">
          <div class="panel-title">// Pipeline Status — 7-Stage Flow</div>
          <div class="panel-badge live">● Live</div>
        </div>
        <div id="dash-pipeline"></div>
      </div>

      <!-- Map + Event Feed -->
      <div class="section" style="padding-top:0;">
        <div class="dash-grid">
          <div class="dash-panel">
            <div class="panel-header">
              <div class="panel-title">// Global Piracy Heatmap</div>
              <div class="panel-badge live">● Live</div>
            </div>
            <div class="world-map-container" id="dash-map"></div>
          </div>
          <div class="dash-panel">
            <div class="panel-header">
              <div class="panel-title">// Event Feed</div>
              <div class="panel-badge live">● Live</div>
            </div>
            <div class="event-feed" id="dash-events"></div>
          </div>
        </div>
      </div>

      <!-- Charts -->
      <div class="section" style="padding-top:0;">
        <div class="dash-grid-3">
          <div class="dash-panel">
            <div class="panel-header">
              <div class="panel-title">// Detection Rate</div>
            </div>
            <div class="chart-container"><canvas id="chart-detections"></canvas></div>
          </div>
          <div class="dash-panel">
            <div class="panel-header">
              <div class="panel-title">// Enforcement Latency</div>
            </div>
            <div class="chart-container"><canvas id="chart-latency"></canvas></div>
          </div>
          <div class="dash-panel">
            <div class="panel-header">
              <div class="panel-title">// Severity Distribution</div>
            </div>
            <div class="chart-container"><canvas id="chart-severity"></canvas></div>
          </div>
        </div>
      </div>
    </div>
  `;

  // Initialize components
  metricsPanel = new MetricsPanel(document.getElementById('dash-kpis'));
  metricsPanel.init([
    { key: 'total_streams',         label: 'Streams Monitored',   variant: 'info',    format: 'number' },
    { key: 'active_threats',        label: 'Active Threats',      variant: 'danger',  format: 'number' },
    { key: 'total_detections',      label: 'Total Detections',    variant: 'danger',  format: 'number' },
    { key: 'total_enforcements',    label: 'Enforcements',        variant: 'success', format: 'number' },
    { key: 'avg_takedown_latency',  label: 'Avg Takedown',        variant: 'info',    format: 'seconds' },
    { key: 'sla_compliance',        label: 'SLA Compliance',      variant: 'success', format: 'percent' },
    { key: 'detection_rate_per_min',label: 'Detections/Min',      variant: 'danger',  format: 'number' },
    { key: 'false_positive_rate',   label: 'False Positive',      variant: 'info',    format: 'percent' },
  ]);

  pipelineViz = new PipelineViz(document.getElementById('dash-pipeline'));
  worldMap = new WorldMap(document.getElementById('dash-map'));
  eventFeed = new EventFeed(document.getElementById('dash-events'));

  // Charts
  const detCanvas = document.getElementById('chart-detections');
  const latCanvas = document.getElementById('chart-latency');
  const sevCanvas = document.getElementById('chart-severity');

  detectionChart = new RollingLineChart(detCanvas, {
    lineColor: '#ff3d57', fillColor: 'rgba(255,61,87,.1)', label: 'Detections / 10s'
  });
  latencyChart = new RollingLineChart(latCanvas, {
    lineColor: '#00e5ff', fillColor: 'rgba(0,229,255,.08)', label: 'Avg Latency (s)'
  });
  severityChart = new BarChart(sevCanvas, {
    colors: { critical: '#ff3d57', high: '#ff9500', medium: '#ffd60a', low: '#4a6070' },
    label: 'Severity'
  });

  // Render loop
  chartInterval = setInterval(() => {
    detectionChart.render();
    latencyChart.render();
    severityChart.render();
  }, 500);
}

export function handleDashboardEvent(msg) {
  const topic = msg.topic;
  const data = msg.data || {};

  if (topic === 'piracy.detected') {
    eventFeed?.addEvent(msg);
    worldMap?.addDetection(data.latitude, data.longitude, data.severity);
    pipelineViz?.highlightStage('detect', 'alert');
  } else if (topic === 'enforcement.executed') {
    eventFeed?.addEvent(msg);
    worldMap?.addDetection(data.latitude, data.longitude, 'enforcement');
    pipelineViz?.highlightStage('enforce', 'active');
  } else if (topic === 'stream.active') {
    pipelineViz?.highlightStage('distribute', 'active');
  }
}

export function updateDashboardKPIs(kpis) {
  metricsPanel?.updateAll(kpis);
  detectionChart?.push(kpis.detection_rate_per_min || 0);
  latencyChart?.push(kpis.avg_takedown_latency || 0);
  severityChart?.update(kpis._severity || { critical: 0, high: 0, medium: 0, low: 0 });
}

export function updateDashboardPipeline(pipelineStats) {
  pipelineViz?.update(
    pipelineStats.stage_counts || {},
    pipelineStats.throughput_per_min || {},
  );
}

export function destroyDashboard() {
  if (chartInterval) clearInterval(chartInterval);
  chartInterval = null;
}
