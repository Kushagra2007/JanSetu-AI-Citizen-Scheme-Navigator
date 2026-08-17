(function () {
  const root = document.documentElement;
  const saved = localStorage.getItem('csn_theme') || 'light';
  root.setAttribute('data-theme', saved);

  window.toggleTheme = function () {
    const current = root.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    localStorage.setItem('csn_theme', next);
    const btn = document.getElementById('themeToggleBtn');
    if (btn) btn.textContent = next === 'dark' ? '☀️' : '🌙';
  };

  document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('themeToggleBtn');
    if (btn) btn.textContent = saved === 'dark' ? '☀️' : '🌙';
  });
})();