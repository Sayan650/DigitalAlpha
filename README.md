# Coinwise - Digital Alpha Dashboard

Coinwise is a responsive credit-card transaction and rewards dashboard. It pairs a Next.js frontend with a FastAPI/PostgreSQL API, supports server-side filtering and analytics for 10,000 transactions, and provides an atomic coin redemption flow.

## Stack

- Next.js + TypeScript + Recharts
- FastAPI + SQLAlchemy + PostgreSQL 18
- Docker Compose for local PostgreSQL

## Live Deployments

- **Frontend (Vercel)**: https://digital-alpha-nu.vercel.app
- **Backend API (Render)**: https://digitalalpha-2j98.onrender.com
- **GitHub Repository**: https://github.com/Sayan650/DigitalAlpha

## Run locally

Prerequisites: Node 20+, Python 3.12+, and Docker Desktop. The provided `transactions_DA.json` is tracked under `api/data/`.

1. Start the database: `docker compose up -d db`
2. Copy `.env.example` to `api/.env` and set `DATABASE_URL` if needed.
3. Install and seed the API:
   ```bash
   cd api
   python -m venv .venv
   .venv/Scripts/pip install -r requirements.txt
   .venv/Scripts/python -m app.seed --reset
   .venv/Scripts/uvicorn app.main:app --reload --port 8000
   ```
4. In another terminal, run the frontend:
   ```bash
   cd web
   pnpm install
   pnpm dev
   ```

Open `http://localhost:3000`. The API docs are at `http://localhost:8000/docs`.

## Status

Implemented: normalized seed pipeline, server-side transaction queries, analytics, reward balance/redemption, responsive custom table, filters, charts, modal details, and tests.

Not included: authentication and external voucher fulfilment. Deployment URLs are intentionally environment-specific; configure `DATABASE_URL`, `FRONTEND_ORIGIN`, and `NEXT_PUBLIC_API_URL` for Neon, Render, and Vercel.

## Useful commands

- `cd api && pytest` - API/unit tests
- `cd web && pnpm test` - frontend tests
- `cd web && pnpm build` - production frontend build
