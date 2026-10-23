const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const html = fs.readFileSync(path.join(__dirname, '..', 'sql-spa-tools-schema-studio.html'), 'utf8');

assert.match(html, /<title>SQL SPA Tools｜SQL 欄位映射<\/title>/);
assert.equal((html.match(/<h1>/g) || []).length, 1, 'page must expose exactly one main heading');
assert.match(html, /<h1>SQL SPA Tools｜SQL 欄位映射<\/h1>/);
assert.match(html, /\.brand h1\{[^}]*margin:0/);

// 編輯目標欄位必須寫回 state，不可寫入 effectiveState() 的深拷貝
const editColumn = html.match(/function editColumn\(side, id\) \{[\s\S]*?\n  \}/);
assert.ok(editColumn, 'editColumn must exist');
assert.match(editColumn[0], /state\.targetColumns\)\.find/, 'target column editing must read the live state');
assert.doesNotMatch(editColumn[0], /effectiveState\(state\)\.targetColumns/, 'editing a deep clone silently discards the change');

// 預設淺色模式：欄位名稱與摘要不可使用固定淺灰
assert.match(html, /\.field-label\{[^}]*color:var\(--theme-text\)/);
assert.match(html, /\.mapping-summary\{[^}]*color:var\(--theme-muted\)/);
assert.match(html, /\.field-row\.mapped\{[^}]*background:var\(--theme-surface-soft\)/);
assert.ok(!html.includes('color:#dddddd'), 'field labels must not keep the dark-only #dddddd colour');
assert.ok(!html.includes('.field-row.mapped{background:#1a1a1a}'), 'mapped rows must not keep the dark-only background');

// 主題橋接區塊不得重複貼上
assert.equal(
  html.split('body{background:var(--theme-page);color:var(--theme-text);font-family:var(--theme-font-sans)}').length - 1,
  1,
  'theme bridge block must not be duplicated',
);

console.log('Schema Studio contract passed: heading, target-column editing, light-theme tokens');
