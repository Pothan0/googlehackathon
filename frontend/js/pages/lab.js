/**
 * Sports Media Sentinel — Testing Lab Page (Enhanced)
 * Full testing suite: Pipeline, Watermark, Extract, Detect, Register,
 * Robustness Test, URL Crawler, Audit Trail, DMCA Generator
 */
export function renderLab(container) {
  container.innerHTML = `
    <div class="page-content">
      <div class="section" style="padding-top:24px">
        <div class="section-header">
          <span class="section-num">LAB</span>
          <h2 class="section-title">Testing Lab</h2>
        </div>
        <p style="color:var(--muted);margin-bottom:32px;max-width:720px;">
          Upload your own images to test the SMS pipeline end-to-end. All operations use real cryptographic
          signing, DCT watermarking, SSIM detection, and tamper-proof audit logging.
        </p>
      </div>

      <!-- Tab Navigation -->
      <div class="section" style="padding-top:0;">
        <div style="display:flex;gap:2px;margin-bottom:24px;flex-wrap:wrap;">
          <button class="lab-tab active" data-tab="full-pipeline" onclick="window._labSwitchTab('full-pipeline')">▶ Pipeline</button>
          <button class="lab-tab" data-tab="watermark" onclick="window._labSwitchTab('watermark')">🔏 Watermark</button>
          <button class="lab-tab" data-tab="extract" onclick="window._labSwitchTab('extract')">🔍 Extract</button>
          <button class="lab-tab" data-tab="detect" onclick="window._labSwitchTab('detect')">🧠 Detect</button>
          <button class="lab-tab" data-tab="register" onclick="window._labSwitchTab('register')">📡 Register</button>
          <button class="lab-tab" data-tab="robustness" onclick="window._labSwitchTab('robustness')">🛡 Robustness</button>
          <button class="lab-tab" data-tab="crawler" onclick="window._labSwitchTab('crawler')">🌐 Crawler</button>
          <button class="lab-tab" data-tab="audit" onclick="window._labSwitchTab('audit')">🔗 Audit</button>
          <button class="lab-tab" data-tab="dmca" onclick="window._labSwitchTab('dmca')">⚖ DMCA</button>
        </div>

        <!-- Full Pipeline Tab -->
        <div class="lab-panel" id="tab-full-pipeline">
          <div class="dash-grid">
            <div class="dash-panel">
              <div class="panel-header"><div class="panel-title">// Full 7-Step Pipeline Test</div></div>
              <p style="font-size:12px;color:var(--muted);margin-bottom:16px;">
                Upload an image to run it through all 7 stages: Capture → Ingest → Watermark → Distribute → Crawl → Detect → Enforce
              </p>
              <form id="form-pipeline" class="lab-form">
                <div class="lab-field"><label>Image File</label><input type="file" name="file" accept="image/*" required class="lab-input-file"></div>
                <div class="lab-field"><label>Asset Name</label><input type="text" name="asset_name" value="My Sports Broadcast" class="lab-input"></div>
                <div class="lab-field"><label>Subscriber ID</label><input type="text" name="subscriber_id" value="SUB-TEST-001" class="lab-input"></div>
                <button type="submit" class="lab-btn">▶ Run Full Pipeline</button>
              </form>
              <div id="pipeline-preview" class="lab-preview" style="display:none;">
                <div class="panel-title" style="margin-bottom:8px;">// Original vs Watermarked</div>
                <div style="display:flex;gap:8px;">
                  <div style="flex:1;text-align:center;">
                    <div style="font-size:9px;color:var(--muted);margin-bottom:4px;font-family:'IBM Plex Mono',monospace;">ORIGINAL</div>
                    <img id="pipeline-img-orig" style="max-width:100%;border:1px solid var(--border);border-radius:4px;">
                  </div>
                  <div style="flex:1;text-align:center;">
                    <div style="font-size:9px;color:var(--muted);margin-bottom:4px;font-family:'IBM Plex Mono',monospace;">WATERMARKED</div>
                    <img id="pipeline-img-wm" style="max-width:100%;border:1px solid var(--border);border-radius:4px;">
                  </div>
                </div>
              </div>
            </div>
            <div class="dash-panel">
              <div class="panel-header"><div class="panel-title">// Pipeline Results</div></div>
              <div id="pipeline-results" class="lab-results">
                <div style="color:var(--muted);font-size:12px;padding:40px 0;text-align:center;">Upload an image and run the pipeline to see results here</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Watermark Tab -->
        <div class="lab-panel" id="tab-watermark" style="display:none;">
          <div class="dash-grid">
            <div class="dash-panel">
              <div class="panel-header"><div class="panel-title">// Embed Forensic Watermark</div></div>
              <p style="font-size:12px;color:var(--muted);margin-bottom:16px;">
                Multi-scale DCT watermark with spread-spectrum encoding and error correction. Survives JPEG compression, resizing, and cropping.
              </p>
              <form id="form-watermark" class="lab-form">
                <div class="lab-field"><label>Image File</label><input type="file" name="file" accept="image/*" required class="lab-input-file"></div>
                <div class="lab-field"><label>Subscriber ID</label><input type="text" name="subscriber_id" value="SUB-TEST-001" class="lab-input"></div>
                <button type="submit" class="lab-btn">🔏 Embed Watermark</button>
              </form>
            </div>
            <div class="dash-panel">
              <div class="panel-header"><div class="panel-title">// Watermark Result</div></div>
              <div id="watermark-results" class="lab-results">
                <div style="color:var(--muted);font-size:12px;padding:40px 0;text-align:center;">Upload an image to embed a watermark</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Extract Tab -->
        <div class="lab-panel" id="tab-extract" style="display:none;">
          <div class="dash-grid">
            <div class="dash-panel">
              <div class="panel-header"><div class="panel-title">// Extract Watermark (Forensic Tracing)</div></div>
              <p style="font-size:12px;color:var(--muted);margin-bottom:16px;">
                Upload a suspected pirated image. The system reads DCT coefficients, applies majority-vote decoding, and traces the content back to the source subscriber.
              </p>
              <form id="form-extract" class="lab-form">
                <div class="lab-field"><label>Suspected Pirated Image</label><input type="file" name="file" accept="image/*" required class="lab-input-file"></div>
                <button type="submit" class="lab-btn">🔍 Extract Watermark</button>
              </form>
            </div>
            <div class="dash-panel">
              <div class="panel-header"><div class="panel-title">// Extraction Result</div></div>
              <div id="extract-results" class="lab-results">
                <div style="color:var(--muted);font-size:12px;padding:40px 0;text-align:center;">Upload a watermarked image to extract the payload</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Detect Tab -->
        <div class="lab-panel" id="tab-detect" style="display:none;">
          <div class="dash-grid">
            <div class="dash-panel">
              <div class="panel-header"><div class="panel-title">// Multi-Method Piracy Detection</div></div>
              <p style="font-size:12px;color:var(--muted);margin-bottom:16px;">
                4-layer detection: perceptual hashing (pHash/dHash/wHash) + SSIM structural similarity + color histogram + multi-hash consensus scoring.
              </p>
              <form id="form-detect" class="lab-form">
                <div class="lab-field"><label>Suspect Image</label><input type="file" name="file" accept="image/*" required class="lab-input-file"></div>
                <button type="submit" class="lab-btn">🧠 Run Detection</button>
              </form>
            </div>
            <div class="dash-panel">
              <div class="panel-header"><div class="panel-title">// Detection Result</div></div>
              <div id="detect-results" class="lab-results">
                <div style="color:var(--muted);font-size:12px;padding:40px 0;text-align:center;">Upload an image to run piracy detection</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Register Tab -->
        <div class="lab-panel" id="tab-register" style="display:none;">
          <div class="dash-grid">
            <div class="dash-panel">
              <div class="panel-header"><div class="panel-title">// Register Protected Asset</div></div>
              <p style="font-size:12px;color:var(--muted);margin-bottom:16px;">
                Registers with X.509-signed C2PA provenance, computes multi-hash fingerprints, and mints a Story Protocol IP token. Certificate chain is cryptographically verifiable.
              </p>
              <form id="form-register" class="lab-form">
                <div class="lab-field"><label>Image File</label><input type="file" name="file" accept="image/*" required class="lab-input-file"></div>
                <div class="lab-field"><label>Asset Name</label><input type="text" name="name" value="My Protected Content" class="lab-input"></div>
                <button type="submit" class="lab-btn">📡 Register Asset</button>
              </form>
            </div>
            <div class="dash-panel">
              <div class="panel-header"><div class="panel-title">// Registration Result</div></div>
              <div id="register-results" class="lab-results">
                <div style="color:var(--muted);font-size:12px;padding:40px 0;text-align:center;">Upload an image to register it as a protected asset</div>
              </div>
            </div>
          </div>
        </div>

        <!-- NEW: Robustness Test Tab -->
        <div class="lab-panel" id="tab-robustness" style="display:none;">
          <div class="dash-grid">
            <div class="dash-panel">
              <div class="panel-header"><div class="panel-title">// Watermark Robustness Test</div></div>
              <p style="font-size:12px;color:var(--muted);margin-bottom:16px;">
                Tests watermark survival against 6 attack vectors: direct extraction, JPEG Q85, JPEG Q50, 50% resize, 75% resize, and 10% crop. Shows amplified difference image.
              </p>
              <form id="form-robustness" class="lab-form">
                <div class="lab-field"><label>Image File</label><input type="file" name="file" accept="image/*" required class="lab-input-file"></div>
                <div class="lab-field"><label>Subscriber ID</label><input type="text" name="subscriber_id" value="SUB-ROBUST-001" class="lab-input"></div>
                <button type="submit" class="lab-btn">🛡 Run Robustness Test</button>
              </form>
            </div>
            <div class="dash-panel">
              <div class="panel-header"><div class="panel-title">// Robustness Results</div></div>
              <div id="robustness-results" class="lab-results">
                <div style="color:var(--muted);font-size:12px;padding:40px 0;text-align:center;">Upload an image to test watermark robustness against attacks</div>
              </div>
            </div>
          </div>
        </div>

        <!-- NEW: URL Crawler Tab -->
        <div class="lab-panel" id="tab-crawler" style="display:none;">
          <div class="dash-grid">
            <div class="dash-panel">
              <div class="panel-header"><div class="panel-title">// Web Content Crawler</div></div>
              <p style="font-size:12px;color:var(--muted);margin-bottom:16px;">
                Enter a URL to scan. The crawler downloads the page, extracts all media (images, video posters), and runs each through the detection engine for fingerprint + watermark matching.
              </p>
              <form id="form-crawler" class="lab-form">
                <div class="lab-field"><label>URL to Scan</label><input type="text" name="url" value="https://example.com" class="lab-input" placeholder="https://..."></div>
                <button type="submit" class="lab-btn">🌐 Crawl URL</button>
              </form>
            </div>
            <div class="dash-panel">
              <div class="panel-header"><div class="panel-title">// Crawl Results</div></div>
              <div id="crawler-results" class="lab-results">
                <div style="color:var(--muted);font-size:12px;padding:40px 0;text-align:center;">Enter a URL to scan for pirated content</div>
              </div>
            </div>
          </div>
        </div>

        <!-- NEW: Audit Trail Tab -->
        <div class="lab-panel" id="tab-audit" style="display:none;">
          <div class="dash-grid" style="grid-template-columns:1fr;">
            <div class="dash-panel">
              <div class="panel-header"><div class="panel-title">// Tamper-Proof Audit Trail (SHA-256 Hash Chain)</div></div>
              <p style="font-size:12px;color:var(--muted);margin-bottom:16px;">
                Every action creates an immutable audit entry. Each entry contains the SHA-256 hash of the previous entry, forming a chain. Any tampering breaks the chain.
              </p>
              <div style="display:flex;gap:8px;margin-bottom:16px;">
                <button class="lab-btn" onclick="window._loadAudit()" style="font-size:11px;">🔗 Load Audit Trail</button>
                <button class="lab-btn" onclick="window._verifyChain()" style="font-size:11px;background:var(--accent3);">✓ Verify Chain Integrity</button>
                <button class="lab-btn" onclick="window._exportAudit()" style="font-size:11px;background:var(--surface2);border:1px solid var(--border);">⬇ Export Chain</button>
              </div>
              <div id="audit-results" class="lab-results">
                <div style="color:var(--muted);font-size:12px;padding:40px 0;text-align:center;">Click "Load Audit Trail" to see all logged actions</div>
              </div>
            </div>
          </div>
        </div>

        <!-- NEW: DMCA Generator Tab -->
        <div class="lab-panel" id="tab-dmca" style="display:none;">
          <div class="dash-grid">
            <div class="dash-panel">
              <div class="panel-header"><div class="panel-title">// DMCA Notice Generator</div></div>
              <p style="font-size:12px;color:var(--muted);margin-bottom:16px;">
                Generate a legally-formatted DMCA takedown notice (17 U.S.C. § 512(c)) with forensic evidence references, blockchain TX hash, and watermark proof.
              </p>
              <form id="form-dmca" class="lab-form">
                <div class="lab-field"><label>Platform</label><input type="text" name="platform" value="YouTube" class="lab-input"></div>
                <div class="lab-field"><label>Infringing URL</label><input type="text" name="source_url" value="https://youtube.com/watch?v=pirated123" class="lab-input"></div>
                <div class="lab-field"><label>Content Name</label><input type="text" name="event_name" value="IPL 2026 DC vs RCB" class="lab-input"></div>
                <div class="lab-field"><label>Subscriber (leaker)</label><input type="text" name="subscriber_id" value="JIOHOTSTAR-USR-48291" class="lab-input"></div>
                <button type="submit" class="lab-btn">⚖ Generate DMCA Notice</button>
              </form>
            </div>
            <div class="dash-panel">
              <div class="panel-header"><div class="panel-title">// Generated DMCA Notice</div></div>
              <div id="dmca-results" class="lab-results">
                <div style="color:var(--muted);font-size:12px;padding:40px 0;text-align:center;">Fill in details to generate a DMCA takedown notice</div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  `;

  // Tab switching
  window._labSwitchTab = (tab) => {
    document.querySelectorAll('.lab-panel').forEach(p => p.style.display = 'none');
    document.querySelectorAll('.lab-tab').forEach(t => t.classList.remove('active'));
    document.getElementById('tab-' + tab).style.display = 'block';
    document.querySelector(`.lab-tab[data-tab="${tab}"]`).classList.add('active');
  };

  // Form handlers
  _bindForm('form-pipeline', '/api/lab/full-pipeline', (data) => {
    const preview = document.getElementById('pipeline-preview');
    const origImg = document.getElementById('pipeline-img-orig');
    const wmImg = document.getElementById('pipeline-img-wm');
    if (data.watermarked_image_base64) {
      wmImg.src = 'data:image/png;base64,' + data.watermarked_image_base64;
      preview.style.display = 'block';
    }
    const fileInput = document.querySelector('#form-pipeline input[type=file]');
    if (fileInput.files[0]) origImg.src = URL.createObjectURL(fileInput.files[0]);
    _renderPipelineResults(document.getElementById('pipeline-results'), data.pipeline_results);
  });

  _bindForm('form-watermark', '/api/lab/watermark', (data) => {
    _renderJSON(document.getElementById('watermark-results'), data, 'watermark');
  });

  _bindForm('form-extract', '/api/lab/extract', (data) => {
    _renderJSON(document.getElementById('extract-results'), data, 'extract');
  });

  _bindForm('form-detect', '/api/lab/detect', (data) => {
    _renderJSON(document.getElementById('detect-results'), data, 'detect');
  });

  _bindForm('form-register', '/api/lab/register', (data) => {
    _renderJSON(document.getElementById('register-results'), data, 'register');
  });

  // NEW: Robustness test
  _bindForm('form-robustness', '/api/lab/robustness-test', (data) => {
    _renderRobustnessResults(document.getElementById('robustness-results'), data);
  });

  // NEW: Crawler
  _bindForm('form-crawler', '/api/lab/crawl', (data) => {
    _renderCrawlResults(document.getElementById('crawler-results'), data);
  });

  // NEW: DMCA
  _bindForm('form-dmca', '/api/lab/dmca', (data) => {
    _renderDMCA(document.getElementById('dmca-results'), data);
  });

  // NEW: Audit trail functions
  window._loadAudit = async () => {
    const res = await fetch('/api/audit');
    const data = await res.json();
    _renderAudit(document.getElementById('audit-results'), data);
  };

  window._verifyChain = async () => {
    const res = await fetch('/api/audit/verify');
    const data = await res.json();
    const el = document.getElementById('audit-results');
    const color = data.valid ? 'var(--accent3)' : 'var(--accent2)';
    const icon = data.valid ? '✅' : '❌';
    el.innerHTML = `
      <div style="text-align:center;padding:32px;">
        <div style="font-size:48px;margin-bottom:16px;">${icon}</div>
        <div style="font-size:18px;font-weight:700;color:${color};margin-bottom:8px;">${data.valid ? 'CHAIN INTACT' : 'CHAIN BROKEN'}</div>
        <div style="font-size:12px;color:var(--muted);">${data.details}</div>
        <div style="font-size:11px;color:var(--muted);margin-top:8px;">Entries checked: ${data.entries_checked}</div>
      </div>`;
  };

  window._exportAudit = async () => {
    const res = await fetch('/api/audit/export');
    const data = await res.json();
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'sms_audit_chain.json';
    a.click();
  };
}

