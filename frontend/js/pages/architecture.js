/**
 * Sports Media Sentinel — System Architecture Page
 * Full architecture doc from the design specification.
 */
export function renderArchitecture(container) {
  container.innerHTML = `
    <div class="page-content">

      <!-- System Architecture -->
      <div class="section" style="padding-top:24px">
        <div class="section-header">
          <span class="section-num">02</span>
          <h2 class="section-title">System Architecture</h2>
        </div>
        <div class="arch-wrap">
          <div class="arch-title">// Layered System Overview — Data flows top to bottom</div>
          <div class="arch-layers">
            ${_layer('LAYER 0','Capture & Provenance','accent',[
              'C2PA In-Camera Hardware Signing','3D Depth Anti-Restream Sensor',
              'Tamper-Proof Server-Sync Timestamp','Master Feed Registry (Immutable Log)'
            ])}
            <div class="arch-arrow">↓</div>
            ${_layer('LAYER 1','Ingest & Watermark','accent',[
              'CDN Edge Watermark Embedder','Session / Subscriber Node Binding',
              'Temporal Watermark Pooling (4K/60fps)','Asset Catalog Service (S3 + ES)'
            ])}
            <div class="arch-arrow">↓</div>
            ${_layer('LAYER 2','Distribution','',[
              'OTT / HLS / DASH CDN Delivery','Social Media API Push (Licensed)',
              'DRM Packaging (Widevine / FairPlay)','Subscriber License Token Issuance'
            ])}
            <div class="arch-arrow">↓</div>
            ${_layer('LAYER 3','Detection Engine','danger',[
              'P2P Distributed Web Crawler','Forensic Watermark Extractor (LVLM)',
              'MMD-Agent Multimodal Copy Detector','IPTV / Social Platform Scanners'
            ])}
            <div class="arch-arrow">↓</div>
            ${_layer('LAYER 4','Enforcement & IP','green',[
              'Smart Contract Enforcement','CDN Session Termination API',
              'Revenue Redirection (On-Chain)','Audit Trail + Legal Evidence Export'
            ])}
            <div class="arch-arrow">↓</div>
            ${_layer('LAYER 5','Observability','',[
              'Real-Time Piracy Dashboard','Distributed Tracing (OpenTelemetry)',
              'Alerting & SLA Monitoring','Incident Audit Ledger (Immutable)'
            ])}
          </div>
        </div>
      </div>

      <!-- Microservice Breakdown -->
      <div class="section">
        <div class="section-header">
          <span class="section-num">05</span>
          <h2 class="section-title">Microservice Breakdown</h2>
        </div>
        <div class="comp-grid">
          ${_comp('📡','Provenance Service','Validates and registers C2PA credentials for every inbound camera feed',[
            'C2PA manifest parsing & signature verification','3D depth anti-restream validation',
            'Master Feed immutable registration','Cryptographic hash chaining per GOP'
          ])}
          ${_comp('🔏','Watermark Service','Embeds and retrieves per-subscriber forensic marks at CDN edge',[
            'Adversarial-only encoder inference (GPU)','Temporal pooling across frame sequences',
            'JND attenuation pipeline for 4K output','Watermark DB write (subscriber → hash)'
          ])}
          ${_comp('🌐','Crawler Orchestrator','Manages distributed P2P crawler fleet assigned to internet subsets',[
            'Hash-partitioned crawler assignment','Social API rate-limit management',
            'IPTV + torrent index polling (30s cadence)','Kafka event emission on match candidates'
          ])}
          ${_comp('🧠','Detection Engine','Multimodal AI pipeline that classifies and traces unauthorized streams',[
            'C2PA metadata presence check (fast path)','Forensic watermark extraction (LVLM)',
            'MMD-Agent cross-modal anomaly scoring','Confidence threshold routing to enforcement'
          ])}
          ${_comp('⚖️','Enforcement Service','Orchestrates smart contract calls and CDN termination upon confirmed piracy',[
            'Blockchain license state lookup','Smart contract trigger (Story Protocol)',
            'CDN session kill via edge API','Platform DMCA / takedown API dispatch'
          ])}
          ${_comp('💰','IP & Rights Service','Manages on-chain IP tokens, licenses, and automated royalty distribution',[
            'IP Lego minting (ERC-1155 + metadata)','License issuance & validity management',
            'On-chain royalty split calculation','Audit trail export (legal / insurance)'
          ])}
          ${_comp('🗄️','Asset Catalog Service','Source of truth for all registered media assets and their metadata',[
            'Asset CRUD with versioning','Fingerprint database (Elasticsearch)',
            'Soft-binding index (watermark + fingerprint)','Historical archive search API'
          ])}
          ${_comp('🔑','Auth & License Gateway','Issues and validates subscriber tokens, DRM licenses, and API keys',[
            'OAuth 2.0 / OIDC subscriber auth','Widevine + FairPlay DRM license server',
            'Session token binding to watermark ID','Rate-limiting + abuse detection'
          ])}
          ${_comp('📊','Observability Service','Aggregates metrics, traces, and incidents for operational and legal use',[
            'Real-time piracy heatmap (Grafana)','SLA compliance monitoring',
            'Distributed trace correlation (Jaeger)','Immutable incident log (Immudb)'
          ])}
        </div>
      </div>

      <!-- NFR -->
      <div class="section">
        <div class="section-header">
          <span class="section-num">06</span>
          <h2 class="section-title">Non-Functional Requirements</h2>
        </div>
        <table class="nfr-table">
          <thead><tr><th>Category</th><th>Requirement</th><th>Target Metric</th><th>Mechanism</th></tr></thead>
          <tbody>
            ${_nfr('Latency','Watermark embed (per stream)','< 50ms per segment','GPU edge inference via FastVLM')}
            ${_nfr('Latency','End-to-end takedown loop','< 90 seconds','Pre-authorized smart contract, CDN API')}
            ${_nfr('Throughput','Concurrent stream monitoring','10M+ streams','Hash-partitioned P2P crawler fleet')}
            ${_nfr('Accuracy','Watermark detection rate','> 99.5% (post-compression)','Adversarial-only training + temporal pooling')}
            ${_nfr('Accuracy','False positive rate','< 0.1%','Multi-stage confidence gating')}
            ${_nfr('Availability','Watermark & enforcement services','99.99% uptime','Multi-region active-active K8s')}
            ${_nfr('Scalability','Horizontal autoscaling','0 → 10K pods in < 5min','KEDA event-driven autoscaler')}
            ${_nfr('Security','Internal service communication','Zero-trust mTLS','Istio service mesh + Vault PKI')}
            ${_nfr('Compliance','GDPR / CCPA subscriber data','Data minimization','Watermark ID abstraction layer')}
            ${_nfr('Resilience','Single-region failure','RTO < 30s, RPO = 0','Multi-region active-active + Kafka geo-replication')}
          </tbody>
        </table>
      </div>

      <!-- Security Threat Model -->
      <div class="section">
        <div class="section-header">
          <span class="section-num">07</span>
          <h2 class="section-title">Security Threat Model</h2>
        </div>
        <div class="threat-grid">
          ${_threat('AI Purification Attack',
            'Diffusion model / GAN removes forensic watermark while preserving visual quality',
            'Adversarial-only training with purification simulation. Temporal pooling increases attack surface.')}
          ${_threat('Geometric Transformation Evasion',
            'Heavy cropping, rotation, or resolution shifts alter the watermark signal',
            'Learned detectors trained on geometric distortion augmentation. Soft-binding fallback via fingerprint.')}
          ${_threat('Adversarial Watermarking Attack',
            'Pre-injected perturbation exploits the watermark to cause false attribution',
            'Pre-embedding adversarial scan on ingest. Multi-modal cross-check required for attribution.')}
          ${_threat('Re-Streaming via Monitor Capture',
            'Pirate records an authorized 2D display with a camera, bypassing digital watermarks',
            'Sony C2PA 3D depth sensor detects flat display recording vs. live subject.')}
          ${_threat('C2PA Metadata Stripping',
            'Attacker strips Content Credentials metadata from the file before redistribution',
            'Soft-binding: invisible watermark + fingerprint links asset to blockchain record.')}
          ${_threat('Smart Contract Manipulation',
            'Attacker attempts to forge a valid license or block enforcement contract execution',
            'Contracts are immutable post-deploy. Gnosis Safe multisig. Chainlink oracle bridges evidence.')}
        </div>
      </div>

      <!-- Roadmap -->
      <div class="section">
        <div class="section-header">
          <span class="section-num">08</span>
          <h2 class="section-title">Delivery Roadmap</h2>
        </div>
        <div class="roadmap">
          <div class="rm-card">
            <div class="rm-phase" style="color:var(--accent)">Phase 01</div>
            <div class="rm-timeline">Months 1–4 · Foundation</div>
            <ul class="rm-list">
              <li>Core microservice scaffolding (Go + gRPC)</li>
              <li>Kafka + Storm pipeline skeleton</li>
              <li>C2PA provenance service integration</li>
              <li>Asset catalog service (PostgreSQL + ES)</li>
              <li>Auth gateway + DRM license server</li>
              <li>Basic CI/CD + infra (Terraform, EKS)</li>
            </ul>
          </div>
          <div class="rm-card">
            <div class="rm-phase" style="color:var(--accent2)">Phase 02</div>
            <div class="rm-timeline">Months 5–8 · ML Core</div>
            <ul class="rm-list">
              <li>Adversarial-only watermark model training</li>
              <li>CDN edge watermark embedder deployment</li>
              <li>Temporal pooling implementation</li>
              <li>MMD-Agent copy detection v1</li>
              <li>P2P crawler fleet (social + IPTV)</li>
              <li>Watermark extraction pipeline</li>
            </ul>
          </div>
          <div class="rm-card">
            <div class="rm-phase" style="color:var(--accent3)">Phase 03</div>
            <div class="rm-timeline">Months 9–12 · Enforcement</div>
            <ul class="rm-list">
              <li>Story Protocol IP token minting</li>
              <li>Smart enforcement contract deployment</li>
              <li>CDN session termination integration</li>
              <li>Revenue redirection (on-chain royalty)</li>
              <li>Chainlink oracle bridge</li>
              <li>Grafana piracy heatmap dashboard</li>
            </ul>
          </div>
          <div class="rm-card">
            <div class="rm-phase" style="color:var(--white)">Phase 04</div>
            <div class="rm-timeline">Months 13–18 · Scale & Harden</div>
            <ul class="rm-list">
              <li>Multi-region active-active deployment</li>
              <li>Continuous adversarial retraining loop</li>
              <li>KEDA autoscaler tuning (10M streams)</li>
              <li>Compliance audit (GDPR / CCPA)</li>
              <li>Legal evidence export certification</li>
              <li>Partner SDK for broadcaster integration</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Team Structure -->
      <div class="section">
        <div class="section-header">
          <span class="section-num">09</span>
          <h2 class="section-title">Recommended Team Structure</h2>
        </div>
        <div class="stack-grid">
          <div class="stack-card">
            <h4>// Engineering</h4>
            <div class="stack-row"><span class="k">Backend (Go)</span><span class="v">3 Engineers — Core services & gRPC</span></div>
            <div class="stack-row"><span class="k">ML / AI</span><span class="v">3 Engineers — Watermark models, MMD-Agent</span></div>
            <div class="stack-row"><span class="k">Data Engineering</span><span class="v">2 Engineers — Kafka, Storm, ClickHouse</span></div>
            <div class="stack-row"><span class="k">Blockchain</span><span class="v">2 Engineers — Smart contracts, oracle bridge</span></div>
            <div class="stack-row"><span class="k">DevOps / SRE</span><span class="v">2 Engineers — K8s, Terraform, SLAs</span></div>
            <div class="stack-row"><span class="k">Frontend</span><span class="v">1 Engineer — Ops dashboard</span></div>
          </div>
          <div class="stack-card">
            <h4>// Leadership & Specialists</h4>
            <div class="stack-row"><span class="k">Engineering Lead</span><span class="v">1 × Principal Architect</span></div>
            <div class="stack-row"><span class="k">ML Lead</span><span class="v">1 × Research Engineer (watermarking)</span></div>
            <div class="stack-row"><span class="k">Product</span><span class="v">1 × PM (sports media domain)</span></div>
            <div class="stack-row"><span class="k">Security</span><span class="v">1 × AppSec + Threat Model specialist</span></div>
            <div class="stack-row"><span class="k">Legal / IP</span><span class="v">1 × IP Counsel (rights + compliance)</span></div>
            <div class="stack-row"><span class="k">QA</span><span class="v">1 × SDET (adversarial test suites)</span></div>
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

function _layer(num, name, cls, items) {
  const boxes = items.map(i => `<div class="lbox ${cls}"><span class="lbox-dot"></span> ${i}</div>`).join('');
  return `<div class="arch-layer">
    <div class="layer-label"><div class="l-num">${num}</div><div class="l-name">${name}</div></div>
    <div class="layer-boxes">${boxes}</div>
  </div>`;
}

function _comp(icon, name, role, items) {
  const lis = items.map(i => `<li>${i}</li>`).join('');
  return `<div class="comp-card">
    <div class="comp-icon">${icon}</div>
    <div class="comp-name">${name}</div>
    <div class="comp-role">${role}</div>
    <ul class="comp-list">${lis}</ul>
  </div>`;
}

function _nfr(cat, req, metric, mech) {
  return `<tr><td class="category">${cat}</td><td>${req}</td><td class="metric">${metric}</td><td>${mech}</td></tr>`;
}

function _threat(title, desc, mit) {
  return `<div class="threat-card">
    <div class="threat-title">${title}</div>
    <div><div class="threat-sub">Threat</div><div class="threat-desc">${desc}</div></div>
    <div><div class="threat-sub">Mitigation</div><div class="threat-mit">${mit}</div></div>
  </div>`;
}
