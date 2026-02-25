-- Holiday Holliday - Supabase Schema
-- Run this in the Supabase SQL editor at: https://supabase.com/dashboard/project/xtmtntpbtzjdgghzhhjq/sql

-- ============================================================
-- Tables
-- ============================================================

-- user_preferences: per-user settings, keyed on auth user ID
create table if not exists user_preferences (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade not null unique,
  annual_leave_allowance int not null default 25,
  carryover_max int not null default 5,
  carryover_days int not null default 0,
  week_start int not null default 1,  -- 1=Monday, 0=Sunday
  year_start_month int not null default 1,
  year_start_day int not null default 1,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- leave_entries: individual leave days
create table if not exists leave_entries (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade not null,
  date date not null,
  leave_type text not null default 'vacation' check (leave_type in ('vacation', 'sick')),
  half_day boolean not null default false,
  notes text not null default '',
  created_at timestamptz default now(),
  updated_at timestamptz default now(),
  unique(user_id, date)
);

create index if not exists leave_entries_user_date on leave_entries (user_id, date);
create index if not exists leave_entries_user_type on leave_entries (user_id, leave_type);

-- ============================================================
-- Row Level Security
-- ============================================================

alter table user_preferences enable row level security;
alter table leave_entries enable row level security;

-- Each user can only see/modify their own data
create policy "Users manage their own preferences"
  on user_preferences for all
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

create policy "Users manage their own leave"
  on leave_entries for all
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

-- ============================================================
-- Auto-create preferences row on new user signup
-- ============================================================

create or replace function handle_new_user()
returns trigger
language plpgsql
security definer set search_path = public
as $$
begin
  insert into public.user_preferences (user_id)
  values (new.id)
  on conflict (user_id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function handle_new_user();

-- ============================================================
-- Updated_at trigger
-- ============================================================

create or replace function update_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create trigger user_preferences_updated_at
  before update on user_preferences
  for each row execute function update_updated_at();

create trigger leave_entries_updated_at
  before update on leave_entries
  for each row execute function update_updated_at();
