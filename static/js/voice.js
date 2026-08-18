let recognition = null;
let isListening = false;
let recognitionHandler = null;
let voiceEnabled = localStorage.getItem('csn_voice_enabled') !== 'false';

function setVoiceEnabled(enabled) {
  voiceEnabled = enabled;
  localStorage.setItem('csn_voice_enabled', String(enabled));
  const mic = document.getElementById('micBtn');
  if (mic) { mic.disabled = !enabled; mic.setAttribute('aria-disabled', String(!enabled)); }
  if (!enabled && isListening) recognition?.stop();
}
function initSpeechRecognition(onResult) {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) return null;
  recognition = new SpeechRecognition();
  recognition.continuous = false; recognition.interimResults = false; recognition.maxAlternatives = 3;
  recognitionHandler = onResult;
  recognition.onresult = event => recognitionHandler?.(event.results[0][0].transcript.trim());
  recognition.onend = () => { isListening = false; document.getElementById('micBtn')?.classList.remove('listening'); };
  recognition.onerror = event => { isListening = false; document.getElementById('micBtn')?.classList.remove('listening'); if (event.error === 'language-not-supported') alert('Hindi voice recognition is not available in this browser. Try Chrome or use typed Hindi.'); };
  return recognition;
}
function toggleListening(onResult) {
  if (!voiceEnabled) return;
  if (!recognition) recognition = initSpeechRecognition(onResult);
  if (!recognition) { alert('Voice recognition is not supported in this browser.'); return; }
  recognitionHandler = onResult;
  const micBtn = document.getElementById('micBtn');
  if (isListening) { recognition.stop(); return; }
  recognition.lang = document.getElementById('langSelect')?.value === 'hi' ? 'hi-IN' : 'en-IN';
  try { recognition.start(); isListening = true; micBtn?.classList.add('listening'); } catch (_) { recognition.stop(); }
}
function speakText(text, lang = 'en') {
  if (!('speechSynthesis' in window)) return;
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = lang === 'hi' ? 'hi-IN' : 'en-IN'; utterance.rate = 0.95;
  window.speechSynthesis.speak(utterance);
}
function speakSteps(steps, lang = 'en') { speakText(steps.map((s, i) => `Step ${i + 1}: ${s.title}. ${s.description}`).join('. '), lang); }
