async function apiFetch(url, options = {}) {
  const opts = { credentials: 'include', headers: { 'Content-Type': 'application/json' }, ...options };
  const res = await fetch(url, opts);
  const currentPath = window.location.pathname;
  if (res.status === 401 && currentPath !== '/login' && currentPath !== '/register') {
    window.location.href = '/login';
    return null;
  }
  return res;
}

async function loadUnreadCount() {
  const currentPath = window.location.pathname;
  if (currentPath === '/login' || currentPath === '/register') return;
  const res = await apiFetch('/api/notifications/unread-count');
  if (!res || !res.ok) return;
  const data = await res.json();
  const dot = document.getElementById('unreadDot');
  if (dot) {
    if (data.unread_count > 0) { dot.style.display = 'flex'; dot.textContent = data.unread_count; }
    else dot.style.display = 'none';
  }
}

function setActiveNav() {
  const path = window.location.pathname;
  document.querySelectorAll('.nav-links a').forEach(a => {
    if (a.getAttribute('href') === path) a.classList.add('active');
  });
}

async function logout() {
  await apiFetch('/api/auth/logout', { method: 'POST' });
  window.location.href = '/';
}

document.addEventListener('DOMContentLoaded', () => {
  setActiveNav();
  loadUnreadCount();
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/static/service-worker.js').catch(() => {});
  }
});