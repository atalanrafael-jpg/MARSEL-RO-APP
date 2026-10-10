# MARSEL ROAPP — Deployment Runbook

## Runtime
FastAPI is the application/API runtime. The owner interface is served by the same backend at /app. This preserves the current deployment model and avoids introducing a second frontend service before Gate A.

## Required server configuration
- SUPABASE_URL
- SUPABASE_PUBLISHABLE_KEY
- MARSEL_INTERNAL_API_KEY for protected RO App proxy/audit endpoints
- ROAPP_BASE_URL and ROAPP_API_KEY for server-side read-only RO App access
- OPENAI_API_KEY (optional)
- OPENAI_MODEL (optional; default gpt-6-luna)
- PAYMENT_PROVIDER=yookassa
- PAYMENT_SHOP_ID and PAYMENT_SECRET_KEY (server-side only)
- PAYMENT_RETURN_URL: trusted HTTPS URL configured server-side; client-provided return URLs are not trusted
- PAYMENT_LIVE_ENABLED=false during staging

Never place RO App, OpenAI or payment secrets in web/index.html, browser JavaScript, public environment variables or Git.

## Database
The file supabase/migrations/20261008230000_premium_platform.sql is additive. Review it against the current remote Supabase schema before applying. Do not run db reset --linked on the production project.

## Verification
1. GET /health
2. GET /ready
3. Authenticate through Supabase Auth.
4. Open /app and verify owner role.
5. Create a test client and repair in a controlled environment.
6. Verify status history and audit records.
7. Verify /api/v1/platform/health.
8. Verify AI endpoint with a non-sensitive prompt only when OPENAI_API_KEY is configured.
9. Verify payment endpoint remains DISABLED/NOT_CONFIGURED until explicitly enabled.
10. Run the repository test suite and the existing Owner MVP Gate A workflow.

## Production rule
Production WRITE remains disabled. A green build is not proof of external authorization, live RO App reconciliation, payment readiness or production safety.
