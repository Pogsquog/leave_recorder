# Supabase Setup

## 1. Run the schema

In the [Supabase SQL editor](https://supabase.com/dashboard/project/xtmtntpbtzjdgghzhhjq/sql), run `schema.sql`.

This creates:
- `user_preferences` table (per-user settings)
- `leave_entries` table (leave records)
- RLS policies so each user only sees their own data
- A trigger to auto-create a `user_preferences` row on signup

## 2. Enable Email Auth

In the [Auth settings](https://supabase.com/dashboard/project/xtmtntpbtzjdgghzhhjq/auth/providers), ensure **Email** provider is enabled.

## 3. Environment variables

Copy `frontend/.env.example` to `frontend/.env` and fill in:

```
VITE_SUPABASE_URL=https://xtmtntpbtzjdgghzhhjq.supabase.co
VITE_SUPABASE_ANON_KEY=<anon_key from secrets/supabase>
```

## 4. Cloudflare Pages environment variables

Set the same two vars (`VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`) in the Cloudflare Pages project settings under **Settings → Environment variables**.
