/**
 * beds.js — Bed map page logic
 * Handles loading, filtering, and updating bed status
 */

const API = 'http://localhost:5000/api';
let allBeds = [];

async function loadBeds() {
  const container = document.getElementById('beds-container');
  container.innerHTML = '<div class="loading"><div class="spinner"></div> Loading beds...</div>';
  try {
    allBeds = await fetch(`${API}/beds`).then(r => r.json());
    buildWardTabs();
    renderBeds(allBeds);
  } catch (e) {
    container.innerHTML = `
      <div class="empty-state">
        <div style="font-size:32px;">🏥</div>
        <p>Could not load beds.</p>
        <p>Make sure <code>python app.py</code> is running in the backend folder.</p>
      </div>`;
  }
}

function buildWardTabs() {
  const tabsEl = document.getElementById('ward-tabs');
  // Remove old ward tabs but keep the "All Wards" button
  tabsEl.querySelectorAll('.ward-tab').forEach(b => b.remove());

  const wards = [...new Set(allBeds.map(b => b.ward))];
  wards.forEach(w => {
    const btn = document.createElement('button');
    btn.className = 'btn btn-outline btn-sm ward-tab';
    btn.textContent = w;
    btn.onclick = function () { filterWard(w, this); };
    tabsEl.appendChild(btn);
  });
}

function filterWard(ward, btn) {
  // Update active button styling
  document.querySelectorAll('#ward-tabs button').forEach(b => {
    const isWardTab = b.classList.contains('ward-tab');
    b.className = (b === btn)
      ? (isWardTab ? 'btn btn-primary btn-sm ward-tab' : 'btn btn-primary btn-sm')
      : (isWardTab ? 'btn btn-outline btn-sm ward-tab' : 'btn btn-outline btn-sm');
  });
  renderBeds(ward ? allBeds.filter(b => b.ward === ward) : allBeds);
}

function renderBeds(beds) {
  const container = document.getElementById('beds-container');
  if (!beds.length) {
    container.innerHTML = '<div class="empty-state"><p>No beds found for this ward.</p></div>';
    return;
  }

  // Group by ward
  const byWard = beds.reduce((acc, b) => {
    if (!acc[b.ward]) acc[b.ward] = [];
    acc[b.ward].push(b);
    return acc;
  }, {});

  container.innerHTML = Object.entries(byWard).map(([ward, wardBeds]) => {
    const avail = wardBeds.filter(b => b.status === 'available').length;
    const occ   = wardBeds.filter(b => b.status === 'occupied').length;
    const maint = wardBeds.filter(b => b.status === 'maintenance').length;
    const pct   = Math.round((occ / wardBeds.length) * 100);
    const barCls = pct > 90 ? 'danger' : pct > 75 ? 'warn' : '';

    return `
      <div class="card" style="margin-bottom:20px;">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;flex-wrap:wrap;gap:8px;">
          <div class="card-title" style="margin:0;">${ward} Ward</div>
          <div style="font-size:12px;color:#6b6b6b;display:flex;gap:12px;align-items:center;">
            <span style="color:#2e7d32;font-weight:600;">${avail} free</span>
            <span style="color:#c62828;">${occ} occupied</span>
            ${maint ? `<span style="color:#6b6b6b;">${maint} maintenance</span>` : ''}
            <span>${wardBeds.length} total</span>
          </div>
        </div>
        <div class="progress-bar" style="margin-bottom:12px;">
          <div class="progress-fill ${barCls}" style="width:${pct}%"></div>
        </div>
        <div class="bed-grid">
          ${wardBeds.map(bed => `
            <div class="bed-cell ${bed.status}"
                 onclick="showBedMenu(${bed.id}, '${bed.status}', '${bed.bed_number}')"
                 title="${bed.bed_number} — ${bed.status}${bed.patient_id ? ' (Patient #' + bed.patient_id + ')' : ''}">
              <div style="font-size:10px;font-weight:700;">${bed.bed_number.split('-')[1] || bed.bed_number}</div>
              <div style="font-size:9px;opacity:0.7;margin-top:1px;">${bed.status === 'available' ? '✓' : bed.status === 'occupied' ? '●' : '⚙'}</div>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  }).join('');
}

function showBedMenu(id, currentStatus, bedNum) {
  const modal = document.getElementById('bed-modal');
  document.getElementById('bed-modal-title').textContent = `Bed ${bedNum}`;
  document.getElementById('bed-current-status').textContent = currentStatus;
  document.getElementById('bed-current-status').className =
    `badge ${currentStatus === 'available' ? 'badge-green' : currentStatus === 'occupied' ? 'badge-red' : 'badge-gray'}`;

  // Set button states
  ['available', 'occupied', 'maintenance'].forEach(s => {
    const btn = document.getElementById(`set-${s}`);
    btn.disabled = s === currentStatus;
    btn.onclick = () => updateBedStatus(id, s, bedNum);
  });

  modal.classList.add('open');
}

async function updateBedStatus(id, newStatus, bedNum) {
  try {
    await fetch(`${API}/beds/${id}/status`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus })
    });
    closeBedModal();
    showToast(`Bed ${bedNum} → ${newStatus}`, 'success');
    loadBeds();
  } catch (e) {
    showToast('Error updating bed status', 'error');
  }
}

function closeBedModal() {
  document.getElementById('bed-modal').classList.remove('open');
}

function showToast(msg, type = '') {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = `toast show ${type}`;
  setTimeout(() => { t.className = 'toast'; }, 3000);
}

// Initial load
loadBeds();
