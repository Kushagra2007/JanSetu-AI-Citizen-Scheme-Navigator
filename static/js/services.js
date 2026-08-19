let allServices = [];

function renderService(service) {
  return `<article class="card glass"><span class="badge badge-blue">${service.category}</span><h3 style="margin-top:14px;">${service.name}</h3><p style="color:var(--text-muted);line-height:1.55;margin:8px 0 16px;">${service.description}</p><p style="font-size:.82rem;color:var(--text-muted);margin-bottom:4px;">Estimated time: ${service.duration_estimate}</p><p style="font-size:.82rem;color:var(--text-muted);">Fee: ${service.fee}</p><a class="btn btn-primary" style="margin-top:18px;" href="/service/${service.id}">View pathway <span aria-hidden="true">→</span></a></article>`;
}
async function loadServices() {
  const response = await apiFetch('/api/services');
  if (!response || !response.ok) return;
  allServices = await response.json();
  const categorySelect = document.getElementById('serviceCategory');
  [...new Set(allServices.map(service => service.category))].sort().forEach(category => {
    categorySelect.insertAdjacentHTML('beforeend', `<option value="${category}">${category}</option>`);
  });
  renderFilteredServices();
}
function renderFilteredServices() {
  const query = document.getElementById('serviceSearch').value.trim().toLowerCase();
  const category = document.getElementById('serviceCategory').value;
  const services = allServices.filter(service => !category || service.category === category)
    .filter(service => !query || `${service.name} ${service.category} ${service.description}`.toLowerCase().includes(query));
  document.getElementById('servicesGrid').innerHTML = services.map(renderService).join('') || '<p>No matching service pathway was found.</p>';
}
document.addEventListener('DOMContentLoaded', () => {
  loadServices();
  document.getElementById('serviceSearch').addEventListener('input', renderFilteredServices);
  document.getElementById('serviceCategory').addEventListener('change', renderFilteredServices);
});
