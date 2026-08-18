// A conversation belongs to the signed-in account, not to the current page.
// Keeping this stable ensures returning from a scheme or service restores it.
const currentSessionId = 'default';
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
  let res;
  try {
    res = await apiFetch('/api/chat/message', {
      method: 'POST', body: JSON.stringify({ message: text, session_id: currentSessionId, language: currentLang }),
    });
  } catch (_) {
    appendMessage('bot', 'Unable to reach the server. Please check your connection and try again.');
    return;
  }
  if (!res || !res.ok) {
    let message = 'Something went wrong. Please try again.';
    try { message = (await res.json()).detail || message; } catch (_) { /* Keep the safe fallback. */ }
    appendMessage('bot', message);
    return;
  }
  const data = await res.json();
  appendMessage('bot', data.response);
  if (autoSpeak) speakText(data.response, currentLang);
  if (data.redirect_url) {
    const link = document.createElement('a');
    link.className = 'btn btn-primary';
    link.style.marginTop = '8px';
    link.href = data.redirect_url;
    link.textContent = data.redirect_label || 'Open page';
    document.getElementById('chatMessages').appendChild(link);
    window.setTimeout(() => { window.location.href = data.redirect_url; }, 900);
  }
  loadUnreadCount();
}

document.addEventListener('DOMContentLoaded', () => {
  currentLang = localStorage.getItem('csn_chat_language') || 'en';
  document.getElementById('langSelect').value = currentLang;
  document.getElementById('autoSpeakToggle').checked = autoSpeak;
  document.getElementById('voiceToggle').checked = voiceEnabled;
  setVoiceEnabled(voiceEnabled);
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
    localStorage.setItem('csn_chat_language', currentLang);
  });

  document.getElementById('voiceToggle')?.addEventListener('change', (e) => {
    setVoiceEnabled(e.target.checked);
  });

  document.querySelectorAll('.quick-actions button').forEach(btn => {
    btn.addEventListener('click', () => sendChatMessage(btn.dataset.query));
  });

  document.getElementById('clearChatBtn')?.addEventListener('click', async () => {
    await apiFetch(`/api/chat/history?session_id=${currentSessionId}`, { method: 'DELETE' });
    loadChatHistory();
  });
});
