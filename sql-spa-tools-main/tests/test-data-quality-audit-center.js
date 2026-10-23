const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const html = fs.readFileSync(path.join(__dirname, '..', 'sql-spa-tools-data-quality-audit-center.html'), 'utf8');

// 模板輸出 sev-高／sev-中／sev-低，CSS 必須對應
assert.match(html, /\.sev-高\{[^}]*color:var\(--theme-danger\)/);
assert.match(html, /\.sev-中\{[^}]*color:var\(--theme-warning\)/);
assert.match(html, /\.sev-低\{[^}]*color:var\(--theme-muted\)/);
assert.doesNotMatch(html, /\.sev-\?/, 'severity selectors must not contain the mangled ? wildcard');
assert.match(html, /class="sev-高"/);

// 未定義的 --hi 會讓邊框整條失效
assert.doesNotMatch(html, /var\(--hi\)/, 'undefined tokens must not be used');
assert.match(html, /border-left:4px solid var\(--theme-danger\)/);

// 圖表顏色應在主題切換後重繪
assert.match(html, /addEventListener\('sql-spa-tools-theme-change'/);
assert.match(html, /V\[S\.view\]\(\)/);

console.log('Data Quality Audit contract passed: severity styles, theme tokens, theme redraw');
