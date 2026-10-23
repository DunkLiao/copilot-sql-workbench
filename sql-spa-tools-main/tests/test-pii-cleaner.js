const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const html = fs.readFileSync(path.join(__dirname, '..', 'sql-spa-tools-pii-cleaner.html'), 'utf8');

// Worker 失敗時必須讓 Promise 結束，否則畫面會永遠停在「掃描中…」
assert.match(html, /w\.onerror\s*=/, 'worker errors must reject the pending scan');
assert.match(html, /w\.onmessageerror\s*=/, 'message deserialisation errors must reject the pending scan');
assert.match(html, /if \(!workers\.length\) return Promise\.reject/, 'missing workers must fail fast');
assert.doesNotMatch(html, /workers\[\(rr\+\+\)%POOL\]/, 'pool indexing must use the live worker count');

// 寫回時只移除命中的位元組區間
const fn = html.match(/function stripRanges\(buf, hits\)\{[\s\S]*?\n\}/);
assert.ok(fn, 'stripRanges must exist');
const context = {};
vm.runInNewContext(fn[0] + '\nthis.stripRanges = stripRanges;', context);
const input = new Uint8Array([1, 2, 3, 4, 5, 6, 7, 8, 9]).buffer;
const output = context.stripRanges(input, [{ bs: 1, be: 3 }, { bs: 5, be: 8 }]);
assert.deepEqual([...new Uint8Array(output)], [1, 4, 5, 9]);

console.log('PII Cleaner contract passed: worker failure handling, byte-range removal');
