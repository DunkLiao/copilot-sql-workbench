const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const htmlPath = path.join(__dirname, '..', 'sql-spa-tools-excel-csv-sql.html');
const source = fs.readFileSync(htmlPath, 'utf8');
const script = [...source.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi)]
  .map(match => match[1])
  .find(content => content.includes('ExcelCsvSqlCore'));

assert.ok(script, 'page must expose ExcelCsvSqlCore for deterministic tests');
assert.match(source, /id="enableCustomHeaders"[^>]+type="checkbox"/, 'custom headers should require explicit opt-in');
assert.doesNotMatch(source, /id="enableCustomHeaders"[^>]+checked/, 'custom headers should be disabled by default');
assert.match(source, /id="applyCustomHeadersBtn"/, 'custom header mode should provide an explicit apply action');
assert.match(source, /\$\('applyCustomHeadersBtn'\)\.addEventListener\('click'/, 'custom header apply action should rebuild the model');

const context = {
  console,
  document: {
    addEventListener() {},
    getElementById() { return null; },
  },
  window: {},
  URL,
  Blob,
  navigator: {},
  TextDecoder,
};
context.globalThis = context;
vm.runInNewContext(script, context, { filename: htmlPath });
const core = context.ExcelCsvSqlCore;
assert.ok(core, 'ExcelCsvSqlCore should be available');

assert.equal(core.decodeBytes(Uint8Array.from([0xA4, 0xA4, 0xA4, 0xE5, 0x2C, 0x31]), 'big5'), '中文,1');
assert.equal(core.decodeBytes(Uint8Array.from([0xA4, 0xA4, 0xA4, 0xE5, 0x2C, 0x31]), 'auto'), '中文,1');
assert.equal(core.decodeBytes(Uint8Array.from([0xFF, 0xFE, 0x69, 0x00, 0x64, 0x00, 0x0A, 0x00, 0x31, 0x00]), 'auto'), 'id\n1');
assert.equal(core.looksLikeDataRow(['1001', '高雄', '001001', '88.5']), true);

const parsed = core.parseDelimited('id,name,note\n1,"Alice, A.","line 1\nline 2"');
assert.deepEqual(JSON.parse(JSON.stringify(parsed)), [
  ['id', 'name', 'note'],
  ['1', 'Alice, A.', 'line 1\nline 2'],
]);

assert.deepEqual(JSON.parse(JSON.stringify(core.sanitizeHeaders([' Order Date ', 'Order Date', '', '0123']))), [
  'order_date', 'order_date_1', 'column_3', '0123',
]);

assert.equal(core.inferColumnType(['00123', '00456']), 'VARCHAR(50)');
assert.equal(core.inferColumnType(['2147483648']), 'BIGINT');
assert.equal(core.inferColumnType(['12.50', '3.125']), 'DECIMAL(5, 3)');
assert.equal(core.inferColumnType(['2026-01-01', '2026-02-03']), 'DATE');
assert.equal(core.inferColumnType(['true', 'N']), 'BOOLEAN');

const model = core.buildModel(
  [['ID', 'Name', 'Amount'], ['1', "O'Brien", '12.50'], ['2', 'NULL', '3.00']],
  { hasHeader: true, dialect: 'mysql', tableName: 'orders', batchSize: 1, wrapTransaction: true },
);
const sql = core.generateSql(model, 'mysql', { includeDDL: true });
assert.match(sql.dml, /INSERT INTO `orders`/);
assert.match(sql.dml, /'O''Brien'/);
assert.match(sql.dml, /NULL/);
assert.match(sql.ddl, /CREATE TABLE/);
assert.equal(sql.batchCount, 2);

const oracle = core.generateSql(model, 'oracle', { includeDDL: false });
assert.match(oracle.dml, /INSERT ALL/);

const noHeader = core.buildModel(
  [['1001', '高雄', '001001', '88.5'], ['1002', '臺中', '000045', '76.25']],
  { headerMode: 'auto' },
);
assert.deepEqual(JSON.parse(JSON.stringify(noHeader.columns.map(column => column.name))), ['column_1', 'column_2', 'column_3', 'column_4']);
assert.equal(noHeader.rows.length, 2);

const customHeader = core.buildModel(
  [['1001', '高雄', '001001', '88.5']],
  { headerMode: 'custom', customHeaders: ['member_id', 'city', 'postal_code', 'score'] },
);
assert.deepEqual(JSON.parse(JSON.stringify(customHeader.columns.map(column => column.name))), ['member_id', 'city', 'postal_code', 'score']);
assert.throws(() => core.buildModel([['1', '2']], { headerMode: 'custom', customHeaders: ['only_one'] }), /欄位名稱數量/);

const mssql = core.generateSql(model, 'mssql', { includeDDL: true, ifNotExists: true, dropTable: true });
assert.match(mssql.ddl, /IF OBJECT_ID\(N'orders', N'U'\) IS NOT NULL DROP TABLE/);
assert.match(mssql.ddl, /IF OBJECT_ID\(N'orders', N'U'\) IS NULL BEGIN/);

console.log('Excel/CSV to SQL core behavior passed');
