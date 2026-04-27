# CS498 MongoDB Explorer Demo

A demo-friendly MongoDB dashboard using:
- **UI baseline inspired by** `quiet-starlight-69a5c9` (collections + queries workflow)
- **Frontend**: Vite + vanilla JS
- **Backend**: Flask + PyMongo
- **Query engine**: your existing `queries.py` pipelines

The app now has two primary views:
1. **Collections** — collection count + sample document preview.
2. **Queries** — run predefined analytics backed by MongoDB aggregation.

## Project structure

- `index.html` — app entry
- `src/main.js` — dashboard UI, view state, query runner
- `src/style.css` — merged card-style UI theme
- `src/data/mockData.js` — mock dataset
- `src/services/explorerService.js` — API + mock fallback service
- `app.py` — Flask API (`/api/collections`, `/api/queries/run`)
- `queries.py` — MongoDB aggregation pipelines (provided)
- `requirements.txt` — Python backend dependencies
- `.env.example` — environment variable template
- `tests/explorerService.test.js` — smoke/unit tests
- `TOP_LEVEL_DESIGN.md` — top-level design document

## Why this is easy to maintain

1. Data access is isolated in `explorerService` with API fallback to mock mode.
2. Query UI is config-driven (`PREDEFINED_QUERIES`) and easy to extend.
3. Backend wraps reusable query functions without coupling UI to Mongo internals.

## Setup

### 1) Environment

Copy `.env.example` to `.env` and update your Mongo URI:

- `MONGO`: MongoDB connection string
- `PORT`: backend port (default `5001`)
- `VITE_API_BASE`: frontend API base URL (default `http://127.0.0.1:5001`)

### 2) Install dependencies

```bash
npm install
npm test
npm run build
```

```bash
python3 -m pip install -r requirements.txt
```

### 3) Run backend + frontend

In terminal A:

```bash
python3 app.py
```

In terminal B:

```bash
npm run dev
```

Open the Vite URL from terminal (usually `http://localhost:5173`).

## API endpoints

- `GET /api/health`
- `GET /api/collections`
- `POST /api/queries/run`

Supported `queryId` values:
- `top-country`
- `most-active-user`
- `top-hashtags` (with optional `params.limit`)

## Validation commands

```bash
npm test
npm run build
```