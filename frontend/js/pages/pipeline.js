/**
 * Sports Media Sentinel — Live Pipeline Monitor Page
 */
import { PipelineViz } from '../components/pipeline-viz.js';
import { EventFeed } from '../components/event-feed.js';

let pipelineViz, pipelineFeed;

export function renderPipeline(container) {
  container.innerHTML = `
    <div class="page-content">
      <div class="section" style="padding-top:24px">
        <div class="section-header">
          <span class="section-num">03</span>
          <h2 class="section-title">Real-Time Data Pipeline</h2>
        </div>
        <p style="color:var(--muted);margin-bottom:24px;max-width:700px;">
          Watch events flow through the 7-stage pipeline in real-time. Each stage processes
          events from capture through enforcement, with live throughput counters and latency tracking.
        </p>
        <div id="pipeline-main"></div>
      </div>

      <div class="section" style="padding-top:0">
        <div class="dash-grid">
          <div class="dash-panel">
            <div class="panel-header">
              <div class="panel-title">// Pipeline Event Log</div>
              <div class="panel-badge live">● Live</div>
            </div>
            <div class="event-feed" id="pipeline-events" style="max-height:500px;"></div>
          </div>
          <div class="dash-panel">
            <div class="panel-header">
              <div class="panel-title">// Stage Details</div>
            </div>
            <div id="pipeline-details">
              <div class="stack-card" style="border:none;padding:0;">
                <h4>// Capture & Provenance (Layer 0)</h4>
                <div class="stack-row"><span class="k">Protocol</span><span class="v">C2PA (Content Credentials)</span></div>
                <div class="stack-row"><span class="k">Hardware</span><span class="v">Sony IMX989 + HSM Chipset</span></div>
                <div class="stack-row"><span class="k">Anti-Restream</span><span class="v">3D ToF Depth Sensor</span></div>
                <div class="stack-row"><span class="k">Hash Chain</span><span class="v">SHA-256 per GOP</span></div>
              </div>
              <div class="stack-card" style="border:none;padding:16px 0 0 0;border-top:1px solid var(--border);margin-top:16px;">
                <h4>// Watermark Embedding (Layer 1)</h4>
                <div class="stack-row"><span class="k">Algorithm</span><span class="v">Adversarial-Only DCT Encoder</span></div>
                <div class="stack-row"><span class="k">Payload</span><span class="v">64-bit subscriber fingerprint</span></div>
                <div class="stack-row"><span class="k">Attenuation</span><span class="v">JND-aware (Just Noticeable Difference)</span></div>
                <div class="stack-row"><span class="k">Resolution</span><span class="v">4K / 60fps temporal pooling</span></div>
              </div>
              <div class="stack-card" style="border:none;padding:16px 0 0 0;border-top:1px solid var(--border);margin-top:16px;">
                <h4>// Detection Engine (Layer 3)</h4>
                <div class="stack-row"><span class="k">Crawl Cadence</span><span class="v">30s interval, P2P fleet</span></div>
                <div class="stack-row"><span class="k">Copy Detection</span><span class="v">MMD-Agent (Multimodal)</span></div>
                <div class="stack-row"><span class="k">Fast Path</span><span class="v">C2PA metadata check</span></div>
                <div class="stack-row"><span class="k">Confidence</span><span class="v">> 0.80 → auto-enforce</span></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `;

  pipelineViz = new PipelineViz(document.getElementById('pipeline-main'));
  pipelineFeed = new EventFeed(document.getElementById('pipeline-events'));
}

export function handlePipelineEvent(msg) {
  pipelineFeed?.addEvent(msg);
  const topic = msg.topic;
  if (topic === 'stream.active') pipelineViz?.highlightStage('distribute', 'active');
  else if (topic === 'piracy.detected') pipelineViz?.highlightStage('detect', 'alert');
  else if (topic === 'enforcement.executed') pipelineViz?.highlightStage('enforce', 'active');
}

export function updatePipelineStats(stats) {
  pipelineViz?.update(stats.stage_counts || {}, stats.throughput_per_min || {});
}

export function destroyPipeline() {
  pipelineViz = null;
  pipelineFeed = null;
}