function _bindForm(formId, endpoint, onResult) {
  setTimeout(() => {
    const form = document.getElementById(formId);
    if (!form) return;
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const btn = form.querySelector('button[type=submit]');
      const origText = btn.textContent;
      btn.textContent = '⏳ Processing...';
      btn.disabled = true;

      try {
        const fd = new FormData(form);
        const res = await fetch(endpoint, { method: 'POST', body: fd });
        const data = await res.json();
        onResult(data);
      } catch (err) {
        alert('Error: ' + err.message);
      } finally {
        btn.textContent = origText;
        btn.disabled = false;
      }
    });
  }, 100);
}

function _renderPipelineResults(container, results) {
  if (!results) { container.innerHTML = '<div style="color:var(--accent2);">Error processing pipeline</div>'; return; }

  const stageLabels = {
    step_1_capture: { num: '01', name: 'Capture (C2PA Signed)', icon: '📡', color: 'var(--accent)' },
    step_2_ingest: { num: '02', name: 'Ingest (Fingerprinted)', icon: '📥', color: 'var(--accent)' },
    step_3_watermark: { num: '03', name: 'Watermark (DCT-JND)', icon: '🔏', color: 'var(--accent)' },
    step_4_distribute: { num: '04', name: 'Distribute (IP Token)', icon: '📡', color: 'var(--accent)' },
    step_5_crawl: { num: '05', name: 'Crawl', icon: '🌐', color: 'var(--accent2)' },
    step_6_detect: { num: '06', name: 'Detect (SSIM+Hash)', icon: '🧠', color: 'var(--accent2)' },
    step_7_enforce: { num: '07', name: 'Enforce (Automated)', icon: '⚖️', color: 'var(--accent3)' },
  };

  let html = '<div style="display:flex;flex-direction:column;gap:8px;max-height:500px;overflow-y:auto;">';
  for (const [key, meta] of Object.entries(stageLabels)) {
    const data = results[key] || {};
    const entries = Object.entries(data).map(([k, v]) =>
      `<div class="stack-row"><span class="k">${k.replace(/_/g, ' ')}</span><span class="v">${typeof v === 'boolean' ? (v ? '✅ Yes' : '❌ No') : v}</span></div>`
    ).join('');
    html += `
      <div style="background:var(--surface2);border:1px solid var(--border);padding:12px 16px;border-left:3px solid ${meta.color};">
        <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:var(--muted);letter-spacing:.15em;margin-bottom:4px;">STEP ${meta.num}</div>
        <div style="font-size:13px;font-weight:600;color:var(--white);margin-bottom:8px;">${meta.icon} ${meta.name}</div>
        ${entries}
      </div>`;
  }
  html += '</div>';
  container.innerHTML = html;
}

