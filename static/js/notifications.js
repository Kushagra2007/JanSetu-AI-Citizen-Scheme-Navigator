const ICONS = { new_scheme: '🎯', status_update: '🔄', deadline: '⏰', document_missing: '📄' };

function renderNotif(n) {
  return `
    <div class="card glass" style="opacity:${n.read ? 0.6 : 1};">
      <div style="display:flex;justify-content:space-between;">
        <h4>${ICONS[n.type] || '🔔'} ${n.title}</h4>
        <span style="font-size:0.75rem;color:var(--text-muted);">${new Date(n.created_at).toLocaleString()}</span>
      </div>
      <p style="color:var(--text-muted);margin:6px 0;">${n.message}</p>
      <div style="display:flex;gap:8px;">
        ${!n.read ? `<button class="btn btn-outline" style="padding:6px 12px;font-size:0.8rem;" onclick="markRead(${n.id})">Mark read</button>` : ''}
        <button class="btn btn-ghost" style="padding:6px 12px;font-size:0.8rem;" onclick="deleteNotif(${n.id})">Dismiss</button>
      </div>
    </div>`;
}

async function loadNotifications() {
  const res = await apiFetch('/api/notifications');
  if (!res || !res.ok) return;
  const notifs = await res.json();
  document.getElementById('notifList').innerHTML = notifs.map(renderNotif).join('') || '<p>No notifications yet.</p>';
}

async function markRead(id) { await apiFetch(`/api/notifications/${id}/read`, { method: 'PUT' }); loadNotifications(); loadUnreadCount(); }
async function deleteNotif(id) { await apiFetch(`/api/notifications/${id}`, { method: 'DELETE' }); loadNotifications(); loadUnreadCount(); }
async function markAllRead() { await apiFetch('/api/notifications/read-all', { method: 'PUT' }); loadNotifications(); loadUnreadCount(); }

async function requestPushPermission() {
  if (!('Notification' in window)) return;
  const perm = await Notification.requestPermission();
  if (perm === 'granted') new Notification('Citizen Service Navigator', { body: 'Notifications enabled!' });
}

document.addEventListener('DOMContentLoaded', () => {
  loadNotifications();
  document.getElementById('markAllBtn')?.addEventListener('click', markAllRead);
  document.getElementById('enablePushBtn')?.addEventListener('click', requestPushPermission);
});