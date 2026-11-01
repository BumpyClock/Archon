import { readFileSync } from 'node:fs';

const path = process.argv[2] ?? 'public/test-results/test-results.json';
try {
  const result = JSON.parse(readFileSync(path, 'utf8'));
  const keys = ['numTotalTests', 'numPassedTests', 'numFailedTests', 'numTotalTestSuites', 'numFailedTestSuites'];
  if (!keys.every((key) => Number.isInteger(result[key]) && result[key] >= 0) || typeof result.success !== 'boolean') {
    throw new Error('Malformed Vitest summary');
  }
  console.log(`Test Suites: ${result.numFailedTestSuites} failed, ${result.numTotalTestSuites} total`);
  console.log(`Tests: ${result.numPassedTests} passed, ${result.numFailedTests} failed, ${result.numTotalTests} total`);
  console.log(`Results: ${path}`);
  process.exitCode = result.success && result.numTotalTests > 0 && result.numFailedTests === 0 && result.numFailedTestSuites === 0 ? 0 : 1;
} catch (error) {
  console.error(`Cannot summarize ${path}: ${error.message}`);
  process.exitCode = 1;
}
