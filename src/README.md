# Goosemarket Setup Guide

This repo contains both the Flask API (`api/`) and the Vite + React frontend (`src/`) for Goosemarket. Follow the steps below to install dependencies, set environment variables, and run the app from scratch.

## Prerequisites
- Node.js 18+ (Node 20 LTS recommended) and npm
- Python 3.11+ with `pip`
- Supabase project URL and service role (secret) key

## Project Layout
- `api/` — Flask API entrypoint at `api/index.py` (port 5328)
- `src/` — React app served by Vite (default port 5173)
- `requirements.txt` — Python dependencies for the API
- `package.json` — Frontend toolchain and dev scripts
- `../tests/` — Pytest suite (run from the `Project/` root)
- `../.env.template` — Sample environment variable names

## 1) Install dependencies
From `Project/src`:
```bash
# (Optional) create a virtual environment
python -m venv .venv
# Activate it:
#   Windows PowerShell: .\.venv\Scripts\Activate.ps1
#   macOS/Linux: source .venv/bin/activate

# Python deps
python -m pip install -r requirements.txt

# Frontend deps
npm install
```

## 2) Configure environment variables and database
The API reads `SUPABASE_URL` and `SUPABASE_SECRET_KEY` from the environment.

1) Set up supabase database
 Create a new project in supabase, initialize the database using the schema in `Project/schema.sql`

2) Copy the template and fill in your values:
```bash
cp ../.env.template .env   # use copy ..\.env.template .env on Windows
# edit .env and set SUPABASE_URL + SUPABASE_SECRET_KEY
```

## 3) Run the app in development
IF ON WINDOWS, Open two terminals in `Project/src`:
1) Start the App
```bash
python api/index.py
```
2) Start the frontend (served on http://localhost:5173):
```bash
npm run dev -- --host
```
OTHERWISE
```bash
npm run dev
```

Notes:
- The package.json `dev` script uses `python3 api/index.py`; it works on systems where `python3` is available. On Windows, use the two-terminal approach above.
- The API runs on port 5328; the frontend proxies requests to it when hitting `/api/...`.

## 4) Run tests
From `Project` (one level up):
```bash
python -m pip install pytest
python -m pytest
```
Ensure the Supabase environment variables are set if any tests require live credentials.
