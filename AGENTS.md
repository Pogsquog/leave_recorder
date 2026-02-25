# AGENTS.md

Instructions for AI agents working on this codebase.

## Project Overview

Holiday Holliday — A personal leave recorder web app.

## Architecture

- **Frontend**: React + Vite SPA in `frontend/`
- **Database + Auth**: Supabase (Postgres with RLS, email auth)
- **Deployment**: Cloudflare Pages


## Tech Stack

- **Frontend**: React 18, React Router 6, Supabase JS SDK
- **Database**: Supabase Postgres (tables: `leave_entries`, `user_preferences`)
- **Auth**: Supabase Auth (email/password)
- **Deployment**: Cloudflare Pages

## Commands

### Local Development

```bash
cd frontend
cp .env.example .env   # fill in Supabase credentials
npm install
npm run dev            # http://localhost:5173
```

### Build

```bash
cd frontend
npm run build          # output in frontend/dist/
```

## Frontend Structure

```
frontend/
  src/
    supabase.js        # Supabase client (reads VITE_SUPABASE_* env vars)
    App.jsx            # Auth gate + React Router layout
    pages/
      Login.jsx        # Login + register (combined)
      Calendar.jsx     # Main month view with leave CRUD
      Preferences.jsx  # User settings
    components/
      MonthPicker.jsx
      YearStats.jsx
    lib/
      leaveApi.js      # leave_entries CRUD via Supabase
      prefsApi.js      # user_preferences CRUD
      leaveCalc.js     # Year stats calculation (JS port of Python LeaveCalculator)
      dateUtils.js     # Date helpers (JS port of apps/utils/dates.py)
    index.css          # Neon dark theme utility classes
  public/
    _redirects         # Cloudflare Pages SPA routing
  .env.example
```

## Supabase Schema

Run `supabase/schema.sql` in the Supabase SQL editor. Tables:
- `user_preferences` — one row per user (auto-created on signup via trigger)
- `leave_entries` — one row per leave day per user

RLS policies ensure users can only access their own data.

## Environment Variables

| Variable | Description |
|---|---|
| `VITE_SUPABASE_URL` | Supabase project URL |
| `VITE_SUPABASE_ANON_KEY` | Supabase anon/public key |

## Code Style

- No TypeScript (plain JS/JSX)
- Functional components with React hooks
- No comment blocks unless explicitly requested
