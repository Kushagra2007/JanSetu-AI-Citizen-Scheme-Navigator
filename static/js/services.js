function renderService(service) {
  return `<article class="card glass"><span class="badge badge-blue">${service.category}</span><h3 style="margin-top:14px;">${service.name}</h3><p style="color:var(--text-muted);line-height:1.55;margin:8px 0 16px;">${service.description}</p><p style="font-size:.82rem;color:var(--text-muted);margin-bottom:4px;">Estimated time: ${service.duration_estimate}</p><p style="font-size:.82rem;color:var(--text-muted);">Fee: ${service.fee}</p><a class="btn btn-primary" style="margin-top:18px;" href="/service/${service.id}">View pathway <span aria-hidden="true">→</span></a></article>`;
}
async function loadServices() {
  const response = await apiFetch('/api/services');
  if (!response || !response.ok) return;
  const services = await response.json();
  document.getElementById('servicesGrid').innerHTML = services.map(renderService).join('') || '<p>No service pathways are available yet.</p>';
}
document.addEventListener('DOMContentLoaded', loadServices);
