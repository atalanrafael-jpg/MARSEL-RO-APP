# MARSEL ROAPP — Owner MVP Preflight Contract

Date: 2026-10-01
Canonical repository: `atalanrafael-jpg/MARSEL-Ro-app`
Canonical branch: `main`

## Objective

Move MARSEL ROAPP from infrastructure-heavy development to a verifiable owner-facing vertical slice:

`AUTH → OWNER DASHBOARD → CLIENT → REPAIR → ITEM → STATUS → ATTACHMENT → AUDIT → DEPLOY → VERIFY`

## Current verified repository state

- The canonical repository is `atalanrafael-jpg/MARSEL-Ro-app`.
- The default/canonical technical branch is `main`.
- The repository contains the Owner MVP runtime at `/app`.
- Owner authentication is implemented with Supabase Auth plus an application-role check.
- The Owner UI can create/search clients, create repairs, manage status, record status history, record attachment references, and write audit records.
- RO App remains READ-ONLY for the MVP.
- The connected Supabase project currently has zero application rows in the Owner MVP tables.

## Automated preflight

`scripts/marsel_owner_mvp_preflight.py` checks the repository without network access or production mutation.

It verifies:

1. required Owner MVP files exist;
2. no obvious embedded RO App/Supabase service secrets are present in application/UI configuration;
3. health/readiness and Owner MVP routes exist;
4. authentication and application-role gates are present;
5. the UI contains client, repair, status-history, attachment-reference and audit flows;
6. production WRITE remains governed by the existing fail-closed policy.

## External gates that remain separate

The following are not marked complete by this preflight:

- live deployment;
- live end-to-end login with an authorized Owner account;
- live Supabase RLS exercise with real application rows;
- fresh RO App reconciliation;
- production WRITE authorization;
- account-level GitHub security/ruleset verification;
- Gmail OAuth authorization;
- RO App MCP authorization.

A successful preflight is repository evidence, not proof of those external conditions.

## Next safe execution order

1. Run this preflight on canonical `main`.
2. Verify the resulting GitHub Actions run.
3. Verify deployment independently.
4. Execute a controlled Owner MVP E2E test with an authorized account.
5. Capture evidence.
6. Only then advance Product Gate A.

No production data mutation is part of this contract.

## Deployment control checkpoint

2026-10-01: Railway service `marsel-roapp` is configured for this repository and `main`, but a manual redeploy produced a successful deployment from older commit `45a36badad93e05214c64071f81c8b01f0693cbe`. Current GitHub `main` is `4250dc61e63f76de00d53d9a2f82a969a4ecd856`. This discrepancy must be resolved before claiming current-main production deployment.
