# MARSEL ROAPP — SYSTEM SYNCHRONIZATION CONTRACT

## Objective
Maintain one canonical control plane for MARSEL ROAPP and detect drift between repository code, instructions, data contracts, workflows, deployment metadata and external capabilities.

This contract does not infer ChatGPT account state, connector authorization, plugin installation, Supabase remote state, RO App authorization or deployment state from Git alone.

## Canonical identity
- System: MARSEL ROAPP
- Business: Ювелирная студия MARSEL
- Repository: atalanrafael-jpg/MARSEL-Ro-app
- Branch: main
- Production WRITE: disabled by default.

## Repository-synchronized
- application code
- tests
- GitHub workflows
- canonical instructions/contracts
- control policies
- integration metadata
- synchronization registry
- audit logic

## Live verification required
- RO App live data and entity coverage
- RO App MCP authorization
- Gmail OAuth authorization
- Supabase remote migration/schema state
- Vercel deployment/runtime
- GitHub account-level security/rulesets
- ChatGPT account/project/connector authorization
- plugin installation/connection state
- external documentation synchronization

## Drift classes
IDENTITY, BRANCH, CODE, WORKFLOW, INSTRUCTION, API_CONTRACT, DATA_SCHEMA, CONNECTOR, PLUGIN, AUTHORIZATION, DEPLOYMENT, SECURITY, EVIDENCE.

Unknown or conflicting state is NOT_VERIFIED / REVIEW_REQUIRED.

## Safety
No production write is performed by this layer.
No secret value is stored in registry or evidence.
No endpoint, identifier, permission or authorization is inferred from naming.
No automatic deletion is permitted.

## Control loop
OBSERVE → COMPARE → CLASSIFY → FIX → TEST → VERIFY → DOCUMENT → MONITOR
