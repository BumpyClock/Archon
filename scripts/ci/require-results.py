"""Make the existing summary job fail when any required job is not successful."""
import json
import os
import sys

REQUIRED = ('frontend-tests', 'backend-tests', 'docker-build-test')

try:
    needs = json.loads(os.environ['NEEDS_JSON'])
    failed = [name for name in REQUIRED if needs.get(name, {}).get('result') != 'success']
except (KeyError, TypeError, ValueError, AttributeError) as error:
    print(f'Cannot read required results: {error}', file=sys.stderr)
    sys.exit(1)

for name in REQUIRED:
    print(f'{name}: {needs.get(name, {}).get("result", "missing")}')
print('Frontend job remains install-only until its explicitly disabled checks are approved.')
if failed:
    print('Required jobs failed, cancelled, skipped or missing: ' + ', '.join(failed), file=sys.stderr)
    sys.exit(1)
