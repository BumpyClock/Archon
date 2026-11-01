# Staged CI repairs

All existing compatible Linux jobs now select Boat, including Claude, unauthorized-message and release-note jobs. Job IDs, triggers, permissions and authorized-user guards remain unchanged. Public Boat policy is owner-only for BumpyClock, not outsiders or bots. Runner selection does not fix provider API billing. No billing/auth changes, dispatch, deployment or release was performed.

## Baseline and gates

Frontend validation is deliberately disabled pending the existing overhaul. It remains disabled. `scripts/ci/check-frontend.sh` prepares the existing ESLint legacy scope, Biome src/features scope, both application/test and referenced Vite-config TypeScript checks plus Vitest coverage commands for explicit use. Run `npm ci` in archon-ui-main first. Do not enable these gates until owner review of current diagnostics. No tests, rules or isolation were removed to obtain green.

Observed secret-free Boat baseline has existing ESLint/Biome diagnostics, TypeScript errors and failing Vitest suites. Backend Ruff reports existing violations and MyPy stops at an existing syntax error. The backend's previously nonblocking quality commands now propagate failures. MyPy and pytest still run after a prior quality failure unless cancelled; artifact uploads remain always-on.

Backend setup pins uv 0.12.0, uses `uv sync --locked --group all --group dev`, and never adds pytest-cov during CI. Existing lock/group parity passed in Boat. Installed Ruff/MyPy executables run directly; pytest uses `uv run --no-sync`. Missing tools cannot masquerade as successful validation.

The summary checks required job results, not artifact existence. Failure, cancellation, skipping or missing results fail the summary. Frontend install-only success is explicitly not frontend test acceptance. Artifacts use public/test-results/test-results.json, public/test-results/coverage and backend-test-results. The explicit frontend test summary reads the actual Vitest JSON location and fails on missing, malformed, empty or failed results.

## Regression checks

After preparing frontend dependencies, run `python3 scripts/ci/test_frontend_check.py` to prove that application and Vite-only type errors both stop before tests. It uses the project-local TypeScript compiler and synthetic graph fixtures, not the full application. Also run `python3 scripts/ci/test_require_results.py` and `node --test archon-ui-main/scripts/test-summary.test.mjs`. They exercise actual executable result gates with synthetic fixtures and no GitHub/API calls. Existing application lint/typecheck/coverage results are separate evidence, not inferred from these harnesses.

Cache persistence, Docker layer caching and frontend job splitting remain deferred until equivalent passing application baseline and setup overhead measurements exist. Full Vitest isolation and existing required job names remain intact. Changelog updates happen at landing.
