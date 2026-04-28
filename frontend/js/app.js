/**
 * Sports Media Sentinel — SPA Router & Application Core
 */
import { wsManager } from './ws.js';
import { renderLanding, updateLandingStats } from './pages/landing.js';
import { renderDashboard, handleDashboardEvent, updateDashboardKPIs, updateDashboardPipeline, destroyDashboard } from './pages/dashboard.js';
import { renderPipeline, handlePipelineEvent, updatePipelineStats, destroyPipeline } from './pages/pipeline.js';
import { renderArchitecture } from './pages/architecture.js';
import { renderLab, destroyLab } from './pages/lab.js';

const ROUTES = {
  '':            { render: renderLanding,     label: 'Overview',      icon: '◆' },
  'dashboard':   { render: renderDashboard,   label: 'Dashboard',     icon: '▣' },
  'pipeline':    { render: renderPipeline,    label: 'Pipeline',      icon: '▷' },
  'architecture':{ render: renderArchitecture,label: 'Architecture',  icon: '◇' },
  'lab':         { render: renderLab,         label: 'Lab',           icon: '⚗' },
};

let currentRoute = '';
let kpiInterval;

function init() {
  // Build navigation
  const nav = document.getElementById('main-nav');
  const navLinks = document.createElement('ul');
  navLinks.className = 'nav-links';
  for (const [hash, route] of Object.entries(ROUTES)) {
    const a = document.createElement('a');
    a.href = `#${hash}`;
    a.dataset.route = hash;
    a.innerHTML = `${route.icon} ${route.label}`;
    navLinks.appendChild(a);
  }
  nav.insertBefore(navLinks, nav.querySelector('.nav-status'));

  // Route handler
  window.addEventListener('hashchange', navigate);
  navigate();

  // Connect WebSocket
  const wsProtocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = `${wsProtocol}//${location.hostname}:${location.port || 8000}/ws`;
  wsManager.connect(wsUrl);

  // Handle all events
  wsManager.on('_all', handleEvent);

  // Connection status
  wsManager.on('_connected', () => {
    document.getElementById('ws-status').textContent = 'CONNECTED';
    document.getElementById('ws-dot').style.background = 'var(--accent3)';
  });
  wsManager.on('_disconnected', () => {
    document.getElementById('ws-status').textContent = 'RECONNECTING';
    document.getElementById('ws-dot').style.background = 'var(--accent2)';
  });

  // Fetch KPIs periodically
  kpiInterval = setInterval(fetchKPIs, 2000);
  fetchKPIs();
}

function navigate() {
  const hash = location.hash.replace('#', '');
  const route = ROUTES[hash] || ROUTES[''];
  const routeKey = ROUTES[hash] ? hash : '';

  // Cleanup old page
  if (currentRoute === 'dashboard') destroyDashboard();
  if (currentRoute === 'pipeline') destroyPipeline();
  if (currentRoute === 'lab') destroyLab();

  // Render new page
  const container = document.getElementById('app');
  route.render(container);
  currentRoute = routeKey;

  // Update nav active state
  document.querySelectorAll('.nav-links a').forEach(a => {
    a.classList.toggle('active', a.dataset.route === routeKey);
  });
}

function handleEvent(msg) {
  // Route to active page
  if (currentRoute === 'dashboard') {
    handleDashboardEvent(msg);
  } else if (currentRoute === 'pipeline') {
    handlePipelineEvent(msg);
  }
}

async function fetchKPIs() {
  try {
    const [kpiRes, pipeRes] = await Promise.all([
      fetch('/api/kpis'),
      fetch('/api/pipeline/stats'),
    ]);
    const kpis = await kpiRes.json();
    const pipeStats = await pipeRes.json();

    // Fetch severity distribution for dashboard
    try {
      const sevRes = await fetch('/api/severity');
      const severity = await sevRes.json();
      kpis._severity = severity;
    } catch (e) { /* ok */ }

    // Update active page
    if (currentRoute === '') {
      updateLandingStats(kpis);
    } else if (currentRoute === 'dashboard') {
      updateDashboardKPIs(kpis);
      updateDashboardPipeline(pipeStats);
    } else if (currentRoute === 'pipeline') {
      updatePipelineStats(pipeStats);
    }
  } catch (e) {
    // Server not ready yet
  }
}

// Boot
document.addEventListener('DOMContentLoaded', init);
