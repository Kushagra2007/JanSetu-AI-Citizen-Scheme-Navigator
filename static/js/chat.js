let currentSessionId = localStorage.getItem('csn_session_id') || 'default';
let autoSpeak = localStorage.getItem('csn_autospeak') === 'true';
let currentLang = 'en';

function appendMessage(sender, text) {
  const container = document.getElementById('chatMessages');
  const div = document.createElement('div');
  div.className = `msg glass ${sender === 'user' ? 'msg-user' : 'msg-bot'}`;
  div.textContent = text;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

async function loadChatHistory() {
  const res = await apiFetch(`/api/chat/history?session_id=${currentSessionId}`);
  if (!res || !res.ok) return;
  const history = await res.json();
  const container = document.getElementById('chatMessages');
  container.innerHTML = '';
  if (history.length === 0) {
    appendMessage('bot', "Hi! I'm your Citizen Service Navigator. Tell me about yourself (age, income, state) or ask about a scheme/service.");
  }
  history.forEach(m => appendMessage(m.sender, m.message));
}

async function sendChatMessage(text) {
  if (!text.trim()) return;
  appendMessage('user', text);
  document.getElementById('chatInput').value = '';
  const res = await apiFetch('/api/chat/message', {
    method: 'POST', body: JSON.stringify({ message: text, session_id: currentSessionId }),
  });
  if (!res || !res.ok) { appendMessage('bot', 'Something went wrong. Please try again.'); return; }
  const data = await res.json();
  appendMessage('bot', data.response);
  if (autoSpeak) speakText(data.response, currentLang);
  loadUnreadCount();
}

document.addEventListener('DOMContentLoaded', () => {
  localStorage.setItem('csn_session_id', currentSessionId);
  loadChatHistory();

  const form = document.getElementById('chatForm');
  form?.addEventListener('submit', (e) => {
    e.preventDefault();
    const input = document.getElementById('chatInput');
    sendChatMessage(input.value);
  });

  document.getElementById('micBtn')?.addEventListener('click', () => {
    toggleListening((transcript) => { sendChatMessage(transcript); });
  });

  document.getElementById('autoSpeakToggle')?.addEventListener('change', (e) => {
    autoSpeak = e.target.checked;
    localStorage.setItem('csn_autospeak', autoSpeak);
  });

  document.getElementById('langSelect')?.addEventListener('change', (e) => {
    currentLang = e.target.value;
  });

  document.querySelectorAll('.quick-actions button').forEach(btn => {
    btn.addEventListener('click', () => sendChatMessage(btn.dataset.query));
  });

  document.getElementById('clearChatBtn')?.addEventListener('click', async () => {
    await apiFetch(`/api/chat/history?session_id=${currentSessionId}`, { method: 'DELETE' });
    loadChatHistory();
  });
});