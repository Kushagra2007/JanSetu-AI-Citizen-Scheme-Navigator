let recognition = null;
let isListening = false;

function initSpeechRecognition(onResult) {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    alert('Speech recognition is not supported in this browser.');
    return null;
  }
  recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = false;
  recognition.lang = document.getElementById('langSelect')?.value === 'hi' ? 'hi-IN' : 'en-IN';

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    onResult(transcript);
  };
  recognition.onend = () => {
    isListening = false;
    document.getElementById('micBtn')?.classList.remove('listening');
  };
  recognition.onerror = () => {
    isListening = false;
    document.getElementById('micBtn')?.classList.remove('listening');
  };
  return recognition;
}

function toggleListening(onResult) {
  if (!recognition) recognition = initSpeechRecognition(onResult);
  if (!recognition) return;
  const micBtn = document.getElementById('micBtn');
  if (isListening) {
    recognition.stop();
    isListening = false;
    micBtn?.classList.remove('listening');
  } else {
    recognition.lang = document.getElementById('langSelect')?.value === 'hi' ? 'hi-IN' : 'en-IN';
    recognition.start();
    isListening = true;
    micBtn?.classList.add('listening');
  }
}

function speakText(text, lang = 'en') {
  if (!('speechSynthesis' in window)) return;
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = lang === 'hi' ? 'hi-IN' : 'en-IN';
  utterance.rate = 0.95;
  window.speechSynthesis.speak(utterance);
}

function speakSteps(steps, lang = 'en') {
  const text = steps.map((s, i) => `Step ${i + 1}: ${s.title}. ${s.description}`).join('. ');
  speakText(text, lang);
}