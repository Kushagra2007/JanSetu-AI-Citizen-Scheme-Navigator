(function () {
  const root = document.documentElement;
  const saved = localStorage.getItem('csn_theme') || 'light';
  root.setAttribute('data-theme', saved);
  function updateButton(theme) {
    const btn = document.getElementById('themeToggleBtn');
    if (!btn) return;
    btn.innerHTML = `<span class="icon ${theme === 'dark' ? 'icon-sun' : 'icon-moon'}"></span>`;
  }
  window.toggleTheme = function () { const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark'; root.setAttribute('data-theme', next); localStorage.setItem('csn_theme', next); updateButton(next); };
  document.addEventListener('DOMContentLoaded', () => updateButton(saved));
})();
