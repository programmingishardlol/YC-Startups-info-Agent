# YC Startup Research Agent

YC Startup Research Agent fetches recent Y Combinator startups, enriches them with structured research, and presents them in a Next.js frontend backed by FastAPI and PostgreSQL.

## What It Does

- Scrapes Y Combinator's current batch deterministically
- Enriches startup profiles with structured LLM output
- Rewrites key fields in plain English for non-technical readers
- Estimates market size with reasoning, hints, and benchmarks
- Stores all discovered startups in Postgres
- Keeps a separate history of startups shown on the website
- Uses `MEMORY.md` to prevent repeated mistakes across runs

## Stack

- FastAPI backend for YC scraping and LLM enrichment
- Next.js frontend with Tailwind CSS and shadcn/ui-style components
- Prisma ORM with PostgreSQL
- Supabase for hosted Postgres

## Features

- Fetches YC startups from the current batch
- Generates plain-English company summaries
- Estimates market size with reasoning
- Uses a file-based memory system from `MEMORY.md`
- Stores all discovered startups in Postgres
- Keeps a separate history of shown startups
- Manual homepage refresh for a stable "current 5" experience

## Project Structure

- `app/`: FastAPI backend
- `frontend/`: Next.js frontend and Prisma schema
- `MEMORY.md`: learned mistakes and prevention rules
- `MARKET.md`: market-sizing guidance

## Prerequisites

- Python 3.11+
- Node.js 18+
- npm
- OpenAI API key
- PostgreSQL database
- Supabase project if you want hosted Postgres

## Environment Setup

Use the example files as templates:

```bash
cp .env.example .env
cp frontend/.env.example frontend/.env
cp frontend/.env.example frontend/.env.local
```

Fill in real values locally. Do not commit secrets.

Backend env values live in:

- `.env`

Frontend env values live in:

- `frontend/.env`
- `frontend/.env.local`

Important frontend env vars:

- `API_BASE_URL`
- `DATABASE_URL`
- `DIRECT_URL`
- `CRON_SECRET`

## Database Setup

If you are using Supabase:

1. Create a Supabase project.
2. Copy the pooled Postgres connection string into `DATABASE_URL`.
3. Copy the direct Postgres connection string into `DIRECT_URL`.

Then initialize Prisma:

```bash
cd frontend
npm install
npx prisma generate
npx prisma db push
```

This creates the database tables used by the site, including:

- `Startup`
- `StartupView`

## Run Locally

You need both the backend and frontend running.

### Backend

```bash
cd "/path/to/YC research agent"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npx prisma generate
npm run dev
```

## Open The Website

Once both servers are running:

- Frontend website: `http://127.0.0.1:3000`
- Backend API: `http://127.0.0.1:8000`

The website is the main UI.

What to expect:

- The homepage shows the current pinned set of 5 startups.
- The page does not change automatically on reload.
- Clicking the refresh button at the top selects a new set.
- The history page shows startups that were shown before.

Useful routes:

- Website homepage: `http://127.0.0.1:3000`
- Seen startups history: `http://127.0.0.1:3000/history`
- Backend health check: `http://127.0.0.1:8000/health`
- Enriched API JSON: `http://127.0.0.1:8000/api/v1/startups/latest-enriched`

## Refresh Behavior

- `startups` stores all discovered YC startups
- `startup_views` stores view events separately
- the homepage only changes when you click the refresh button
- a scheduled refresh can update the stored startup catalog without changing the homepage

## Optional Weekly Catalog Refresh

The frontend exposes a cron route for catalog refresh:

```text
/api/cron/refresh-startups
```

Protect it with `CRON_SECRET` and trigger it from:

- Supabase Cron
- GitHub Actions
- a normal server cron job

Example:

```bash
curl -X POST http://127.0.0.1:3000/api/cron/refresh-startups \
  -H "x-cron-secret: YOUR_CRON_SECRET"
```

## Environment Files

Do not commit real secrets. Use:

- `.env.example`
- `frontend/.env.example`

Keep real values only in local files such as:

- `.env`
- `.env.local`
- `frontend/.env`
- `frontend/.env.local`
