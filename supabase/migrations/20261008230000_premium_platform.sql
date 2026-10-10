-- MARSEL ROAPP premium platform extension.
-- Additive migration: does not delete or rewrite existing application tables.
-- Review against the current remote schema before applying.

create table if not exists public.subscriptions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  plan_code text not null check (plan_code in ('free','pro','studio','enterprise')),
  status text not null default 'trialing',
  provider text,
  provider_customer_id text,
  provider_subscription_id text,
  current_period_start timestamptz,
  current_period_end timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create unique index if not exists subscriptions_provider_subscription_idx on public.subscriptions(provider_subscription_id) where provider_subscription_id is not null;
create index if not exists subscriptions_user_idx on public.subscriptions(user_id);

create table if not exists public.ai_usage (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  feature text not null,
  model text,
  input_units integer not null default 0,
  output_units integer not null default 0,
  created_at timestamptz not null default now()
);
create index if not exists ai_usage_user_created_idx on public.ai_usage(user_id, created_at desc);

create table if not exists public.payment_events (
  id uuid primary key default gen_random_uuid(),
  provider text not null,
  provider_event_id text not null,
  event_type text not null,
  payload jsonb not null default '{}'::jsonb,
  processed_at timestamptz,
  created_at timestamptz not null default now()
);
create unique index if not exists payment_events_provider_event_idx on public.payment_events(provider, provider_event_id);

alter table public.subscriptions enable row level security;
alter table public.ai_usage enable row level security;
alter table public.payment_events enable row level security;

create policy subscriptions_owner_read on public.subscriptions for select to authenticated using (user_id = auth.uid());
create policy ai_usage_owner_read on public.ai_usage for select to authenticated using (user_id = auth.uid());
-- payment_events is intentionally not client-writable/readable.
