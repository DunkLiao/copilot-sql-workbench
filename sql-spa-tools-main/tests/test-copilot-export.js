const assert = require('node:assert/strict');
const CopilotExport = require('../sql-spa-tools-copilot-export.js');

const rows = [{
  targetObject: 'DEMO_MONTHLY_REPORT',
  targetField: 'SEGMENT_LABEL',
  sourceObject: 'DEMO_CUSTOMER',
  sourceField: 'CUSTOMER_SEGMENT',
  relation: '間接',
  transform: 'SQL 運算式不得輸出',
  expression: 'RAW SQL SECRET_VALUE',
  file: 'D:\\private\\customer.sql',
}, {
  targetObject: 'DEMO_MONTHLY_REPORT',
  targetField: 'CUSTOMER_ID',
  sourceObject: 'DEMO_CUSTOMER',
  sourceField: 'CUSTOMER_ID',
  relation: '直接',
  transform: '直接對應',
  expression: 'CUSTOMER_ID',
}];
const model = {
  messageList: [
    { level: 'warn', text: '解析警告含有 SECRET_VALUE', file: 'D:\\private\\customer.sql' },
    { level: 'error', text: '解析錯誤含有 RAW SQL SECRET_VALUE', file: 'D:\\private\\customer.sql' },
  ],
};

const changeContext = {
  object: 'DEMO_CUSTOMER',
  column: 'CUSTOMER_SEGMENT',
  changeType: 'definition_changed',
  before: 'VARCHAR2(20)',
  after: 'VARCHAR2(40)',
};
const summary = CopilotExport.buildSummary(rows, model, '2026-10-23T00:00:00.000Z', changeContext);
assert.deepEqual(summary, {
  schemaVersion: '1.0',
  generatedAt: '2026-10-23T00:00:00.000Z',
  source: 'SQL SPA Tools column lineage',
  changeSummary: '操作者輸入之變更背景（本工具未驗證 SQL 版本差異）',
  changes: [{
    object: 'DEMO_CUSTOMER',
    column: 'CUSTOMER_SEGMENT',
    changeType: 'definition_changed',
    before: 'VARCHAR2(20)',
    after: 'VARCHAR2(40)',
    origin: 'operator_entered',
    verification: 'not_verified_by_tool',
  }],
  impacts: [{
    object: 'DEMO_MONTHLY_REPORT',
    column: 'SEGMENT_LABEL',
    relationship: '間接',
    evidence: 'DEMO_CUSTOMER.CUSTOMER_SEGMENT → DEMO_MONTHLY_REPORT.SEGMENT_LABEL',
  }],
  analysisMessages: [
    { level: 'warn', count: 1 },
    { level: 'error', count: 1 },
  ],
  limitations: [
    '僅分析目前載入且可靜態解析的 SQL；未載入物件、動態 SQL 與執行期行為不在涵蓋範圍。',
    '訊息僅提供警告與錯誤數量；詳細內容請回到 SQL SPA Tools 本機檢視。',
    '此摘要不是 SQL 版本差異，也不是變更核准或正確性保證。',
    'impacts 僅列出來源欄位符合操作者輸入 changes 的關係；其他欄位關係不在此清單。',
  ],
});

const serialized = JSON.stringify(summary);
for (const forbidden of ['SECRET_VALUE', 'RAW SQL', 'customer.sql', 'D:\\private']) {
  assert.equal(serialized.includes(forbidden), false, `Copilot summary must exclude ${forbidden}`);
}
const emptySummary = CopilotExport.buildSummary([], { messageList: [] }, 'fixed');
assert.deepEqual(emptySummary.analysisMessages, []);
assert.deepEqual(emptySummary.changes, []);
assert.equal(
  CopilotExport.buildSummary(rows, model, 'fixed').impacts.length,
  2,
  'without change metadata, export all loaded lineage impacts',
);
assert.throws(
  () => CopilotExport.buildSummary([], { messageList: [] }, 'fixed', {
    object: 'DEMO_CUSTOMER',
    column: 'CUSTOMER_SEGMENT',
    before: 'VARCHAR2(20); DROP TABLE USERS',
    after: 'VARCHAR2(40)',
  }),
  /資料型別/,
);

console.log('Copilot export contract passed: allowlisted lineage summary, warning counts, and no SQL or paths');
