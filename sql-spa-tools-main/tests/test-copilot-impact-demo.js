const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const CopilotExport = require('../sql-spa-tools-copilot-export.js');

const root = path.join(__dirname, '..');
const fixtureDir = path.join(root, 'uat-fixtures', 'copilot-impact-demo');
const expected = JSON.parse(fs.readFileSync(path.join(fixtureDir, 'expected.json'), 'utf8'));
const beforeSql = fs.readFileSync(path.join(fixtureDir, 'customer-before.sql'), 'utf8');
const afterSql = fs.readFileSync(path.join(fixtureDir, 'customer-after.sql'), 'utf8');
const downstreamSql = fs.readFileSync(path.join(fixtureDir, 'downstream.sql'), 'utf8');
const warningSql = fs.readFileSync(path.join(fixtureDir, 'parser-warning.sql'), 'utf8');
assert.match(beforeSql, /CUSTOMER_SEGMENT\s+VARCHAR2\(20\)/i);
assert.match(afterSql, /CUSTOMER_SEGMENT\s+VARCHAR2\(40\)/i);
assert.equal(beforeSql.replace('VARCHAR2(20)', 'VARCHAR2(40)'), afterSql);

const html = fs.readFileSync(path.join(root, 'sql-spa-tools-column-lineage.html'), 'utf8').replace(/\r\n/g, '\n');
const marker = "'use strict';\n(() => {\n";
const start = html.indexOf(marker);
const end = html.indexOf('// UI events', start);
assert.ok(start >= 0 && end > start, 'column lineage analyzer harness markers must exist');
const analyzerSource = html.slice(start + marker.length, end);
const context = {};
vm.runInNewContext(
  `(() => { ${analyzerSource}\n` +
    'globalThis.__demoApi = { Analyzer, state, buildCopilotRows };\n})();',
  context,
  { filename: 'sql-spa-tools-column-lineage.html' },
);

const api = context.__demoApi;
api.state.model = new api.Analyzer([{ name: 'downstream.sql', text: downstreamSql }]).analyze();
const actualImpacts = api.buildCopilotRows()
  .filter(row => row.sourceObject === 'DEMO_CUSTOMER' && row.sourceField === 'CUSTOMER_SEGMENT')
  .map(row => ({
    object: row.targetObject,
    column: row.targetField,
    relationship: row.relation,
    evidence: `${row.sourceObject}.${row.sourceField} → ${row.targetObject}.${row.targetField}`,
  }))
  .sort((a, b) => a.object.localeCompare(b.object));

assert.deepEqual(JSON.parse(JSON.stringify(actualImpacts)), expected.expectedImpacts);
const copilotImpacts = CopilotExport.buildSummary(
  api.buildCopilotRows(),
  api.state.model,
  '2026-10-23T00:00:00.000Z',
  expected.changedField,
).impacts
  .map(impact => ({
    object: impact.object,
    column: impact.column,
    relationship: impact.relationship,
    evidence: impact.evidence,
  }))
  .sort((a, b) => a.object.localeCompare(b.object));
assert.deepEqual(JSON.parse(JSON.stringify(copilotImpacts)), expected.expectedImpacts);
const copilotSummary = CopilotExport.buildSummary(
  api.buildCopilotRows(),
  api.state.model,
  '2026-10-23T00:00:00.000Z',
  expected.changedField,
);
assert.deepEqual(
  JSON.parse(JSON.stringify(copilotSummary.changes)),
  [{
    ...expected.changedField,
    origin: 'operator_entered',
    verification: 'not_verified_by_tool',
  }],
);
assert.match(copilotSummary.changeSummary, /操作者輸入/);
assert.deepEqual(
  JSON.parse(JSON.stringify(api.state.model.messageList.filter(message => message.level === 'error'))),
  [],
);

const warningModel = new api.Analyzer([{ name: 'parser-warning.sql', text: warningSql }]).analyze();
api.state.model = warningModel;
const warningSummary = CopilotExport.buildSummary(api.buildCopilotRows(), warningModel, '2026-10-23T00:00:00.000Z');
assert.deepEqual(
  JSON.parse(JSON.stringify(warningSummary.analysisMessages)),
  [{ level: 'warn', count: 1 }],
);
assert.ok(warningSummary.limitations.some(text => text.includes('警告與錯誤數量')));

console.log('Copilot demo passed: expected impacts and parser warning are represented in the summary');
