(() => {
  const STORAGE_KEY = 'sql_spa_tools_theme';
  const THEME_EVENT = 'sql-spa-tools-theme-change';
  const root = document.documentElement;
  let storage = null;
  try {
    storage = typeof localStorage === 'undefined' ? null : localStorage;
  } catch (_) {
    storage = null;
  }
  const readTheme = () => {
    try {
      return storage ? storage.getItem(STORAGE_KEY) : null;
    } catch (_) {
      return null;
    }
  };
  const writeTheme = theme => {
    try {
      if (storage) storage.setItem(STORAGE_KEY, theme);
    } catch (_) {
      /* 私密瀏覽或封鎖網站資料時無法寫入，仍允許本次切換 */
    }
  };
  const initial = readTheme() === 'dark' ? 'dark' : 'light';
  root.dataset.theme = initial;

  const render = () => {
    const button = document.getElementById('themeToggle');
    if (!button) return;
    const isDark = root.dataset.theme === 'dark';
    button.textContent = isDark ? '☀️ 淺色模式' : '🌙 深色模式';
    button.title = isDark ? '切換至淺色模式' : '切換至深色模式';
  };

  const apply = theme => {
    const next = theme === 'dark' ? 'dark' : 'light';
    root.dataset.theme = next;
    render();
    window.dispatchEvent(new CustomEvent(THEME_EVENT, { detail: { theme: next } }));
  };
  const setTheme = theme => {
    const next = theme === 'dark' ? 'dark' : 'light';
    writeTheme(next);
    apply(next);
    return next;
  };

  render();
  // 有些頁面（例如 SQL Lab）在 DOMContentLoaded 後才建立主題按鈕，載入後再渲染一次。
  document.addEventListener('DOMContentLoaded', render);
  document.addEventListener('click', event => {
    if (!event.target?.closest?.('#themeToggle')) return;
    setTheme(root.dataset.theme === 'light' ? 'dark' : 'light');
  });
  window.addEventListener('storage', event => {
    if (event.key !== STORAGE_KEY && event.key !== null) return;
    apply(event.newValue);
  });
  window.SQLSpaToolsTheme = Object.freeze({
    getTheme: () => root.dataset.theme === 'dark' ? 'dark' : 'light',
    setTheme,
  });
})();
