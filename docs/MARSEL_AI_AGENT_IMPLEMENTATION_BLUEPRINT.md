# MARSEL ROAPP AI Agent — Implementation Blueprint

Status: PROPOSED / NOT IMPLEMENTED
Owner: MARSEL ROAPP
Canonical repository: `atalanrafael-jpg/MARSEL-Ro-app`
Canonical branch: `main`
Prepared: 2026-10-11

## 1. Goal

Build a governed, provider-neutral AI agent for the existing MARSEL ROAPP product. Extend the current AI control plane; do not create a parallel project or bypass existing production safeguards.

The first deliverable is an owner-facing development and operations agent that can inspect evidence, prioritize defects, propose patches, run tests in CI, summarize outcomes, and monitor business workflows. It must distinguish plans from deployed capabilities.

## 2. Agent roles

1. **Orchestrator** — classifies each request, selects an allowed tool/model, creates a task plan, and tracks evidence.
2. **Software Engineer** — reviews architecture, drafts minimal code changes, and proposes tests.
3. **Quality & Security Auditor** — checks dependencies, auth boundaries, RLS assumptions, exposed secrets, unsafe changes, and test coverage.
4. **Jewelry Operations Analyst** — analyzes catalog quality, materials, repairs, orders, cost composition, and inventory anomalies using authorized data only.
5. **Business Analyst** — calculates KPIs from source data, distinguishes realized results from forecasts, and identifies customer follow-up opportunities.
6. **Catalog & Visual Assistant** — supports product descriptions, image tagging, design briefs, and catalog consistency; never claims an image proves material purity or gemstone authenticity.
7. **Release Controller** — checks CI, migrations, deployment evidence, rollback plans, and approval gates.

These are logical roles in one agent system, not separate project branches or proof of deployed agents.

## 3. Model gateway and routing

Use a provider adapter interface rather than hard-coding a single model. Candidate providers include OpenAI, Anthropic, and Google Gemini, subject to current API support, account access, privacy terms, regional availability, and measured task quality.

Route by task:
- code reasoning and implementation planning: a strong coding/reasoning model;
- multimodal catalog work: a vision-capable model;
- embeddings and retrieval: embedding model plus permission-filtered search;
- structured financial, inventory, and KPI calculations: deterministic code/SQL first; LLM explains results but does not replace arithmetic;
- low-risk repetitive classification: a cheaper model after evaluation;
- provider outage: retry with bounded backoff or use an explicitly approved fallback.

Required controls:
- model registry with provider, model ID, capabilities, pricing metadata, evaluation date, and enabled state;
- task-level budget and token limits;
- timeout, retry, rate-limit handling, and circuit breaker;
- schema-validated outputs for tool calls;
- evaluation suite before model/provider changes;
- no secrets in prompts, logs, browser bundles, commits, or generated reports.

Model names and pricing must be checked against official provider documentation when implementing. Do not treat this candidate list as a claim that APIs are connected.

## 4. Tool and integration boundary

Integrations may include GitHub, Supabase, official ROAPP API/MCP, CI/CD, and deployment/observability services only after capability and authorization are directly verified.

Every connector declares:
- identity and environment;
- read/write capabilities;
- data classification and allowed fields;
- timeout/rate limit;
- required authorization;
- audit-log destination;
- test/health-check method.

Default mode: READ-ONLY. Never infer API endpoints, identifiers, schemas, credentials, migration state, backups, or synchronization success.

## 5. Decision and execution protocol

`OBSERVE → VALIDATE → CLASSIFY → ASSESS_IMPACT → ASSESS_RISK → RECOMMEND → APPROVAL_GATE → ACTION → VERIFY → DOCUMENT`

For each task store:
- task ID and timestamp;
- request and scoped environment;
- source references and evidence freshness;
- plan and expected outcome;
- risk class and approval status;
- tool/model versions;
- action result and verification result;
- follow-up or blocker.

**Internal task lifecycle** (agent execution only): `QUEUED`, `IN_PROGRESS`, `WAITING_APPROVAL`, `COMPLETED`, `CANCELLED`.

**Canonical control/reporting statuses** (for Owner Control Center and control items): `NEW`, `PROPOSED`, `PARTIAL`, `VERIFIED`, `DONE`, `PREPARED`, `NOT VERIFIED`, `FAILED`, `BLOCKED`, `NEEDS USER ACTION`, `REVIEW_REQUIRED`, `NOT_TESTED`.

Never pass internal lifecycle values directly into the Owner Control Center's canonical status field. Map them explicitly at the reporting boundary: `QUEUED` → `NEW`; `IN_PROGRESS` → `PARTIAL`; `WAITING_APPROVAL` → `NEEDS USER ACTION`; `COMPLETED` → `DONE` only after independent verification, otherwise `REVIEW_REQUIRED`; `CANCELLED` → `NOT VERIFIED` with a cancellation reason. Use `VERIFIED` only when implementation, test result, and current evidence support it. A model-generated assertion alone is never evidence.

