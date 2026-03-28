# YC Startup Research Agent

YC Startup Research Agent fetches recent Y Combinator startups, enriches them with structured research, and presents them in a Next.js frontend backed by FastAPI and PostgreSQL.

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

## Local Development

### Backend

```bash
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

## Environment Files

Do not commit real secrets. Use:

- `.env.example`
- `frontend/.env.example`

Keep real values only in local files such as:

- `.env`
- `.env.local`
- `frontend/.env`
- `frontend/.env.local`
