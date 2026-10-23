const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const source = fs.readFileSync(require('node:path').join(__dirname, '..', 'theme.js'), 'utf8');
const root = require('node:path').join(__dirname, '..');
const stylesheet = fs.readFileSync(require('node:path').join(root, 'theme.css'), 'utf8');

for (const token of [
  '--theme-page: #f6f6f6', '--theme-surface: #ffffff', '--theme-text: #303030',
  '--theme-primary: #444444', '--theme-primary-hover: #2e2e2e',
  '--theme-success: #505050', '--theme-success-soft: #e6e6e6',
  '--theme-warning: #5c5c5c', '--theme-warning-soft: #dddddd',
  '--theme-danger: #333333', '--theme-danger-soft: #cecece',
  '--theme-info: #595959', '--theme-info-soft: #eeeeee',
]) {
  assert.ok(stylesheet.includes(token), `Missing ink theme value: ${token}`);
}
for (const [, color] of stylesheet.matchAll(/--theme-[\w-]+:\s*(#[0-9a-f]{6})/gi)) {
  assert.equal(new Set([color.slice(1, 3), color.slice(3, 5), color.slice(5, 7)]).size, 1, `Theme token ${color} must be grayscale`);
}
assert.match(stylesheet, /:root\[data-theme='dark'\]\s*\{[^}]*--theme-page:\s*#202020/s);
assert.match(stylesheet, /:root\[data-theme='dark'\]\s*\{[^}]*--theme-primary:\s*#5a5a5a/s);
assert.match(stylesheet, /:root\[data-theme='dark'\]\s*\{[^}]*--m-id:\s*#3d3d3d/s, 'dark mode must remap --m-* highlight surfaces');
for (const [selector, token] of [
  ['.l-使用中', '--theme-success-soft'], ['.l-草稿', '--theme-warning-soft'],
  ['.t-待處理', '--theme-warning-soft'], ['.modal .mh', '--theme-surface-alt'],
  ['.message.warn', '--theme-warning'], ['.fi.sel', '--theme-surface-soft'],
  ['.toast.error', '--theme-danger-soft'],
]) {
  const escaped = selector.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  assert.match(stylesheet, new RegExp(`${escaped}[^}]*\\{[^}]*var\\(${token}\\)`, 's'), `Missing themed override for ${selector}`);
}

for (const file of ['theme.css', ...fs.readdirSync(root).filter(name => name.endsWith('.html'))]) {
  const content = fs.readFileSync(require('node:path').join(root, file), 'utf8');
  for (const [, color] of content.matchAll(/#([0-9a-f]{3,4}|[0-9a-f]{6}|[0-9a-f]{8})\b/gi)) {
    const channels = color.length <= 4
      ? [...color.slice(0, 3)]
      : [color.slice(0, 2), color.slice(2, 4), color.slice(4, 6)];
    assert.equal(new Set(channels).size, 1, `${file} contains non-gray color #${color}`);
  }
  if (file.endsWith('.html')) {
    const head = content.slice(0, content.indexOf('</head>'));
    assert.ok(head.includes('<script src="theme.js"></script>'), `${file} must load theme.js in <head> so the saved theme applies before first paint`);
    assert.doesNotMatch(content, /id="themeToggle"[^>]*aria-pressed/, `${file} must not mark the theme toggle as pressed while its label describes the action`);
  }
}

function makeButton() {
  const listeners = {};
  return {
    textContent: '',
    title: '',
    attrs: {},
    setAttribute(name, value) { this.attrs[name] = value; },
    addEventListener(name, callback) { listeners[name] = callback; },
    click() { listeners.click?.(); },
  };
}

function runTheme(saved, buttonInitiallyPresent = true, brokenStorage = false) {
  const store = new Map(saved == null ? [] : [['sql_spa_tools_theme', saved]]);
  const documentListeners = {};
  const windowListeners = {};
  const emittedEvents = [];
  let button = buttonInitiallyPresent ? makeButton() : null;
  const context = {
    document: {
      documentElement: { dataset: {} },
      getElementById() { return button; },
      addEventListener(name, callback) { documentListeners[name] = callback; },
    },
    window: {
      addEventListener(name, callback) { windowListeners[name] = callback; },
      dispatchEvent(event) { emittedEvents.push(event); },
    },
    CustomEvent: function CustomEvent(name, options) { this.type = name; Object.assign(this, options); },
    localStorage: brokenStorage ? {
      getItem() { throw new Error('SecurityError: storage blocked'); },
      setItem() { throw new Error('SecurityError: storage blocked'); },
    } : {
      getItem(key) { return store.get(key) ?? null; },
      setItem(key, value) { store.set(key, value); },
    },
  };
  vm.runInNewContext(source, context);
  return {
    context,
    store,
    documentListeners,
    windowListeners,
    emittedEvents,
    get button() { return button; },
    addButton() { button = makeButton(); return button; },
    click() {
      if (typeof documentListeners.click === 'function') {
        documentListeners.click({ target: { closest: selector => selector === '#themeToggle' ? button : null } });
      } else {
        button.click();
      }
    },
    changeFromAnotherTab(theme) {
      assert.equal(typeof windowListeners.storage, 'function', 'theme listens for cross-tab storage changes');
      windowListeners.storage({ key: 'sql_spa_tools_theme', newValue: theme });
    },
  };
}

const first = runTheme(null);
assert.equal(first.context.document.documentElement.dataset.theme, 'light');
first.click();
assert.equal(first.context.document.documentElement.dataset.theme, 'dark');
assert.equal(first.button.textContent, '☀️ 淺色模式');

const restored = runTheme('dark');
assert.equal(restored.context.document.documentElement.dataset.theme, 'dark');
restored.click();
assert.equal(restored.context.document.documentElement.dataset.theme, 'light');
assert.equal(restored.button.textContent, '🌙 深色模式');

const lateButton = runTheme(null, false);
lateButton.addButton();
assert.equal(typeof lateButton.documentListeners?.click, 'function');
assert.equal(typeof lateButton.documentListeners?.DOMContentLoaded, 'function', 'theme renders buttons created before DOMContentLoaded');
lateButton.documentListeners.DOMContentLoaded();
assert.equal(lateButton.button.textContent, '🌙 深色模式');
lateButton.click();
assert.equal(lateButton.context.document.documentElement.dataset.theme, 'dark');
assert.equal(lateButton.store.get('sql_spa_tools_theme'), 'dark');

const otherTab = runTheme('light');
otherTab.changeFromAnotherTab('dark');
assert.equal(otherTab.context.document.documentElement.dataset.theme, 'dark');
assert.equal(otherTab.button.attrs['aria-pressed'], undefined, 'aria-pressed must not contradict the action label');
assert.ok(otherTab.emittedEvents.some(event => event.type === 'sql-spa-tools-theme-change' && event.detail.theme === 'dark'));

// 私密瀏覽／封鎖網站資料時 localStorage 會丟錯，主題仍必須可切換
const blocked = runTheme('dark', true, true);
assert.equal(blocked.context.document.documentElement.dataset.theme, 'light');
blocked.click();
assert.equal(blocked.context.document.documentElement.dataset.theme, 'dark');
assert.equal(blocked.button.textContent, '☀️ 淺色模式');
assert.doesNotMatch(source, /setAttribute\('aria-pressed'/);

const sqlLabSource = fs.readFileSync(require('node:path').join(root, 'sql-spa-tools-sql-lab.html'), 'utf8');
assert.match(sqlLabSource, /addEventListener\('sql-spa-tools-theme-change'/);
assert.match(sqlLabSource, /savePrefs\(\)\s*\{\s*this\.settings\.theme\s*=\s*window\.SQLSpaToolsTheme\.getTheme\(\)/);
assert.match(sqlLabSource, /SQLSpaToolsTheme\.setTheme\(e\.target\.value\)/);

console.log('Theme behavior passed: default light, toggle, persistence, late button, cross-tab sync, blocked storage');
