# MARSEL ROAPP — Premium Platform V1

Commercial owner platform for Ювелирная студия MARSEL. Existing control-plane, RO App read-only integration, Supabase/RLS, audit and historical material remain intact.

## New product layer
- Premium responsive owner dashboard.
- CRM/client management.
- Repair workflow for jewelry, watches, glasses and other items.
- Status history and audit trail.
- Attachment references.
- AI assistant boundary with server-side credentials only.
- YooKassa payment adapter with live charging disabled by default.
- Subscription schema for Free / Pro / Studio / Enterprise.
- Admin-ready navigation and capability model.
- SEO metadata and PWA manifest.
- Performance-focused single-page frontend without a build dependency.

## Security invariants
- RO App remains READ-ONLY.
- No RO App API key reaches the browser.
- OpenAI key remains server-side.
- Payment credentials remain server-side.
- Supabase RLS remains the application authorization boundary.
- AI output is advisory, not authoritative.
- Live payments require explicit PAYMENT_LIVE_ENABLED=true plus verified provider credentials.

## Commercial model
Suggested tiers: Free, Pro, Studio and Enterprise. Pricing is a product decision and must be validated against unit economics and market testing.

## Deployment
1. Keep main as the canonical branch.
2. Review the additive SQL migration against the current remote Supabase schema before applying.
3. Configure Supabase Auth and publishable key.
4. Configure OPENAI_API_KEY only on the server if AI is enabled.
5. Configure payment credentials only in server secret storage; keep live mode disabled during staging.
6. Deploy FastAPI with HTTPS.
7. Run health/readiness and authenticated owner E2E checks.
8. Keep production WRITE fail-closed until the existing production gates pass with fresh evidence.

## Roadmap
V1.1: catalog, quotes, invoices, webhooks and richer analytics.
V1.2: WhatsApp/email automation, scheduling and stock forecasting.
V2: AI sales copilot, visual catalog assistant, personalization and recommendation engine.
