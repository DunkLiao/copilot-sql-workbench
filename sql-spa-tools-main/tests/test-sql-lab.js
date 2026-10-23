const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const htmlPath = path.join(__dirname, '..', 'sql-spa-tools-sql-lab.html');
const html = fs.readFileSync(htmlPath, 'utf8');

// 切換工作區時，草稿必須寫回它原本的工作區
assert.match(html, /saveEditor: debounce\(\(text, wsId\) => Store\.setSetting\('editor:' \+ \(wsId \|\| App\.ws\.id\), text\), 600\)/);
assert.match(html, /App\.saveEditor\(v, App\.ws\.id\)/);
assert.match(html, /App\.saveEditor\(App\.editorText, App\.ws\.id\)/);
assert.match(html, /App\.saveEditor\(text, App\.ws\.id\)/);
assert.match(html, /this\.saveEditor\.cancel\(\)/);
assert.match(html, /await Store\.setSetting\('editor:' \+ this\.ws\.id, this\.editorText\)/);
assert.match(html, /if \(!eng\)[\s\S]{0,200}renderHeader\(\); return;/);
assert.doesNotMatch(html, /aria-pressed/);

// MiniSQL 的敘述拆分（SQLite 引擎模式也使用它）
const engine = html.match(/<script>(\/\* ===================== MiniSQL[\s\S]*?)<\/script>/);
assert.ok(engine, 'MiniSQL engine script must exist');
const context = {
  module: { exports: {} },
  console,
  performance,
  TextDecoder,
  TextEncoder,
  Blob,
  URL,
  navigator: {},
};
vm.runInNewContext(engine[1], context);
const MiniSQL = context.module.exports;
assert.ok(MiniSQL && typeof MiniSQL.splitStatements === 'function');

assert.deepEqual(
  Array.from(MiniSQL.splitStatements("SELECT ';' AS semi; SELECT 2;")),
  ["SELECT ';' AS semi", 'SELECT 2'],
);
assert.deepEqual(
  Array.from(MiniSQL.splitStatements("SELECT 'O''Brien' AS name; -- tail\nSELECT 1;")),
  ["SELECT 'O''Brien' AS name", '-- tail\nSELECT 1'],
);
assert.deepEqual(
  Array.from(MiniSQL.splitStatements('CREATE TRIGGER t AFTER INSERT ON x BEGIN UPDATE x SET a = 1; END; SELECT 1;')),
  ['CREATE TRIGGER t AFTER INSERT ON x BEGIN UPDATE x SET a = 1; END', 'SELECT 1'],
);

console.log('SQL Lab contract passed: workspace draft isolation, renderHeader fallback, statement splitting');
