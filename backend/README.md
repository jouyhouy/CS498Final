# Backend API

## Project Overview
This backend is a FastAPI service for a Twitter/X data analysis project. It connects to MongoDB and is intended to power analytics-style queries over a `tweets` collection (for example: top country, most active user, and top hashtags).

The app currently includes a basic API route:

- `GET /` -> returns a simple test response (`{"Hello": "World"}`)

Additional query functions are already implemented in code and can be exposed as API endpoints as the project expands.

## Purpose
The purpose of this backend is to:

- Provide a Python API layer for tweet analytics data.
- Centralize MongoDB access and query logic in one service.
- Serve as the backend foundation for the frontend application in this project.

## Requirements

- Python 3.10+
- pip (Python package manager)
- A MongoDB connection string (local MongoDB or MongoDB Atlas)

Tested locally with Python `3.14.4` in `.venv`.

## Environment Variables
Create a `.env` file in the `backend/` directory, or export the variable in your shell, with:

```env
MONGODB_URI=your_mongodb_connection_string
```

The app will exit on startup if `MONGODB_URI` is not set.

## Run Locally

From the project root (`CS498Final`):

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Start the API server:

```bash
uvicorn main:app --reload
```

The backend will be available at:

- API root: `http://127.0.0.1:8000/`
- Swagger docs: `http://127.0.0.1:8000/docs`
- ReDoc docs: `http://127.0.0.1:8000/redoc`

## Quick Verification
Once the server is running, verify it with:

```bash
curl http://127.0.0.1:8000/
```

Expected response:

```json
{"Hello":"World"}
```

## Notes

- MongoDB database name is currently hardcoded in `main.py` as `twitter_project`.
- Tweet data is expected in the `tweets` collection.
