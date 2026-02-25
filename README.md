# Leave Recorder

A personal leave tracking web app. Record and visualize your annual leave with an interactive calendar.

## Tech Stack

- **Frontend**: React + Vite SPA
- **Backend/DB/Auth**: [Supabase](https://supabase.com) (Postgres + Auth + RLS)
- **Deployment**: [Cloudflare Pages](https://pages.cloudflare.com)

## Quick Start

### Prerequisites

- Node.js 18+
- A Supabase project (see [supabase/README.md](./supabase/README.md))

### Local Development

```bash
cd frontend
cp .env.example .env
# Fill in your Supabase URL and anon key in .env
npm install
npm run dev
```

Visit http://localhost:5173

### Build for Production

```bash
cd frontend
npm run build
# Output is in frontend/dist/
```

## Supabase Setup

Run [supabase/schema.sql](./supabase/schema.sql) in the Supabase SQL editor. See [supabase/README.md](./supabase/README.md) for full instructions.

## Cloudflare Pages Deployment

1. Connect the GitHub repo to Cloudflare Pages
2. Set **Build command**: `cd frontend && npm run build`
3. Set **Build output directory**: `frontend/dist`
4. Add environment variables:
   - `VITE_SUPABASE_URL`
   - `VITE_SUPABASE_ANON_KEY`

## Features

- Month view calendar with leave tracking
- Left-click to toggle vacation/sick leave
- Right-click to toggle half-day
- Click and drag to select a date range
- Year stats: total allowance, taken, booked, remaining days
- User preferences: allowance, carryover, week start, leave year start
- Supabase Auth (email + password) with Row Level Security

## Environment Variables

| Variable | Description |
|---|---|
| `VITE_SUPABASE_URL` | Your Supabase project URL |
| `VITE_SUPABASE_ANON_KEY` | Your Supabase anon/public key |
