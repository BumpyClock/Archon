"""Exercise the executable summary gate; never calls GitHub."""
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name('require-results.py')


class SummaryGateTests(unittest.TestCase):
    def invoke(self, results):
        return subprocess.run([sys.executable, str(SCRIPT)],
                              env=dict(os.environ, NEEDS_JSON=json.dumps(results)),
                              capture_output=True, text=True)

    def test_all_existing_required_jobs_successful(self):
        result = self.invoke({name: {'result': 'success'} for name in
                              ['frontend-tests', 'backend-tests', 'docker-build-test']})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('install-only', result.stdout)

    def test_failure_cancel_skip_and_missing_propagate(self):
        for status in ['failure', 'cancelled', 'skipped', None]:
            with self.subTest(status=status):
                results = {name: {'result': 'success'} for name in
                           ['frontend-tests', 'backend-tests', 'docker-build-test']}
                if status is None:
                    del results['backend-tests']
                else:
                    results['backend-tests']['result'] = status
                result = self.invoke(results)
                self.assertEqual(result.returncode, 1)
                self.assertIn('backend-tests', result.stderr)

    def test_unreadable_payload_is_not_green(self):
        result = self.invoke([])
        self.assertEqual(result.returncode, 1)


if __name__ == '__main__':
    unittest.main()
