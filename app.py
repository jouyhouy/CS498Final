import os
import time
from typing import Any

from bson import json_util
from flask import Flask, jsonify, request
from flask_cors import CORS

from queries import (
    query_most_active_user,
    query_top_country,
    query_top_hashtags,
    tweets,
)


app = Flask(__name__)
CORS(app)


def to_json_safe(value: Any) -> Any:
    """Convert BSON-compatible types (ObjectId, datetime, etc.) to JSON-safe values."""
    return json_util.loads(json_util.dumps(value))


@app.get("/api/health")
def health():
    return jsonify({"ok": True})


@app.get("/api/collections")
def collections():
    count = tweets.estimated_document_count()
    sample_doc = tweets.find_one({}, {"_id": 0})
    payload = [
        {
            "name": "tweets",
            "count": count,
            "sampleDoc": to_json_safe(sample_doc) if sample_doc else None,
        }
    ]
    return jsonify(payload)


@app.post("/api/queries/run")
def run_query():
    body = request.get_json(silent=True) or {}
    query_id = body.get("queryId")
    params = body.get("params") or {}

    start = time.perf_counter()

    if query_id == "top-country":
        rows = query_top_country()
    elif query_id == "most-active-user":
        rows = query_most_active_user()
    elif query_id == "top-hashtags":
        limit_raw = params.get("limit", 10)
        try:
            limit = int(limit_raw)
        except (TypeError, ValueError):
            return jsonify({"error": "Invalid 'limit' parameter."}), 400
        limit = max(1, min(100, limit))
        rows = query_top_hashtags(limit=limit)
    else:
        return jsonify({"error": f"Unknown queryId: {query_id}"}), 400

    execution_ms = int((time.perf_counter() - start) * 1000)

    return jsonify(
        {
            "rows": to_json_safe(rows),
            "count": len(rows),
            "executionMs": execution_ms,
            "source": "mongo",
        }
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5001"))
    app.run(host="0.0.0.0", port=port, debug=True)