function _renderRobustnessResults(container, data) {
  const scoreColor = data.robustness_score >= 80 ? 'var(--accent3)' : data.robustness_score >= 50 ? 'var(--accent)' : 'var(--accent2)';
  let html = `
    <div style="text-align:center;margin-bottom:16px;">
      <div style="font-size:32px;font-weight:700;color:${scoreColor};font-family:'Bebas Neue',sans-serif;">${data.robustness_score}%</div>
      <div style="font-size:10px;color:var(--muted);letter-spacing:.1em;">ROBUSTNESS SCORE (${data.tests_passed}/${data.tests_total} PASSED)</div>
    </div>`;

  // Show diff image
  if (data.diff_image_base64) {
    html += `<div style="margin-bottom:12px;text-align:center;">
      <div style="font-size:9px;color:var(--muted);margin-bottom:4px;font-family:'IBM Plex Mono',monospace;">DIFFERENCE IMAGE (20x AMPLIFIED)</div>
      <img src="data:image/png;base64,${data.diff_image_base64}" style="max-width:100%;max-height:150px;border:1px solid var(--border);border-radius:4px;">
    </div>`;
  }

  // Show individual test results
  html += '<div style="display:flex;flex-direction:column;gap:4px;">';
  for (const [test, result] of Object.entries(data.results || {})) {
    const pass = result.success;
    const icon = pass ? '✅' : '❌';
    const label = test.replace(/_/g, ' ').replace(/pct/, '%');
    html += `<div class="stack-row">
      <span class="k">${icon} ${label}</span>
      <span class="v" style="color:${pass ? 'var(--accent3)' : 'var(--accent2)'};">${pass ? `${result.subscriber} (${(result.confidence * 100).toFixed(0)}%)` : 'FAILED'}</span>
    </div>`;
  }
  html += '</div>';
  container.innerHTML = html;
}

