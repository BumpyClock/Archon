#!/usr/bin/env python3
"""Run the prepared checker against small real TypeScript project graphs."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
FRONTEND = ROOT / 'archon-ui-main'
TSC = Path(os.environ.get('ARCHON_TEST_TSC_JS', FRONTEND / 'node_modules/typescript/bin/tsc'))
NODE = shutil.which('node')


class FrontendProjectChecks(unittest.TestCase):
    def setUp(self):
        self.assertTrue(TSC.is_file(), 'Run npm ci in archon-ui-main first, or set ARCHON_TEST_TSC_JS to a prepared compiler.')
        node = NODE
        if node is None:
            raise RuntimeError('Prepare Node before running these fixtures.')
        self.temp = tempfile.TemporaryDirectory(prefix='frontend graph ')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.frontend = self.root / 'archon-ui-main'
        (self.frontend / 'src').mkdir(parents=True)
        (self.frontend / 'src/main.ts').write_text('export const value = 1;\n')
        (self.frontend / 'vite.config.ts').write_text('export default 1;\n')
        for name in ['tsconfig.json', 'tsconfig.node.json']:
            shutil.copy2(FRONTEND / name, self.frontend / name)
        checker = self.root / 'scripts/ci/check-frontend.sh'
        checker.parent.mkdir(parents=True)
        shutil.copy2(ROOT / 'scripts/ci/check-frontend.sh', checker)
        bins = self.frontend / 'node_modules/.bin'
        bins.mkdir(parents=True)
        (bins / 'tsc').write_text('#!/bin/sh\nexec "$ARCHON_TEST_NODE" "$ARCHON_TEST_TSC_JS" "$@"\n')
        (bins / 'vitest').write_text('#!/bin/sh\nexit 0\n')
        for path in bins.iterdir():
            path.chmod(0o755)
        tools = self.root / 'tools'
        tools.mkdir()
        npm = tools / 'npm'
        npm.write_text('#!/bin/sh\nprintf "%s\\n" "$*" >> "$ARCHON_TEST_COMMANDS"\n')
        npm.chmod(0o755)
        self.log = self.root / 'commands'
        self.env = dict(os.environ, PATH=str(tools) + os.pathsep + os.environ['PATH'],
                        ARCHON_TEST_NODE=node, ARCHON_TEST_TSC_JS=str(TSC.resolve()),
                        ARCHON_TEST_COMMANDS=str(self.log))
        self.checker = checker

    def run_checker(self):
        return subprocess.run(['bash', str(self.checker)], cwd=self.root, env=self.env,
                              text=True, capture_output=True, timeout=30)

    def test_valid_application_and_vite_projects_reach_tests(self):
        result = self.run_checker()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('run test:coverage:run', self.log.read_text())

    def test_vite_only_type_error_stops_before_tests(self):
        (self.frontend / 'vite.config.ts').write_text('const value: number = "wrong";\nexport default value;\n')
        result = self.run_checker()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('TS2322', result.stdout + result.stderr)
        self.assertNotIn('run test:coverage:run', self.log.read_text())

    def test_application_type_error_stops_before_tests(self):
        (self.frontend / 'src/main.ts').write_text('export const value: number = "wrong";\n')
        result = self.run_checker()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('TS2322', result.stdout + result.stderr)
        self.assertNotIn('run test:coverage:run', self.log.read_text())


if __name__ == '__main__':
    unittest.main()
