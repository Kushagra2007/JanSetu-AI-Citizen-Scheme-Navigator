let service;

function escapeHtml(value) {
  const element = document.createElement('div');
  element.textContent = value ?? '';
  return element.innerHTML;
}

function renderSteps(steps) {
  const container = document.getElementById('stepsContainer');
  container.innerHTML = steps.map((step, index) => `
    <article class="card glass" style="margin-bottom:12px;">
      <h3>${index + 1}. ${escapeHtml(step.title)}</h3>
      <p style="color:var(--text-muted);margin:8px 0;">${escapeHtml(step.description)}</p>
      <p><strong>Estimated time:</strong> ${escapeHtml(step.duration || 'Not specified')}</p>
      ${step.documents?.length ? `<p><strong>Documents:</strong> ${step.documents.map(escapeHtml).join(', ')}</p>` : ''}
      ${step.sub_tasks?.length ? `<ul>${step.sub_tasks.map(task => `<li>${escapeHtml(task)}</li>`).join('')}</ul>` : ''}
      ${step.url ? `<a class="btn btn-outline" href="${escapeHtml(step.url)}" target="_blank" rel="noopener">Open official site</a>` : ''}
    </article>`).join('') || '<p>No steps are available for this service yet.</p>';
}

async function loadService() {
  const res = await apiFetch(`/api/services/${SERVICE_ID}`);
  if (!res || !res.ok) return;
  service = await res.json();
  document.getElementById('serviceTitle').textContent = service.name;
  renderSteps(service.steps);
}

async function startApplication() {
  const res = await apiFetch('/api/applications', {
    method: 'POST', body: JSON.stringify({ type: 'service', ref_id: SERVICE_ID }),
  });
  if (res?.ok) window.location.assign('/applications');
}

document.addEventListener('DOMContentLoaded', () => {
  loadService();
  document.getElementById('startAppBtn')?.addEventListener('click', startApplication);
  document.getElementById('listenAllBtn')?.addEventListener('click', () => {
    if (!service || typeof speakText !== 'function') return;
    const text = service.steps.map((step, index) => `Step ${index + 1}: ${step.title}. ${step.description}`).join('. ');
    speakText(text, document.getElementById('langSelect')?.value || 'en');
  });
});