function _renderCrawlResults(container, data) {
  let html = `
    <div style="margin-bottom:12px;">
      <div class="stack-row"><span class="k">URL</span><span class="v" style="word-break:break-all;">${data.url}</span></div>
      <div class="stack-row"><span class="k">Media Found</span><span class="v">${data.media_found}</span></div>
      <div class="stack-row"><span class="k">Media Analyzed</span><span class="v">${data.media_analyzed}</span></div>
      <div class="stack-row"><span class="k">Matches</span><span class="v" style="color:${data.matches_found > 0 ? 'var(--accent2)' : 'var(--accent3)'};">${data.matches_found}</span></div>
      <div class="stack-row"><span class="k">Duration</span><span class="v">${data.duration_seconds}s</span></div>
    </div>`;

  if (data.matches && data.matches.length > 0) {
    html += '<div class="panel-title" style="margin:12px 0 8px;">// Matches Found</div>';
    for (const m of data.matches) {
      html += `<div style="background:rgba(255,50,50,0.1);border:1px solid var(--accent2);padding:8px;margin-bottom:8px;font-size:11px;">
        <div class="stack-row"><span class="k">URL</span><span class="v" style="word-break:break-all;">${m.url}</span></div>
        <div class="stack-row"><span class="k">Size</span><span class="v">${m.image_size}</span></div>
        ${m.fingerprint_match ? '<div class="stack-row"><span class="k">Fingerprint</span><span class="v" style="color:var(--accent2);">MATCHED</span></div>' : ''}
        ${m.watermark_extraction ? `<div class="stack-row"><span class="k">Watermark</span><span class="v" style="color:var(--accent2);">Subscriber: ${m.watermark_extraction.subscriber_id}</span></div>` : ''}
      </div>`;
    }
  }

  if (data.errors && data.errors.length > 0) {
    html += `<div style="font-size:10px;color:var(--muted);margin-top:8px;">${data.errors.length} error(s) during crawl</div>`;
  }

  container.innerHTML = html;
}

