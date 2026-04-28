/**
 * Sports Media Sentinel — Landing Page
 */
export function renderLanding(container) {
  container.innerHTML = `
    <div class="hero">
      <div class="hero-tag animate-up">Project Architecture — System Design</div>
      <h1 class="animate-up delay-1">Sports<br>Media<br><span>Sentinel</span></h1>
      <p class="hero-desc animate-up delay-2">
        An industry-grade, multi-layer platform for real-time forensic watermarking,
        hardware-anchored content provenance, AI-driven piracy detection, and
        decentralized IP enforcement across global sports media distribution.
      </p>
      <div class="hero-meta animate-up delay-3">
        <div class="meta-cell">
          <div class="label">Codename</div>
          <div class="value">SMS v1.0</div>
        </div>
        <div class="meta-cell">
          <div class="label">Architecture</div>
          <div class="value">Event-Driven Microservices</div>
        </div>
        <div class="meta-cell">
          <div class="label">Target Latency</div>
          <div class="value" id="landing-latency">&lt; 90s Takedown</div>
        </div>
        <div class="meta-cell">
          <div class="label">Scale Target</div>
          <div class="value">10M+ Concurrent Streams</div>
        </div>
      </div>
    </div>

    <div class="page-content">
      <!-- Overview -->
      <div class="section">
        <div class="section-header">
          <span class="section-num">01</span>
          <h2 class="section-title">Project Overview</h2>
        </div>
        <div class="overview-grid">
          <div class="ov-card" data-num="1">
            <div class="ov-title">Problem Domain</div>
            <h3>Content Leakage at Scale</h3>
            <p>Sports broadcasts are stolen and redistributed within seconds of airing. Legacy DRM and basic watermarking are bypassed by AI-powered piracy pipelines and IPTV networks operating across jurisdictions.</p>
          </div>
          <div class="ov-card" data-num="2">
            <div class="ov-title">Solution Core</div>
            <h3>Proactive Authentication Stack</h3>
            <p>A three-layer system combining in-camera C2PA provenance, forensic watermark embedding at CDN edge, and an AI multimodal detection agent backed by blockchain-enforced IP contracts.</p>
          </div>
          <div class="ov-card" data-num="3">
            <div class="ov-title">Business Impact</div>
            <h3>Programmable IP Economy</h3>
            <p>Automated enforcement via smart contracts enables near-instant stream shutdown, revenue redirection from derivatives, and a transparent audit trail for legal and insurance use.</p>
          </div>
        </div>
      </div>

      <!-- Live Stats -->
      <div class="section">
        <div class="section-header">
          <span class="section-num">02</span>
          <h2 class="section-title">Live System Status</h2>
        </div>
        <div class="kpi-row" id="landing-kpis">
          <div class="kpi-card info">
            <div class="kpi-label">Streams Monitored</div>
            <div class="kpi-value accent" id="ls-streams">—</div>
            <div class="kpi-sub">Real-time count</div>
          </div>
          <div class="kpi-card danger">
            <div class="kpi-label">Threats Detected</div>
            <div class="kpi-value danger" id="ls-threats">—</div>
            <div class="kpi-sub">Since startup</div>
          </div>
          <div class="kpi-card success">
            <div class="kpi-label">Enforcements</div>
            <div class="kpi-value success" id="ls-enforcements">—</div>
            <div class="kpi-sub">Auto-triggered</div>
          </div>
          <div class="kpi-card info">
            <div class="kpi-label">Avg Takedown</div>
            <div class="kpi-value accent" id="ls-latency">—</div>
            <div class="kpi-sub">Seconds</div>
          </div>
          <div class="kpi-card success">
            <div class="kpi-label">SLA Compliance</div>
            <div class="kpi-value success" id="ls-sla">—</div>
            <div class="kpi-sub">Target: 99.99%</div>
          </div>
        </div>
      </div>

      <!-- Technology Stack (abridged) -->
      <div class="section">
        <div class="section-header">
          <span class="section-num">03</span>
          <h2 class="section-title">Technology Stack</h2>
        </div>
        <div class="stack-grid">
          <div class="stack-card">
            <h4>// Backend Services</h4>
            <div class="stack-row"><span class="k">Language</span><span class="v">Go (services), Python (ML pipelines)</span></div>
            <div class="stack-row"><span class="k">Frameworks</span><span class="v">gRPC, FastAPI, Gin</span></div>
            <div class="stack-row"><span class="k">Message Bus</span><span class="v">Apache Kafka (multi-region)</span></div>
            <div class="stack-row"><span class="k">Stream Proc.</span><span class="v">Apache Storm / Flink</span></div>
            <div class="stack-row"><span class="k">API Gateway</span><span class="v">Kong / AWS API Gateway</span></div>
            <div class="stack-row"><span class="k">Auth</span><span class="v">OAuth 2.0 + JWT, mTLS (internal)</span></div>
          </div>
          <div class="stack-card">
            <h4>// ML / AI Subsystem</h4>
            <div class="stack-row"><span class="k">Watermark Model</span><span class="v">Adversarial-Only Encoder (PyTorch) <span class="badge">Custom</span></span></div>
            <div class="stack-row"><span class="k">Vision Encoder</span><span class="v">FastVLM (edge inference)</span></div>
            <div class="stack-row"><span class="k">Copy Detection</span><span class="v">MMD-Agent (LVLM + Tool-Use)</span></div>
            <div class="stack-row"><span class="k">Training Infra</span><span class="v">Ray + A100 GPU Cluster</span></div>
            <div class="stack-row"><span class="k">Model Registry</span><span class="v">MLflow + S3 artifact store</span></div>
            <div class="stack-row"><span class="k">Feature Store</span><span class="v">Feast + Redis Online Store</span></div>
          </div>
          <div class="stack-card">
            <h4>// Blockchain / IP Layer</h4>
            <div class="stack-row"><span class="k">Protocol</span><span class="v">Story Protocol <span class="badge green">On-Chain</span></span></div>
            <div class="stack-row"><span class="k">Smart Contracts</span><span class="v">Solidity / EVM-compatible</span></div>
            <div class="stack-row"><span class="k">IP Asset Token</span><span class="v">ERC-1155 (IP Lego structure)</span></div>
            <div class="stack-row"><span class="k">Oracle</span><span class="v">Chainlink (off-chain enforcement bridge)</span></div>
            <div class="stack-row"><span class="k">Wallet Infra</span><span class="v">Gnosis Safe (multisig for rights holders)</span></div>
            <div class="stack-row"><span class="k">Indexer</span><span class="v">The Graph (event subscriptions)</span></div>
          </div>
          <div class="stack-card">
            <h4>// Infrastructure & DevOps</h4>
            <div class="stack-row"><span class="k">Orchestration</span><span class="v">Kubernetes (EKS multi-region)</span></div>
            <div class="stack-row"><span class="k">Service Mesh</span><span class="v">Istio (mTLS, traffic shaping)</span></div>
            <div class="stack-row"><span class="k">CDN / Edge</span><span class="v">Cloudfront + Lambda@Edge</span></div>
            <div class="stack-row"><span class="k">IaC</span><span class="v">Terraform + Helmcharts</span></div>
            <div class="stack-row"><span class="k">CI/CD</span><span class="v">GitHub Actions + ArgoCD</span></div>
            <div class="stack-row"><span class="k">Secrets</span><span class="v">HashiCorp Vault</span></div>
          </div>
        </div>
      </div>
    </div>

    <div class="footer">
      <div class="logo">SMS — Sports Media Sentinel</div>
      <div>CONFIDENTIAL · SYSTEM DESIGN DOCUMENT · v1.0</div>
      <div>Architecture · Infrastructure · IP Enforcement</div>
    </div>
  `;
}

export function updateLandingStats(kpis) {
  const set = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
  };
  set('ls-streams', kpis.total_streams?.toLocaleString() || '0');
  set('ls-threats', kpis.total_detections?.toLocaleString() || '0');
  set('ls-enforcements', kpis.total_enforcements?.toLocaleString() || '0');
  set('ls-latency', (kpis.avg_takedown_latency || 0).toFixed(1) + 's');
  set('ls-sla', (kpis.sla_compliance || 100).toFixed(1) + '%');
}
