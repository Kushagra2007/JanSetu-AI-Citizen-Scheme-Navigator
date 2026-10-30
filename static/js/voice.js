let isListening = false;
let mediaRecorder = null;
let mediaStream = null;
let audioChunks = [];
let speechRecognizer = null;
let voiceEnabled = localStorage.getItem('csn_voice_enabled') !== 'false';

function setVoiceEnabled(enabled) {
  voiceEnabled = enabled;
  localStorage.setItem('csn_voice_enabled', String(enabled));
  const mic = document.getElementById('micBtn');
  if (mic) {
    mic.disabled = !enabled;
    mic.setAttribute('aria-disabled', String(!enabled));
  }
  if (!enabled && isListening) stopListening();
}

function resetRecorder() {
  isListening = false;
  const micBtn = document.getElementById('micBtn');
  if (micBtn) micBtn.classList.remove('listening');
  if (speechRecognizer) {
    try { speechRecognizer.stop(); } catch (_) {}
    speechRecognizer = null;
  }
  if (mediaStream) {
    mediaStream.getTracks().forEach(track => track.stop());
    mediaStream = null;
  }
  mediaRecorder = null;
  audioChunks = [];
}

function stopListening() {
  if (speechRecognizer) {
    try { speechRecognizer.stop(); } catch (_) {}
  }
  if (mediaRecorder && mediaRecorder.state === 'recording') {
    mediaRecorder.stop();
  }
  resetRecorder();
}

async function toggleListening(onResult) {
  if (!voiceEnabled) {
    alert('Voice input is currently disabled. Toggle the voice input switch above to enable it.');
    return;
  }

  const micBtn = document.getElementById('micBtn');
  if (isListening) {
    stopListening();
    return;
  }

  const selectedLang = typeof currentLang !== 'undefined' ? currentLang : 'en';
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  // 1. Prefer native browser Web Speech API for instantaneous, keyless recognition
  if (SpeechRecognition) {
    try {
      speechRecognizer = new SpeechRecognition();
      speechRecognizer.lang = selectedLang === 'hi' ? 'hi-IN' : 'en-IN';
      speechRecognizer.continuous = false;
      speechRecognizer.interimResults = false;

      speechRecognizer.onstart = () => {
        isListening = true;
        micBtn?.classList.add('listening');
      };

      speechRecognizer.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        resetRecorder();
        if (transcript && transcript.trim()) {
          onResult(transcript.trim());
        }
      };

      speechRecognizer.onerror = (event) => {
        resetRecorder();
        // Fallback to server-side recorder if speech service fails
        if (event.error === 'not-allowed') {
          alert('Microphone permission is required for voice input.');
        } else if (event.error !== 'no-speech') {
          fallbackToServerRecording(selectedLang, onResult);
        }
      };

      speechRecognizer.onend = () => {
        resetRecorder();
      };

      speechRecognizer.start();
      return;
    } catch (_) {
      // Fall through to MediaRecorder fallback
    }
  }

  // 2. Server-side transcription fallback via MediaRecorder & /api/chat/transcribe
  fallbackToServerRecording(selectedLang, onResult);
}

async function fallbackToServerRecording(selectedLang, onResult) {
  const micBtn = document.getElementById('micBtn');
  if (!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder) {
    alert('Voice input is not supported in this browser.');
    return;
  }

  try {
    mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
      ? 'audio/webm;codecs=opus'
      : 'audio/webm';
    mediaRecorder = new MediaRecorder(mediaStream, { mimeType });
    audioChunks = [];

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size) audioChunks.push(event.data);
    };

    mediaRecorder.onstop = async () => {
      const blob = new Blob(audioChunks, { type: 'audio/webm' });
      resetRecorder();
      const formData = new FormData();
      formData.append('audio', blob, 'voice.webm');
      formData.append('language', selectedLang);

      try {
        const response = await fetch('/api/chat/transcribe', {
          method: 'POST',
          body: formData,
          credentials: 'same-origin',
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'Voice transcription failed.');
        if (data.transcript) onResult(data.transcript);
      } catch (error) {
        alert(error.message || 'Voice transcription failed.');
      }
    };

    mediaRecorder.start();
    isListening = true;
    micBtn?.classList.add('listening');

    // Auto-stop after 30 seconds
    window.setTimeout(() => {
      if (isListening) stopListening();
    }, 30000);
  } catch (_) {
    resetRecorder();
    alert('Microphone permission is required for voice input.');
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
  speakText(
    steps.map((s, i) => `Step ${i + 1}: ${s.title}. ${s.description}`).join('. '),
    lang
  );
}