function _renderAudit(container, data) {
  const s = data.summary || {};
  const v = data.chain_verification || {};
  const chainColor = v.valid ? 'var(--accent3)' : 'var(--accent2)';

  let html = `
    <div style="display:flex;gap:16px;margin-bottom:16px;flex-wrap:wrap;">
      <div style="background:var(--surface2);padding:12px 16px;border:1px solid var(--border);flex:1;min-width:120px;">
        <div style="font-size:9px;color:var(--muted);letter-spacing:.1em;margin-bottom:4px;">TOTAL ENTRIES</div>
        <div style="font-size:24px;font-weight:700;color:var(--accent);font-family:'Bebas Neue',sans-serif;">${s.total_entries || 0}</div>
      </div>
      <div style="background:var(--surface2);padding:12px 16px;border:1px solid ${chainColor};flex:1;min-width:120px;">
        <div style="font-size:9px;color:var(--muted);letter-spacing:.1em;margin-bottom:4px;">CHAIN INTEGRITY</div>
        <div style="font-size:24px;font-weight:700;color:${chainColor};font-family:'Bebas Neue',sans-serif;">${v.valid ? '✅ VALID' : '❌ BROKEN'}</div>
      </div>
      <div style="background:var(--surface2);padding:12px 16px;border:1px solid var(--border);flex:1;min-width:120px;">
        <div style="font-size:9px;color:var(--muted);letter-spacing:.1em;margin-bottom:4px;">LATEST HASH</div>
        <div style="font-size:11px;font-weight:600;color:var(--white);font-family:'IBM Plex Mono',monospace;word-break:break-all;">${s.latest_hash || 'N/A'}</div>
      </div>
    </div>`;

  // Event type counts
  if (s.event_counts) {
    html += '<div style="display:flex;gap:8px;margin-bottom:16px;flex-wrap:wrap;">';
    for (const [type, count] of Object.entries(s.event_counts)) {
      html += `<div style="background:var(--surface2);padding:6px 12px;border:1px solid var(--border);font-size:10px;">
        <span style="color:var(--accent);">${type}</span>: <span style="color:var(--white);font-weight:600;">${count}</span>
      </div>`;
    }
    html += '</div>';
  }

  // Entries
  const entries = data.entries || [];
  if (entries.length > 0) {
    html += '<div style="max-height:400px;overflow-y:auto;">';
    for (const e of entries) {
      const typeColors = { registration: 'var(--accent)', watermark: '#a855f7', detection: 'var(--accent2)', enforcement: '#ef4444', pipeline: 'var(--accent3)', license: '#f59e0b', crawl: '#06b6d4' };
      const col = typeColors[e.event_type] || 'var(--muted)';
      html += `<div style="background:var(--surface2);border:1px solid var(--border);border-left:3px solid ${col};padding:8px 12px;margin-bottom:4px;font-size:11px;">
        <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
          <span style="color:${col};font-weight:600;text-transform:uppercase;font-size:9px;letter-spacing:.1em;">${e.event_type}</span>
          <span style="color:var(--muted);font-size:9px;">#${e.sequence} | ${e.timestamp_iso}</span>
        </div>
        <div class="stack-row"><span class="k">${e.entity_type} / ${e.action}</span><span class="v">${e.entity_id?.substring(0, 20) || ''}</span></div>
        <div style="font-size:9px;color:var(--muted);margin-top:4px;font-family:'IBM Plex Mono',monospace;">hash: ${e.entry_hash?.substring(0, 32)}... → prev: ${e.prev_hash?.substring(0, 16)}...</div>
      </div>`;
    }
    html += '</div>';
  }

  container.innerHTML = html;
}

