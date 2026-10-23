const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const htmlPath = path.join(__dirname, '..', 'sql-spa-tools-sqlscriptmanage.html');
const html = fs.readFileSync(htmlPath, 'utf8');
const match = html.match(/<script id="app-script">([\s\S]*?)<\/script>/);
assert.ok(match, 'SQLScriptManage core script must exist');

const context = { window: {}, console };
vm.runInNewContext(match[1], context);
const core = context.window.SQLScriptManage;
assert.ok(core, 'SQLScriptManage core API must be exposed for tests');
assert.match(html, /\.sm-editor\s*\{[^}]*min-height:\s*0/, 'editor area must be shrinkable so its action bar remains visible');
for (const color of ['#e9e9e9', '#e8e8e8', '#ebebeb']) {
  assert.ok(html.includes(color), `diff report theme color ${color} must be embedded`);
}
for (const id of [
  'projectInfoBtn', 'refreshBtn', 'editScriptBtn', 'duplicateScriptBtn',
  'saveDraftBtn', 'restoreDraftBtn', 'clearEditorBtn', 'versionInfoBtn',
  'rollbackVersionBtn', 'downloadVersionBtn', 'authorInput', 'scriptDialogTitle',
  'versionCompareBtn', 'compareDialog', 'baseVersionSelect', 'targetVersionSelect',
  'ignoreCaseInput', 'ignoreTrailingWhitespaceInput', 'ignoreBlankLinesInput',
  'compareRunBtn', 'sideBySideTab', 'unifiedTab', 'summaryTab',
  'copyUnifiedBtn', 'downloadDiffReportBtn'
]) {
  assert.match(html, new RegExp(`id="${id}"`), `UI control ${id} must exist`);
}

const project = core.createProject({ name: '使用者服務', description: '核心資料庫' });
const script = core.createScript(project.id, {
  name: 'V1_init.sql',
  description: '建立使用者表',
  tags: ['DDL'],
});
const rootVersion = core.createVersion(script, {
  versionNumber: '1.0.0',
  author: 'DBA',
  changeLog: '初始化',
  sqlContent: 'CREATE TABLE users (id INT);',
  parentId: null,
});
const branchVersion = core.createVersion(script, {
  versionNumber: '1.1.0-feature',
  changeLog: '加入索引',
  sqlContent: 'CREATE TABLE users (id INT);\nCREATE INDEX ix_users_id ON users(id);',
  parentId: rootVersion.id,
});

assert.equal(script.projectId, project.id);
assert.equal(branchVersion.parentId, rootVersion.id);
assert.equal(rootVersion.author, 'DBA');
const diff = core.compareLines('SELECT 1;\nFROM dual;\nOLD_LINE;', 'select 1;\nFROM dual;\nNEW_LINE;\nADDED;', { ignoreCase: true });
assert.equal(diff.stats.added, 1);
assert.equal(diff.stats.removed, 0);
assert.equal(diff.stats.changed, 1);
assert.ok(diff.rows.some(row => row.type === 'changed' && row.leftText === 'OLD_LINE;' && row.rightText === 'NEW_LINE;'));
assert.match(diff.unifiedText, /-OLD_LINE;/);
assert.match(diff.unifiedText, /\+NEW_LINE;/);
const whitespaceDiff = core.compareLines('SELECT 1;  \n\n', 'select 1;\n', { ignoreCase: true, ignoreTrailingWhitespace: true, ignoreBlankLines: true });
assert.equal(whitespaceDiff.stats.added + whitespaceDiff.stats.removed + whitespaceDiff.stats.changed, 0);
assert.equal(JSON.stringify(core.versionTree([rootVersion, branchVersion])), JSON.stringify([
  { version: rootVersion, children: [{ version: branchVersion, children: [] }] },
]));

const backup = core.createBackup({
  projects: [project],
  scripts: [script],
  versions: [rootVersion, branchVersion],
  app_settings: [{ id: 'settings', currentProjectId: project.id }],
});
assert.equal(core.validateBackup(backup).valid, true);
assert.equal(core.validateBackup({ schemaVersion: 1 }).valid, false);

const incoming = { ...backup, stores: { ...backup.stores, projects: [{ ...project, name: '更新後專案' }] } };
const merged = core.mergeBackup({
  current: { projects: [project], scripts: [], versions: [], app_settings: [] },
  incoming,
});
assert.equal(merged.projects[0].name, '更新後專案');
assert.equal(core.mergeBackup({ current: { projects: [project] }, incoming }).projects.length, 1);
assert.equal(core.normalizeImportMode('overwrite'), 'overwrite');
assert.equal(core.normalizeImportMode('invalid'), 'merge');

// 版本樹只能選取版本；直接 checkout 會改掉 activeVersionId 並清掉草稿
assert.equal(html.split("$('versionTree').addEventListener").length - 1, 1, 'version tree must have exactly one click handler');
assert.doesNotMatch(html, /\$\('versionTree'\)\.addEventListener\([^;]*checkoutVersion/, 'clicking a version must not silently check it out');
assert.equal(html.split("$('scriptList').addEventListener").length - 1, 1, 'script list must have exactly one click handler');

console.log('SQLScriptManage core contract passed: schema, versions, tree, backup, merge');
