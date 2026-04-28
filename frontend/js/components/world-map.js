/**
 * Sports Media Sentinel — SVG World Map with Piracy Heatmap
 */
export class WorldMap {
  constructor(container) {
    this.container = container;
    this.dots = [];
    this.maxDots = 150;
    this._buildMap();
  }

  _buildMap() {
    // Simplified world map using SVG path data (low-poly continents)
    this.container.innerHTML = `
      <svg viewBox="0 0 1000 500" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%">
        <defs>
          <radialGradient id="dotGlow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#ff3d57" stop-opacity="0.8"/>
            <stop offset="100%" stop-color="#ff3d57" stop-opacity="0"/>
          </radialGradient>
          <radialGradient id="dotGlowGreen" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#b8ff57" stop-opacity="0.8"/>
            <stop offset="100%" stop-color="#b8ff57" stop-opacity="0"/>
          </radialGradient>
          <radialGradient id="dotGlowCyan" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#00e5ff" stop-opacity="0.6"/>
            <stop offset="100%" stop-color="#00e5ff" stop-opacity="0"/>
          </radialGradient>
        </defs>
        <!-- Grid -->
        <g stroke="rgba(30,45,61,.3)" stroke-width="0.5" fill="none">
          ${Array.from({length: 9}, (_, i) => `<line x1="0" y1="${(i+1)*50}" x2="1000" y2="${(i+1)*50}"/>`).join('')}
          ${Array.from({length: 19}, (_, i) => `<line x1="${(i+1)*50}" y1="0" x2="${(i+1)*50}" y2="500"/>`).join('')}
        </g>
        <!-- Continents (simplified) -->
        <g fill="rgba(30,45,61,.5)" stroke="rgba(30,45,61,.8)" stroke-width="0.5">
          <!-- North America -->
          <path d="M120,80 L220,60 L270,90 L280,140 L260,180 L230,200 L200,210 L170,220 L150,200 L130,160 L110,140 L100,110 Z"/>
          <path d="M230,200 L260,210 L270,240 L250,260 L220,250 L210,230 Z"/>
          <!-- South America -->
          <path d="M240,280 L270,270 L290,290 L300,330 L310,370 L300,410 L280,430 L260,420 L250,380 L240,340 L230,310 Z"/>
          <!-- Europe -->
          <path d="M440,80 L480,70 L520,80 L540,100 L530,130 L510,150 L490,160 L460,150 L440,130 L430,100 Z"/>
          <!-- Africa -->
          <path d="M450,190 L490,180 L530,200 L550,240 L560,290 L550,340 L530,370 L500,380 L470,370 L450,340 L440,290 L440,240 Z"/>
          <!-- Asia -->
          <path d="M550,60 L620,50 L700,60 L780,80 L820,100 L830,140 L810,170 L760,180 L700,170 L650,160 L600,150 L560,130 L540,100 Z"/>
          <!-- India -->
          <path d="M650,170 L680,170 L700,200 L690,240 L670,260 L650,240 L640,210 Z"/>
          <!-- Southeast Asia -->
          <path d="M730,180 L770,170 L800,190 L810,220 L790,240 L760,230 L740,210 Z"/>
          <!-- Australia -->
          <path d="M780,310 L840,300 L880,320 L890,360 L870,390 L830,400 L790,380 L770,350 L770,330 Z"/>
        </g>
        <!-- Equator -->
        <line x1="0" y1="250" x2="1000" y2="250" stroke="rgba(0,229,255,.1)" stroke-width="0.5" stroke-dasharray="4,4"/>
        <!-- Event dots layer -->
        <g id="map-dots"></g>
        <!-- Region labels -->
        <g fill="rgba(74,96,112,.6)" font-family="IBM Plex Mono" font-size="8" letter-spacing="2">
          <text x="180" y="175">NA</text>
          <text x="260" y="350">SA</text>
          <text x="480" y="130">EU</text>
          <text x="495" y="290">AF</text>
          <text x="700" y="130">APAC</text>
          <text x="640" y="220">ME</text>
        </g>
      </svg>
    `;
    this.dotsLayer = this.container.querySelector('#map-dots');
  }

  addDetection(lat, lon, severity = 'high') {
    const x = ((lon + 180) / 360) * 1000;
    const y = ((90 - lat) / 180) * 500;

    const colors = {
      critical: '#ff3d57',
      high: '#ff9500',
      medium: '#ffd60a',
      enforcement: '#b8ff57',
      stream: '#00e5ff',
    };
    const color = colors[severity] || colors.high;
    const gradId = severity === 'enforcement' ? 'dotGlowGreen'
      : severity === 'stream' ? 'dotGlowCyan'
      : 'dotGlow';

    // Glow
    const glow = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    glow.setAttribute('cx', x);
    glow.setAttribute('cy', y);
    glow.setAttribute('r', '12');
    glow.setAttribute('fill', `url(#${gradId})`);
    glow.style.animation = 'mapPulse 2.5s ease-out forwards';

    // Dot
    const dot = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    dot.setAttribute('cx', x);
    dot.setAttribute('cy', y);
    dot.setAttribute('r', '3');
    dot.setAttribute('fill', color);

    const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    g.appendChild(glow);
    g.appendChild(dot);
    this.dotsLayer.appendChild(g);

    this.dots.push(g);

    // Remove old dots
    while (this.dots.length > this.maxDots) {
      const old = this.dots.shift();
      old.remove();
    }

    // Fade old dots
    setTimeout(() => {
      dot.setAttribute('r', '2');
      dot.style.opacity = '0.4';
    }, 3000);
  }

  clear() {
    this.dots.forEach(d => d.remove());
    this.dots = [];
  }
}