function _renderDMCA(container, data) {
  let html = `
    <div style="margin-bottom:12px;">
      <div class="stack-row"><span class="k">Notice ID</span><span class="v" style="color:var(--accent);">${data.notice_id}</span></div>
      <div class="stack-row"><span class="k">Platform</span><span class="v">${data.platform}</span></div>
      <div class="stack-row"><span class="k">Legal Basis</span><span class="v">${data.legal_basis}</span></div>
      <div class="stack-row"><span class="k">Generated</span><span class="v">${data.generated_at}</span></div>
    </div>
    <div style="background:var(--surface2);border:1px solid var(--border);padding:16px;font-family:'IBM Plex Mono',monospace;font-size:10px;line-height:1.6;color:var(--white);white-space:pre-wrap;max-height:400px;overflow-y:auto;">${data.notice_text}</div>
    <button onclick="navigator.clipboard.writeText(document.querySelector('#dmca-results pre,#dmca-results [style*=pre-wrap]').textContent)" class="lab-btn" style="margin-top:12px;font-size:11px;">📋 Copy to Clipboard</button>`;
  container.innerHTML = html;
}

function _renderJSON(container, data, type) {
  const statusColors = {
    watermarked: 'var(--accent3)', watermark_found: 'var(--accent3)',
    no_watermark: 'var(--accent2)', detection_complete: 'var(--accent)', registered: 'var(--accent3)',
  };
  const color = statusColors[data.status] || 'var(--muted)';
  let html = `<div style="margin-bottom:12px;font-family:'IBM Plex Mono',monospace;font-size:11px;color:${color};text-transform:uppercase;letter-spacing:.1em;">${data.status?.replace(/_/g, ' ') || 'Result'}</div>`;

  if (type === 'watermark' && data.image_base64) {
    html += `<div style="margin-bottom:12px;"><img src="data:image/png;base64,${data.image_base64}" style="max-width:100%;max-height:200px;border:1px solid var(--border);border-radius:4px;"></div>`;
    html += `<div style="margin-bottom:8px;"><a href="${data.download_url}" download style="font-size:11px;color:var(--accent);">⬇ Download Watermarked Image</a></div>`;
  }

  html += '<div style="display:flex;flex-direction:column;gap:2px;">';
  for (const [k, v] of Object.entries(data)) {
    if (k === 'image_base64' || k === 'watermarked_image_base64') continue;
    let display = v;
    if (typeof v === 'object' && v !== null) {
      display = '<div style="padding-left:16px;margin-top:4px;">' +
        Object.entries(v).map(([sk, sv]) =>
          `<div class="stack-row"><span class="k">${sk.replace(/_/g, ' ')}</span><span class="v">${typeof sv === 'boolean' ? (sv ? '✅' : '❌') : (sv ?? '—')}</span></div>`
        ).join('') + '</div>';
    } else if (typeof v === 'boolean') {
      display = v ? '✅ Yes' : '❌ No';
    }
    html += `<div class="stack-row"><span class="k">${k.replace(/_/g, ' ')}</span><span class="v">${display}</span></div>`;
  }
  html += '</div>';
  container.innerHTML = html;
}

export function destroyLab() {
  window._labSwitchTab = null;
  window._loadAudit = null;
  window._verifyChain = null;
  window._exportAudit = null;
}
