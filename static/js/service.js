let allSchemes = [];

function renderSchemeCard(s) {
  const score = s.score;
  const scoreColor = score.total_score >= 70 ? 'badge-green' : score.total_score >= 40 ? 'badge-orange' : 'badge-red';
  return `
    <div class="card glass">
      <div style="display:flex;justify-content:space-between;align-items:start;">
        <h3>${s.name}</h3>
        <span class="badge ${scoreColor}">${score.total_score}% match</span>
      </div>
      <p style="color:var(--text-muted);margin:8px 0;">${s.description}</p>
      <span class="badge badge-blue">${s.category}</span>
      <div class="progress-bar" style="margin-top:12px;">
        <div class="progress-fill" style="width:${score.total_score}%;"></div>
      </div>
      <p style="font-size:0.8rem;margin-top:6px;color:var(--text-muted);">
        Eligibility ${score.eligibility_score}/60 · Docs ${score.document_score}/30 · Profile ${score.completeness_score}/10
      </p>
      ${score.missing_documents.length ? `<p style="font-size:0.8rem;color:#dc2626;">Missing docs: ${score.missing_documents.join(', ')}</p>` : ''}
      <div style="display:flex;gap:10px;margin-top:14px;flex-wrap:wrap;">
        <button class="btn btn-outline" onclick="saveScheme(${s.id})">💾 Save</button>
        <a class="btn btn-primary" href="${s.official_url}" target="_blank">Apply Now</a>
        <button class="btn btn-secondary" onclick="createApplication('scheme', ${s.id}, '${s.name.replace(/'/g, "\\'")}')">Track Application</button>
      </div>
    </div>`;
}

async function loadSchemes() {
  const res = await apiFetch('/api/schemes/recommended');
  if (!res || !res.ok) return;
  allSchemes = await res.json();
  renderSchemes(allSchemes);
}

function renderSchemes(schemes) {
  document.getElementById('schemesGrid').innerHTML = schemes.map(renderSchemeCard).join('') || '<p>No schemes found.</p>';
}

function filterSchemes() {
  const category = document.getElementById('categoryFilter').value;
  const minScore = parseInt(document.getElementById('scoreFilter').value || '0');
  let filtered = allSchemes;
  if (category) filtered = filtered.filter(s => s.category === category);
  filtered = filtered.filter(s => s.score.total_score >= minScore);
  renderSchemes(filtered);
}

async function saveScheme(id) {
  await apiFetch(`/api/schemes/${id}/save`, { method: 'POST' });
  alert('Scheme saved!');
}

async function createApplication(type, refId, name) {
  const res = await apiFetch('/api/applications', { method: 'POST', body: JSON.stringify({ type, ref_id: refId }) });
  if (res && res.ok) { window.location.href = '/applications'; }
}

document.addEventListener('DOMContentLoaded', () => {
  loadSchemes();
  document.getElementById('categoryFilter')?.addEventListener('change', filterSchemes);
  document.getElementById('scoreFilter')?.addEventListener('input', filterSchemes);
});