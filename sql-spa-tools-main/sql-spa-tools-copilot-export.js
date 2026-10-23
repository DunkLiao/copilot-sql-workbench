(function (root) {
  'use strict';

  const LIMITATIONS = [
    '僅分析目前載入且可靜態解析的 SQL；未載入物件、動態 SQL 與執行期行為不在涵蓋範圍。',
    '訊息僅提供警告與錯誤數量；詳細內容請回到 SQL SPA Tools 本機檢視。',
    '此摘要不是 SQL 版本差異，也不是變更核准或正確性保證。',
  ];

  function normalizeChangeContext(context) {
    if (!context) return [];
    const values = {
      object: String(context.object || '').trim(),
      column: String(context.column || '').trim(),
      before: String(context.before || '').trim(),
      after: String(context.after || '').trim(),
    };
    if (!Object.values(values).some(Boolean)) return [];
    if (!Object.values(values).every(Boolean)) {
      throw new TypeError('變更物件、欄位及前後型別必須完整提供。');
    }

    const part = '(?:[A-Za-z][A-Za-z0-9_$#]{0,127}|"[A-Za-z0-9_$# ]{1,128}")';
    if (!new RegExp(`^${part}(?:\\.${part}){0,2}$`).test(values.object)
      || !new RegExp(`^${part}$`).test(values.column)) {
      throw new TypeError('變更物件或欄位名稱格式不支援。');
    }
    const typePattern = /^[A-Za-z][A-Za-z0-9_ ]{0,31}(?:\(\s*\d{1,5}(?:\s*,\s*\d{1,5})?\s*\))?(?:\s+WITH(?:\s+LOCAL)?\s+TIME\s+ZONE)?$/i;
    if (values.before.length > 64 || values.after.length > 64
      || !typePattern.test(values.before) || !typePattern.test(values.after)) {
      throw new TypeError('前後型別請輸入簡短資料型別，例如 VARCHAR2(20)。');
    }

    return [{
      ...values,
      changeType: 'definition_changed',
      origin: 'operator_entered',
      verification: 'not_verified_by_tool',
    }];
  }

  function canonicalIdentifier(value) {
    const parts = String(value || '').trim().match(/"(?:[^"]|"")*"|[^.]+/g) || [];
    return parts.map(part => {
      const trimmed = part.trim();
      if (trimmed.startsWith('"') && trimmed.endsWith('"')) {
        return trimmed.slice(1, -1).replace(/""/g, '"');
      }
      return trimmed.toUpperCase();
    }).join('.');
  }

  function buildSummary(rows, model, generatedAt, changeContext) {
    const changes = normalizeChangeContext(changeContext);
    const relevantRows = changes.length
      ? rows.filter(row => changes.some(change =>
        canonicalIdentifier(row.sourceObject) === canonicalIdentifier(change.object)
        && canonicalIdentifier(row.sourceField) === canonicalIdentifier(change.column)))
      : rows;
    const impacts = relevantRows.map(row => ({
      object: String(row.targetObject || ''),
      column: String(row.targetField || ''),
      relationship: row.relation === '間接' ? '間接' : '直接',
      evidence: row.sourceObject && row.sourceField
        ? `${row.sourceObject}.${row.sourceField} → ${row.targetObject}.${row.targetField}`
        : `SQL 分析結果 → ${row.targetObject}.${row.targetField}`,
    }));
    const counts = new Map();
    for (const message of model?.messageList || []) {
      if (message.level === 'warn' || message.level === 'error') {
        counts.set(message.level, (counts.get(message.level) || 0) + 1);
      }
    }

    return {
      schemaVersion: '1.0',
      generatedAt,
      source: 'SQL SPA Tools column lineage',
      changeSummary: changes.length
        ? '操作者輸入之變更背景（本工具未驗證 SQL 版本差異）'
        : '載入之 SQL 欄位血緣分析摘要（非 SQL 版本差異）',
      changes,
      impacts,
      analysisMessages: ['warn', 'error']
        .filter(level => counts.has(level))
        .map(level => ({ level, count: counts.get(level) })),
      limitations: [
        ...LIMITATIONS,
        ...(changes.length
          ? ['impacts 僅列出來源欄位符合操作者輸入 changes 的關係；其他欄位關係不在此清單。']
          : []),
      ],
    };
  }

  const api = { buildSummary, normalizeChangeContext };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (root) root.SQLCopilotExport = api;
})(typeof window !== 'undefined' ? window : globalThis);
