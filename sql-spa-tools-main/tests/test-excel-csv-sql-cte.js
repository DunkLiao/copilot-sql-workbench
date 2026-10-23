const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const htmlPath = path.join(__dirname, '..', 'sql-spa-tools-excel-csv-sql-cte.html');
const source = fs.readFileSync(htmlPath, 'utf8');
const script = [...source.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi)]
  .map(match => match[1])
  .find(content => content.includes('ExcelCsvSqlCteCore'));

assert.ok(script, 'CTE page must expose ExcelCsvSqlCteCore for deterministic tests');
const context = { console, document: { getElementById() { return null; } }, TextDecoder, Blob, URL, navigator: {} };
context.globalThis = context;
vm.runInNewContext(script, context, { filename: htmlPath });
const core = context.ExcelCsvSqlCteCore;
assert.ok(core, 'ExcelCsvSqlCteCore should be available');
assert.equal(core.decodeFile(new TextEncoder().encode('id\n1'), 'auto').encoding, 'UTF-8');
assert.equal(core.decodeFile(Uint8Array.from([0xef, 0xbb, 0xbf, 0x69, 0x64]), 'auto').encoding, 'UTF-8 BOM');

assert.deepEqual(JSON.parse(JSON.stringify(core.parseDelimited('id,name,note\n1,"Alice, A.","line 1\nline 2"'))), [
  ['id', 'name', 'note'], ['1', 'Alice, A.', 'line 1\nline 2'],
]);
assert.equal(core.decodeBytes(Uint8Array.from([0xff, 0xfe, 0x69, 0, 0x64, 0, 10, 0]), 'auto'), 'id\n');
assert.deepEqual(JSON.parse(JSON.stringify(core.resolveColumnNames([
  { originalName: 'Order Date' }, { originalName: 'Order Date' }, { originalName: '??', customName: '  ' },
], true))), ['Order_Date', 'Order_Date_1', 'col_3']);
assert.deepEqual(JSON.parse(JSON.stringify(core.findDuplicateCustomNames([
  { customName: 'user id' }, { customName: 'user-id' }, { customName: 'other' },
]))), [0, 1]);
assert.equal(core.inferColumnType(['1990-01-02', 'NULL', '2000-06-15', '1975-03-08']), 'DATE');

const rows = [['1', "O'Brien"], ['2', 'Alice']];
const columns = [
  { originalName: 'User ID', inferredType: 'INTEGER', overrideType: '' },
  { originalName: 'Full Name', inferredType: 'TEXT', overrideType: '' },
];
const sqlite = core.generateCteSql({ rows, columns, dialect: 'sqlite', cteName: 'cte_data', chunkSize: 1 });
assert.match(sqlite, /WITH\s+cte_data_part_1\s*\("User_ID", "Full_Name"\) AS \(\s*VALUES/i);
assert.match(sqlite, /CAST\(1 AS INTEGER\)/i);
assert.match(sqlite, /'O''Brien'/);
assert.match(sqlite, /UNION ALL[\s\S]*SELECT \* FROM cte_data_part_2/);
assert.match(sqlite, /SELECT \* FROM cte_data;/);

const sqlServer = core.generateCteSql({ rows, columns, dialect: 'mssql', cteName: 'cte_data', chunkSize: 1000 });
assert.match(sqlServer, /\[User_ID\]/);
assert.match(sqlServer, /WITH\s+cte_data_part_1\s*\(\[User_ID\], \[Full_Name\]\) AS/i);
assert.match(sqlServer, /AS \(\s*SELECT[\s\S]*FROM \(VALUES[\s\S]*\) AS \[cte_values\]/);
assert.match(core.generateCteSql({ rows: [['1', '王小明']], columns: [{ originalName: 'id', inferredType: 'INTEGER' }, { originalName: 'name', inferredType: 'TEXT' }], dialect: 'mssql' }), /N'王小明'/);
assert.equal(core.normalizeChunkSize('mssql', 5000), 1000);
assert.equal(core.normalizeChunkSize('sqlite', 8000), 1000);
assert.equal(core.dialectType('INTEGER', 'mysql'), 'SIGNED');
assert.equal(core.dialectType('TIMESTAMP', 'mysql'), 'DATETIME');
assert.equal(core.dialectType('TIMESTAMP', 'mssql'), 'DATETIME2');

const oracle = core.generateCteSql({
  rows: [['1990-01-02', '2026-10-09 15:45:10'], ['2000-06-15', 'NULL']],
  columns: [{ originalName: 'Birthday', inferredType: 'DATE' }, { originalName: 'Updated At', inferredType: 'TIMESTAMP' }],
  dialect: 'oracle', cteName: 'cte_data', chunkSize: 1000,
});
assert.match(oracle, /FROM dual/);
assert.match(oracle, /TO_DATE\('1990-01-02', 'YYYY-MM-DD'\)/);
assert.match(oracle, /TO_TIMESTAMP\('2026-10-09 15:45:10', 'YYYY-MM-DD HH24:MI:SS'\)/);

const bigQuery = core.generateCteSql({ rows, columns, dialect: 'bigquery', cteName: 'cte_data', chunkSize: 1000 });
assert.match(bigQuery, /SELECT CAST\(1 AS INT64\) AS `User_ID`/);
assert.match(bigQuery, /UNION ALL/);

const largeSql = core.generateCteSql({
  rows: Array.from({ length: 100000 }, (_, index) => [String(index + 1)]),
  columns: [{ originalName: 'id', inferredType: 'INTEGER', overrideType: '' }],
  dialect: 'sqlite', cteName: 'large_data', chunkSize: 1000,
});
assert.match(largeSql, /large_data_part_100/);
assert.match(largeSql, /\(100000\)/);
assert.ok(largeSql.length > 1_000_000);

console.log('Excel/CSV to SQL CTE core behavior passed');
