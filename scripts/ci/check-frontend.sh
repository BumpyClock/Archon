#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../../archon-ui-main"
[[ -x node_modules/.bin/tsc && -x node_modules/.bin/vitest ]] || { echo 'Run npm ci explicitly first.' >&2; exit 1; }
# Prepared for explicit use only. CI activation waits for frontend overhaul approval.
npm run lint
npm run biome:ci -- src/features
node_modules/.bin/tsc --noEmit --project tsconfig.json
node_modules/.bin/tsc --noEmit --project tsconfig.node.json
npm run test:coverage:run
npm run test:coverage:summary
