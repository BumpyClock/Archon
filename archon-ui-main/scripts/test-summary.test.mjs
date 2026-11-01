import assert from 'node:assert/strict';
import { mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';
import { test } from 'node:test';

const script = new URL('./test-summary.mjs', import.meta.url);
const passed = { success: true, numTotalTests: 4, numPassedTests: 4, numFailedTests: 0, numTotalTestSuites: 2, numFailedTestSuites: 0 };

for (const [name, value, code] of [
  ['passing', passed, 0],
  ['failed tests', { ...passed, success: false, numFailedTests: 1 }, 1],
  ['failed suite without failed assertion', { ...passed, numFailedTestSuites: 1 }, 1],
  ['empty suite', { ...passed, numTotalTests: 0 }, 1],
  ['malformed', {}, 1],
  ['missing', null, 1],
]) {
  test(name, () => {
    const directory = mkdtempSync(join(tmpdir(), 'summary space '));
    try {
      const path = join(directory, 'results.json');
      if (value !== null) writeFileSync(path, JSON.stringify(value));
      const result = spawnSync(process.execPath, [script.pathname, path], { encoding: 'utf8' });
      assert.equal(result.status, code, result.stdout + result.stderr);
      if (code === 0) assert.match(result.stdout, /4 passed, 0 failed, 4 total/);
    } finally {
      rmSync(directory, { recursive: true, force: true });
    }
  });
}
