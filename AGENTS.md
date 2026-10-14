# MARSEL ROAPP — Agent Control Rules

1. Treat MARSEL and ROAPP as one system and one project.
2. Use `main` and the canonical repository `atalanrafael-jpg/Ro-app` as the source of truth.
3. Prefer existing canonical implementations over creating versioned duplicates.
4. Default all live data operations to READ-ONLY.
5. Never claim live verification, backup, restore, OAuth, MCP authorization or WRITE readiness without direct evidence.
6. Do not guess identifiers or mutate production data to discover API behavior.
7. Keep credentials out of source, documentation, logs and artifacts.
8. Use `.github/workflows/marsel-unified-control-plane.yml` for the unified audit path.
9. When a duplicate PR or audit implementation is superseded, close the duplicate and preserve the canonical implementation.
10. After changes, run CI and verify the resulting state before declaring the task complete.
11. In VS Code Agent, prefer the smallest relevant tool set; enable browser tools only for UI verification and MCP tools only when their server and permissions are explicitly configured.
12. For local verification, run the same canonical checks used by `marsel-release-readiness.yml`: compile `scripts`, run `marsel_canonical_self_check.py`, run `marsel_release_readiness_v1.py`, then verify the production gate remains fail-closed.
13. Never synthesize PASS evidence. Missing, stale, malformed, or incomplete evidence must remain a failure/review state.
14. For automation, use the sequence `inspect → change → test → evidence → review`; do not silently bypass a failed gate.
# MARSEL ROAPP — Codex Agent Instructions

## Scope

This repository is the canonical technical contour for MARSEL ROAPP.
- MARSEL = business contour.
- ROAPP = technical contour.
- Canonical branch: `main`.
- `main` is the technical canonical branch and current execution source.

## Operating priorities

Accuracy → Security → Data preservation → Recovery → Stability → Legality → API verification → Automation → Efficiency → Growth.

## Safety gate

Default to READ-ONLY work.

Before any production write:
1. READ
2. ANALYZE
3. BACKUP
4. VERIFY RESTORE PATH
5. DRY-RUN
6. WRITE only when explicitly authorized and technically verified
7. VERIFY expected vs actual
8. QA and record evidence

Never delete, migrate, mass-update, or overwrite RO App production data automatically.

## No guessing

Never invent or infer API endpoints, methods, IDs, fields, schemas, statuses, relationships, permissions, limits, backup status, synchronization status, or integration state. Use only verified live data, verified official documentation, repository configuration/code, or explicit business requirements. Otherwise mark `NOT VERIFIED` or `PROPOSED`.

## RO App API

Before using an endpoint, verify official documentation or repository evidence, URL/path, HTTP method, authentication, parameters, response schema, pagination, errors, limits, and version. Prefer the established read-only API inventory and diagnostics. Never expose `ROAPP_API_KEY` or any other secret in code, commits, logs, artifacts, issues, or reports.

## Data integrity

For audits check pagination and the complete available range. Track IDs, duplicates, missing values, invalid relationships, clients, orders, products, services, categories, inventory, prices, costs, metals, stones, repairs, statuses, and reference data where the API actually exposes them. Never auto-delete duplicates; compare IDs, codes/SKU, names, relationships, history, and usage first.

## GitHub / CI

CI success is evidence only for checks actually executed. Verify workflow logs, artifacts, tests, dependency/security checks, and the exact commit. After changes use: BEFORE → ACTION → AFTER → DIFF → INTEGRITY → QA → EVIDENCE. Never claim a change is installed, deployed, synchronized, backed up, restored, or production-ready without direct evidence.

## Automation

Use TRIGGER → VALIDATE → ACTION → LOG → VERIFY → ALERT. Prefer audit and diagnostic automation first. Keep production WRITE disabled unless the explicit safety gate and authorization are satisfied.

## Project control

Continue from the latest confirmed control point. Do not repeat closed work without a reason. Resolve contradictions by preferring newer, directly verified evidence. Prefer existing canonical implementations over versioned duplicates.

## Status vocabulary

`VERIFIED` · `PARTIAL` · `FAILED` · `BLOCKED` · `NOT VERIFIED` · `PROPOSED`

## Reporting

For material changes report: GOAL → VERIFIED → DATA → CHANGED → ERRORS → QA → RISKS → RESULT → NEXT STEP.
