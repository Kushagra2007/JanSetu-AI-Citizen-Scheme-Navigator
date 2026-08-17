const STATUS_COLORS = { draft: 'badge-orange', submitted: 'badge-blue', review: 'badge-blue', approved: 'badge-green', rejected: 'badge-red', completed: 'badge-green' };

function renderApp(a) {
  const total = a.progress.length || 1;
  const done = a.progress.filter(p => p.completed).length;
  const pct = Math.round((done / total) * 100);
  return `
    <div class="card glass">
      <div style="display:flex;justify-content:space-between;">
        <h3>${a.ref_name}</h3>
        <span class="badge ${STATUS_COLORS[a.status] || 'badge-blue'}">${a.status}</span>
      </div>
      <p style="color:var(--text-muted);">Type: ${a.type} · Created ${new Date(a.created_at).toLocaleDateString()}</p>
      <div class="progress-bar" style="margin:10px 0;"><div class="progress-fill" style="width:${pct}%;"></div></div>
      <p style="font-size:0.85rem;">${done}/${total} steps completed</p>
      <div style="display:flex;gap:10px;margin-top:12px;flex-wrap:wrap;">
        ${a.progress.map(p => `<button class="btn ${p.completed ? 'btn-secondary' : 'btn-ghost'}" style="padding:6px 12px;font-size:0.8rem;" onclick="toggleAppStep(${a.id}, ${p.step}, ${!p.completed})">Step ${p.step + 1} ${p.completed ? '✓' : ''}</button>`).join('')}
      </div>
      <div style="margin-top:12px;display:flex;gap:10px;">
        <select onchange="updateAppStatus(${a.id}, this.value)" class="form-control" style="width:auto;">
          ${['draft','submitted','review','approved','rejected','completed'].map(s => `<option value="${s}" ${s===a.status?'selected':''}>${s}</option>`).join('')}
        </select>
        <button class="btn btn-outline" onclick="deleteApp(${a.id})">🗑 Delete</button>
      </div>
    </div>`;
}

async function loadApplications() {
  const res = await apiFetch('/api/applications');
  if (!res || !res.ok) return;
  const apps = await res.json();
  document.getElementById('appsGrid').innerHTML = apps.map(renderApp).join('') || '<p>No applications yet. Start one from Schemes or Services!</p>';
}

async function toggleAppStep(appId, stepIndex, completed) {
  await apiFetch(`/api/applications/${appId}/step`, { method: 'PUT', body: JSON.stringify({ step_index: stepIndex, completed }) });
  loadApplications();
}

async function updateAppStatus(appId, status) {
  await apiFetch(`/api/applications/${appId}/status`, { method: 'PUT', body: JSON.stringify({ status }) });
  loadApplications();
}

async function deleteApp(appId) {
  if (!confirm('Delete this application?')) return;
  await apiFetch(`/api/applications/${appId}`, { method: 'DELETE' });
  loadApplications();
}

document.addEventListener('DOMContentLoaded', loadApplications);