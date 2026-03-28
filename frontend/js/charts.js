/**
 * charts.js — Reusable chart and visualization helpers
 * Used by dashboard.js and forecast pages
 */

/**
 * Render a horizontal bar occupancy chart into a container element.
 * @param {string} containerId  - ID of the DOM element to render into
 * @param {Array}  wardData     - Array of { ward, total, available, occupied }
 */
function renderOccupancyChart(containerId, wardData) {
  const el = document.getElementById(containerId);
  if (!el || !wardData.length) return;

  el.innerHTML = wardData.map(ward => {
    const pct = Math.round((ward.occupied / ward.total) * 100) || 0;
    const barCls = pct >= 90 ? 'danger' : pct >= 75 ? 'warn' : '';
    const labelColor = pct >= 90 ? '#c62828' : pct >= 75 ? '#e65100' : '#2e7d32';

    return `
      <div style="margin-bottom:16px;">
        <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:5px;">
          <span style="font-size:13px;font-weight:600;">${ward.ward}</span>
          <span style="font-size:12px;color:${labelColor};font-weight:600;">${pct}%</span>
        </div>
        <div class="progress-bar">
          <div class="progress-fill ${barCls}" style="width:${pct}%"></div>
        </div>
        <div class="progress-label">
          <span style="color:#2e7d32;">${ward.available} available</span>
          <span>${ward.occupied} / ${ward.total}</span>
        </div>
      </div>
    `;
  }).join('');
}

/**
 * Render a simple vertical bar chart for forecast data.
 * @param {string} containerId
 * @param {Array}  forecastData - Array of { day, date, predicted_admissions, predicted_emergency, predicted_icu, surge_alert }
 */
function renderForecastBars(containerId, forecastData) {
  const el = document.getElementById(containerId);
  if (!el || !forecastData.length) return;

  const maxVal = Math.max(...forecastData.map(d => d.predicted_admissions), 1);

  el.innerHTML = `
    <div class="forecast-bar-wrap">
      ${forecastData.map(d => {
        const totalH = Math.round((d.predicted_admissions / maxVal) * 110);
        const emH    = Math.round((d.predicted_emergency  / maxVal) * 110);
        const icuH   = Math.round((d.predicted_icu        / maxVal) * 110);
        const surgeStyle = d.surge_alert ? 'border:1px solid #ef9a9a;border-radius:6px;padding:4px 2px;background:#fff5f5;' : '';

        return `
          <div class="forecast-bar-group" style="${surgeStyle}">
            ${d.surge_alert ? '<div style="font-size:9px;color:#c62828;font-weight:700;text-align:center;margin-bottom:2px;">SURGE</div>' : ''}
            <div class="forecast-bar-inner">
              <div class="forecast-bar total"     style="height:${totalH}px;" title="Total: ${d.predicted_admissions}"></div>
              <div class="forecast-bar emergency" style="height:${emH}px;"    title="Emergency: ${d.predicted_emergency}"></div>
              <div class="forecast-bar icu"       style="height:${icuH}px;"   title="ICU: ${d.predicted_icu}"></div>
            </div>
            <div class="forecast-label">
              <strong>${d.day.slice(0, 3)}</strong><br>
              ${d.date.slice(5)}
            </div>
          </div>
        `;
      }).join('')}
    </div>
    <div class="forecast-legend">
      <div class="legend-item"><div class="legend-dot" style="background:#1a4480;"></div> Total admissions</div>
      <div class="legend-item"><div class="legend-dot" style="background:#c62828;"></div> Emergency</div>
      <div class="legend-item"><div class="legend-dot" style="background:#e65100;"></div> ICU</div>
    </div>
  `;
}

/**
 * Render a donut-style occupancy ring using SVG.
 * @param {string} containerId
 * @param {number} pct  - 0–100
 * @param {string} label
 */
function renderDonut(containerId, pct, label) {
  const el = document.getElementById(containerId);
  if (!el) return;

  const r = 36, cx = 48, cy = 48;
  const circumference = 2 * Math.PI * r;
  const filled = (pct / 100) * circumference;
  const color = pct >= 90 ? '#c62828' : pct >= 75 ? '#e65100' : '#2e7d32';

  el.innerHTML = `
    <svg width="96" height="96" viewBox="0 0 96 96">
      <circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="#e0e0e0" stroke-width="8"/>
      <circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="${color}" stroke-width="8"
        stroke-dasharray="${filled} ${circumference}"
        stroke-dashoffset="${circumference / 4}"
        stroke-linecap="round"
        transform="rotate(-90 ${cx} ${cy})"/>
      <text x="${cx}" y="${cy - 4}" text-anchor="middle" font-size="14" font-weight="700"
            fill="${color}" font-family="Segoe UI, sans-serif">${pct}%</text>
      <text x="${cx}" y="${cy + 12}" text-anchor="middle" font-size="9"
            fill="#6b6b6b" font-family="Segoe UI, sans-serif">${label}</text>
    </svg>
  `;
}

/**
 * Format a UTC timestamp string to readable Indian date/time.
 * @param {string} ts
 * @returns {string}
 */
function formatTimestamp(ts) {
  return new Date(ts).toLocaleString('en-IN', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  });
}

/**
 * Show a toast notification. Requires a #toast element in the page.
 * @param {string} msg
 * @param {string} type  - 'success' | 'error' | ''
 */
function showToast(msg, type = '') {
  const t = document.getElementById('toast');
  if (!t) return;
  t.textContent = msg;
  t.className = `toast show ${type}`;
  setTimeout(() => { t.className = 'toast'; }, 3200);
}