## 6. Safety tiers

- **Tier 0 — Observe:** read-only repository, logs, and authorized business data.
- **Tier 1 — Prepare:** generate patch, SQL migration, report, or deployment plan without applying it.
- **Tier 2 — Reversible non-production action:** allowed only with policy, authorization, and verification.
- **Tier 3 — Production or sensitive action:** disabled by default; requires explicit approval, verified backup/restore, dry-run, idempotency, rollback, least privilege, and post-action verification.

Never silently enable production writes, modify RLS/security policy, reset or repair linked production migrations, rotate keys, delete business records, merge a PR, or deploy to production.

## 7. Product capabilities to build

### Owner Control Center
- prioritized work queue and blocker list;
- sales, margin, work-in-progress, repair turnaround, inventory, and customer follow-up KPIs;
- source timestamp and confidence/evidence class on every metric;
- AI recommendations with expected benefit, risk, and approval state;
- integration health and latest successful verification;
- audit trail and exportable reports.

### Jewelry workflow intelligence
- repair intake/status/attachment/audit trail;
- item and material catalog quality checks;
- cost composition for metal, stones, labor, and other recorded costs;
- duplicate product-code and orphan/reference detection;
- reminders for customer follow-up and uncollected repairs;
- product descriptions and image tagging with human review;
- online catalog readiness checks.

### Developer autopilot
- inspect current main and open work before proposing changes;
- reproduce issues with tests where possible;
- generate smallest compatible patch on a feature branch;
- run lint/type-check/unit/integration/security checks;
- open a draft PR with evidence and rollback notes;
- never merge or deploy automatically until explicit release policy authorizes it.

## 8. Data architecture

Use existing Supabase project `wdbytmvzuensuuoquvav`; do not create a replacement project.

Proposed entities, subject to schema review:
- `ai_tasks`
- `ai_task_events`
- `ai_evidence`
- `ai_model_registry`
- `ai_tool_registry`
- `ai_approvals`
- `ai_evaluations`

Before migrations, inspect the current schema and migration history, produce a reviewed baseline, check RLS policies, and test against a non-production database. Do not apply this proposed schema to production as-is.

## 9. Continuous monitoring

Scheduled checks should monitor:
- current main SHA and recent commits;
- required GitHub Actions/checks tied to that SHA;
- open PRs/issues and new blockers;
- dependency/security alerts when authorized;
- Supabase health, migration consistency, Auth/RLS tests;
- ROAPP integration status using documented read-only calls;
- data-quality and inventory exception counts;
- provider/model availability and official release notes when configured.

Every report must include checked-at time, evidence links, status, differences from the previous checkpoint, and one next safe action. If monitoring cannot access a source, report `BLOCKED` rather than inventing a result.

## 10. Required implementation sequence

1. **Baseline** — inspect app entry points, current architecture, CI workflows, Supabase schema/migrations, RLS, and issue tracker.
2. **Repair quality gates** — replace placeholder test scripts with real checks; add lint/type-check/unit tests appropriate to the actual stack.
3. **Agent core** — typed task contract, evidence ledger, policy engine, provider adapters, tool registry, audit log.
4. **Read-only connectors** — GitHub/Supabase/ROAPP read-only adapters with contract tests and redaction.
5. **Owner UI** — expose task status, evidence, approvals, exceptions, and KPIs in the existing app.
6. **Evaluations** — prompt injection tests, tool authorization tests, RLS tests, cost/latency evaluation, regression set.
7. **Staged rollout** — local/test → preview → owner review → production only after all gates pass.

## 11. Acceptance criteria

- no secret values appear in repository, client code, prompts, or logs;
- every AI claim that affects decisions links to current evidence;
- every tool call is allow-listed and permission-checked;
- RLS isolation and protected-route behavior have automated tests;
- model outputs are schema-validated and untrusted content cannot override system policy;
- no production write can occur without the configured approval gate;
- failures produce actionable logs and do not falsely report success;
- current-SHA CI and deployment verification are visible;
- model/provider switching does not require rewriting business logic;
- the Owner MVP remains the productization priority.

## 12. Current known blockers

- Issue #187 records a Supabase migration-history mismatch: remote history had six versions while the canonical repository had only two migration files, with the Supabase branch reported as `MIGRATIONS_FAILED` in the issue's dated evidence. This must be rechecked live before any repair.
- The repository `package.json` currently defines `npm test` as a placeholder that exits with failure. Replace only after confirming the actual app/tooling layout.
- This blueprint is documentation only. No runtime agent, provider API, model key, background worker, or production automation is created by this file.

## 13. Change-control rule

Implement in small feature branches and draft PRs. Keep `main` protected by review and CI. Never mark a capability `VERIFIED` until its actual implementation, test result, and runtime evidence are available.
