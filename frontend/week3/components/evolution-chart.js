/**
 * ═══════════════════════════════════════════════════════════════════════════
 * QUIRRELY EVOLUTION CHART COMPONENT v2.0
 * ═══════════════════════════════════════════════════════════════════════════
 * 
 * Visualizes how a user's writing voice evolves over time.
 * Shows profile distribution, trends, and patterns.
 * 
 * Uses Chart.js for rendering.
 */

class EvolutionChart extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this.chart = null;
  }
  
  static get observedAttributes() {
    return ['data', 'days', 'chart-type'];
  }
  
  connectedCallback() {
    this.render();
    this.loadChartJS().then(() => this.initChart());
  }
  
  disconnectedCallback() {
    if (this.chart) {
      this.chart.destroy();
    }
  }
  
  attributeChangedCallback(name, oldVal, newVal) {
    if (oldVal !== newVal && this.chart) {
      this.updateChart();
    }
  }
  
  get chartData() {
    try {
      return JSON.parse(this.getAttribute('data') || '{}');
    } catch {
      return {};
    }
  }
  
  get days() {
    return parseInt(this.getAttribute('days') || '30');
  }
  
  get chartType() {
    return this.getAttribute('chart-type') || 'timeline'; // 'timeline', 'distribution', 'radar'
  }
  
  async loadChartJS() {
    if (window.Chart) return;
    
    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = 'https://cdn.jsdelivr.net/npm/chart.js';
      script.onload = resolve;
      script.onerror = reject;
      document.head.appendChild(script);
    });
  }
  
  render() {
    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
          width: 100%;
        }
        
        .container {
          position: relative;
          width: 100%;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }
        
        .chart-wrapper {
          position: relative;
          height: 200px;
          width: 100%;
        }
        
        canvas {
          width: 100% !important;
          height: 100% !important;
        }
        
        .loading {
          position: absolute;
          inset: 0;
          display: flex;
          align-items: center;
          justify-content: center;
          background: #F8F5F0;
          border-radius: 12px;
          color: #636E72;
          font-size: 0.9rem;
        }
        
        .empty-state {
          text-align: center;
          padding: 2rem;
          color: #636E72;
        }
        
        .empty-state .icon {
          font-size: 2.5rem;
          margin-bottom: 0.75rem;
        }
        
        .empty-state h4 {
          margin-bottom: 0.5rem;
          color: #2D3436;
        }
        
        .legend {
          display: flex;
          flex-wrap: wrap;
          gap: 1rem;
          margin-top: 1rem;
          justify-content: center;
        }
        
        .legend-item {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 0.8rem;
          color: #636E72;
        }
        
        .legend-color {
          width: 12px;
          height: 12px;
          border-radius: 3px;
        }
        
        .summary {
          display: flex;
          justify-content: space-around;
          padding: 1rem 0;
          margin-top: 1rem;
          border-top: 1px solid #E9ECEF;
        }
        
        .stat {
          text-align: center;
        }
        
        .stat-value {
          font-size: 1.25rem;
          font-weight: 700;
          color: #2D3436;
        }
        
        .stat-label {
          font-size: 0.7rem;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          color: #636E72;
        }
        
        .trend {
          display: inline-flex;
          align-items: center;
          gap: 0.25rem;
        }
        
        .trend.up { color: #00B894; }
        .trend.down { color: #FF6B6B; }
        .trend.stable { color: #636E72; }
      </style>
      
      <div class="container">
        <div class="chart-wrapper">
          <canvas id="evolutionCanvas"></canvas>
          <div class="loading" id="loading">Loading chart...</div>
        </div>
        <div class="legend" id="legend"></div>
        <div class="summary" id="summary"></div>
      </div>
    `;
  }
  
  initChart() {
    const data = this.chartData;
    const canvas = this.shadowRoot.getElementById('evolutionCanvas');
    const loading = this.shadowRoot.getElementById('loading');
    
    if (!data.timeline || data.timeline.length === 0) {
      loading.innerHTML = `
        <div class="empty-state">
          <div class="icon">📊</div>
          <h4>No evolution data yet</h4>
          <p>Analyze more text to see your voice evolve</p>
        </div>
      `;
      return;
    }
    
    loading.style.display = 'none';
    
    const ctx = canvas.getContext('2d');
    
    if (this.chartType === 'distribution') {
      this.renderDistributionChart(ctx, data);
    } else if (this.chartType === 'radar') {
      this.renderRadarChart(ctx, data);
    } else {
      this.renderTimelineChart(ctx, data);
    }
    
    this.renderSummary(data);
  }
  
  renderTimelineChart(ctx, data) {
    const profileColors = {
      ASSERTIVE: '#FF6B6B',
      MINIMAL: '#4ECDC4',
      POETIC: '#A29BFE',
      DENSE: '#6C5CE7',
      CONVERSATIONAL: '#FDCB6E',
      FORMAL: '#636E72',
      BALANCED: '#00B894',
      LONGFORM: '#0984E3',
      INTERROGATIVE: '#E17055',
      HEDGED: '#81ECEC'
    };
    
    // Group by date and profile
    const dateGroups = {};
    data.timeline.forEach(entry => {
      const date = entry.date || new Date(entry.timestamp).toISOString().split('T')[0];
      if (!dateGroups[date]) {
        dateGroups[date] = {};
      }
      const profile = entry.profileType || entry.profile;
      dateGroups[date][profile] = (dateGroups[date][profile] || 0) + 1;
    });
    
    const dates = Object.keys(dateGroups).sort();
    const profiles = [...new Set(data.timeline.map(e => e.profileType || e.profile))];
    
    const datasets = profiles.map(profile => ({
      label: profile,
      data: dates.map(date => dateGroups[date][profile] || 0),
      backgroundColor: profileColors[profile] || '#999',
      borderColor: profileColors[profile] || '#999',
      borderWidth: 2,
      tension: 0.3,
      fill: false
    }));
    
    this.chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: dates.map(d => {
          const date = new Date(d);
          return `${date.getMonth() + 1}/${date.getDate()}`;
        }),
        datasets
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            mode: 'index',
            intersect: false
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              stepSize: 1
            }
          }
        }
      }
    });
    
    // Render custom legend
    this.renderLegend(profiles, profileColors);
  }
  
  renderDistributionChart(ctx, data) {
    const profileColors = {
      ASSERTIVE: '#FF6B6B',
      MINIMAL: '#4ECDC4',
      POETIC: '#A29BFE',
      DENSE: '#6C5CE7',
      CONVERSATIONAL: '#FDCB6E',
      FORMAL: '#636E72',
      BALANCED: '#00B894',
      LONGFORM: '#0984E3',
      INTERROGATIVE: '#E17055',
      HEDGED: '#81ECEC'
    };
    
    const distribution = data.profiles || {};
    const labels = Object.keys(distribution);
    const values = Object.values(distribution);
    const colors = labels.map(l => profileColors[l] || '#999');
    
    this.chart = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels,
        datasets: [{
          data: values,
          backgroundColor: colors,
          borderWidth: 2,
          borderColor: '#fff'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              boxWidth: 12,
              padding: 15
            }
          }
        }
      }
    });
  }
  
  renderRadarChart(ctx, data) {
    const metrics = data.metrics || {
      assertiveness: 0.7,
      complexity: 0.5,
      formality: 0.3,
      openness: 0.8,
      rhythmicity: 0.4
    };
    
    this.chart = new Chart(ctx, {
      type: 'radar',
      data: {
        labels: Object.keys(metrics).map(k => k.charAt(0).toUpperCase() + k.slice(1)),
        datasets: [{
          label: 'Your Voice',
          data: Object.values(metrics).map(v => v * 100),
          backgroundColor: 'rgba(255, 107, 107, 0.2)',
          borderColor: '#FF6B6B',
          borderWidth: 2,
          pointBackgroundColor: '#FF6B6B'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          r: {
            beginAtZero: true,
            max: 100
          }
        },
        plugins: {
          legend: {
            display: false
          }
        }
      }
    });
  }
  
  renderLegend(profiles, colors) {
    const legend = this.shadowRoot.getElementById('legend');
    legend.innerHTML = profiles.map(profile => `
      <div class="legend-item">
        <div class="legend-color" style="background: ${colors[profile]}"></div>
        <span>${profile}</span>
      </div>
    `).join('');
  }
  
  renderSummary(data) {
    const summary = this.shadowRoot.getElementById('summary');
    
    const totalEntries = data.entries || data.timeline?.length || 0;
    const dominantProfile = data.dominant_profile || data.dominantProfile || '—';
    const trend = data.trend || 'stable';
    
    const trendIcons = {
      up: '↑ Shifting',
      down: '↓ Changing',
      stable: '→ Consistent',
      increasing: '↑ Growing',
      decreasing: '↓ Declining'
    };
    
    const trendClass = trend.includes('up') || trend.includes('increas') ? 'up' : 
                       trend.includes('down') || trend.includes('decreas') ? 'down' : 'stable';
    
    summary.innerHTML = `
      <div class="stat">
        <div class="stat-value">${totalEntries}</div>
        <div class="stat-label">Analyses</div>
      </div>
      <div class="stat">
        <div class="stat-value">${dominantProfile}</div>
        <div class="stat-label">Dominant</div>
      </div>
      <div class="stat">
        <div class="stat-value">
          <span class="trend ${trendClass}">${trendIcons[trend] || trend}</span>
        </div>
        <div class="stat-label">Trend</div>
      </div>
    `;
  }
  
  updateChart() {
    if (this.chart) {
      this.chart.destroy();
    }
    this.initChart();
  }
  
  // Public method to update data
  setData(data) {
    this.setAttribute('data', JSON.stringify(data));
  }
}

// Register the component
customElements.define('evolution-chart', EvolutionChart);

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = EvolutionChart;
}
