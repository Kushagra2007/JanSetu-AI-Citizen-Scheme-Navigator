async function loadDigiLockerStatus() {
  const res = await apiFetch('/api/auth/me');
  if (!res?.ok) return;
  const user = await res.json();
  const connected = Boolean(user.digilocker_connected);
  document.getElementById('digilockerStatus').textContent = connected
    ? 'DigiLocker is connected. Your verified documents can be used in eligibility checks.'
    : 'Connect DigiLocker to import and verify your documents.';
  document.getElementById('connectDigiLockerBtn').style.display = connected ? 'none' : '';
  document.getElementById('refreshDigiLockerBtn').style.display = connected ? '' : 'none';
  document.getElementById('disconnectDigiLockerBtn').style.display = connected ? '' : 'none';
}

document.addEventListener('DOMContentLoaded', () => {
  loadDigiLockerStatus();
  document.getElementById('connectDigiLockerBtn')?.addEventListener('click', async () => {
    const res = await apiFetch('/api/digilocker/connect');
    if (res?.ok) window.location.assign((await res.json()).auth_url);
  });
  document.getElementById('refreshDigiLockerBtn')?.addEventListener('click', async () => {
    await apiFetch('/api/digilocker/refresh', { method: 'POST' });
    loadDigiLockerStatus();
  });
  document.getElementById('disconnectDigiLockerBtn')?.addEventListener('click', async () => {
    await apiFetch('/api/digilocker/disconnect', { method: 'POST' });
    loadDigiLockerStatus();
  });
});
