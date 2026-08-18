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
  const errorBox = document.getElementById('errorBox');
  const showError = (message) => {
    if (!errorBox) return;
    errorBox.textContent = message;
    errorBox.style.display = 'block';
  };
  const submitAuthForm = async (form, url, payload) => {
    const submitButton = form.querySelector('button[type="submit"]');
    if (submitButton) submitButton.disabled = true;
    if (errorBox) errorBox.style.display = 'none';
    try {
      const res = await apiFetch(url, { method: 'POST', body: JSON.stringify(payload) });
      if (!res) return;
      const data = await res.json();
      if (!res.ok) return showError(data.detail || 'Unable to continue. Please try again.');
      window.location.assign('/chat');
    } catch (_) {
      showError('Unable to reach the server. Please try again.');
    } finally {
      if (submitButton) submitButton.disabled = false;
    }
  };
  document.getElementById('loginForm')?.addEventListener('submit', (event) => {
    event.preventDefault();
    submitAuthForm(event.currentTarget, '/api/auth/login', {
      email: document.getElementById('email').value.trim(),
      password: document.getElementById('password').value,
    });
  });
  document.getElementById('registerForm')?.addEventListener('submit', (event) => {
    event.preventDefault();
    submitAuthForm(event.currentTarget, '/api/auth/register', {
      name: document.getElementById('name').value.trim(),
      email: document.getElementById('email').value.trim(),
      phone: document.getElementById('phone').value.trim() || null,
      password: document.getElementById('password').value,
      language_pref: document.getElementById('language_pref').value,
    });
  });
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/static/service-worker.js').catch(() => {});
  }
});
