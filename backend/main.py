import json
import os
from datetime import datetime
from typing import Any, Literal

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from dotenv import load_dotenv

load_dotenv()

mongodb_uri = os.getenv("MONGODB_URI")
if not mongodb_uri:
    raise RuntimeError("MONGODB_URI is not set.")

client: MongoClient = MongoClient(mongodb_uri)
db: Database = client["twitter_project"]
tweets: Collection[dict[str, Any]] = db["tweets"]

# Pydantic models for the tweet document structure
class TweetUser(BaseModel):
    id: int
    name: str
    screen_name: str
    verified: bool


class TweetReply(BaseModel):
    status_id: int | None = None
    user_id: int | None = None
    screen_name: str | None = None


class TweetPlace(BaseModel):
    country: str | None = None
    full_name: str | None = None
    place_type: str | None = None


class TweetMetrics(BaseModel):
    reply_count: int | None = None
    retweet_count: int | None = None
    favorite_count: int | None = None


class TweetDocument(BaseModel):
    id_: int = Field(alias="_id")
    id: int
    created_at: datetime
    text: str
    lang: str | None = None
    tweet_type: Literal["simple", "reply", "retweet", "quote"]
    user: TweetUser
    reply: TweetReply | None = None
    retweeted_status_id: int | None = None
    quoted_status_id: int | None = None
    place: TweetPlace | None = None
    hashtags: list[str]
    metrics: TweetMetrics | None = None
    raw: dict[str, Any] | None = None

    model_config = ConfigDict(populate_by_name=True)



app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}


def encode_cursor(payload: dict[str, Any]) -> str:
    return json.dumps(payload, separators=(",", ":"), default=str)


def decode_cursor(cursor: str | None) -> dict[str, Any] | None:
    if not cursor:
        return None

    try:
        payload = json.loads(cursor)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Invalid cursor.") from exc

    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Invalid cursor.")

    return payload


def score_expression() -> dict[str, Any]:
    return {
        "$add": [
            {"$ifNull": ["$metrics.favorite_count", 0]},
            {"$multiply": [{"$ifNull": ["$metrics.retweet_count", 0]}, 2]},
            {"$ifNull": ["$metrics.reply_count", 0]},
        ]
    }


def project_feed_document() -> dict[str, Any]:
    return {
        "_id": 0,
        "id": 1,
        "created_at": 1,
        "text": 1,
        "lang": 1,
        "tweet_type": 1,
        "user": 1,
        "reply": 1,
        "retweeted_status_id": 1,
        "quoted_status_id": 1,
        "place": 1,
        "hashtags": 1,
        "metrics": 1,
        "raw": 1,
    }


@app.get("/api/tweets")
def read_tweets_feed(
    sort: Literal["latest", "popular"] = Query(default="latest"),
    limit: int = Query(default=20, ge=1, le=100),
    cursor: str | None = Query(default=None),
):
    cursor_data = decode_cursor(cursor)
    fetch_limit = limit + 1

    if sort == "latest":
        pipeline: list[dict[str, Any]] = []

        if cursor_data is not None:
            cursor_created_at = cursor_data.get("created_at")
            cursor_id = cursor_data.get("id")

            if not isinstance(cursor_created_at, str) or not isinstance(cursor_id, int):
                raise HTTPException(status_code=400, detail="Invalid cursor.")

            try:
                created_at_value = datetime.fromisoformat(cursor_created_at)
            except ValueError as exc:
                raise HTTPException(status_code=400, detail="Invalid cursor.") from exc

            pipeline.append(
                {
                    "$match": {
                        "$or": [
                            {"created_at": {"$lt": created_at_value}},
                            {"created_at": created_at_value, "id": {"$lt": cursor_id}},
                        ]
                    }
                }
            )

        pipeline.extend(
            [
                {"$sort": {"created_at": -1, "id": -1}},
                {"$limit": fetch_limit},
                {"$project": project_feed_document()},
            ]
        )

        docs = list(tweets.aggregate(pipeline, allowDiskUse=True))

    elif sort == "popular":
        pipeline = [
            {"$addFields": {"score": score_expression()}},
        ]

        if cursor_data is not None:
            cursor_score = cursor_data.get("score")
            cursor_created_at = cursor_data.get("created_at")
            cursor_id = cursor_data.get("id")

            if not isinstance(cursor_score, int) or not isinstance(cursor_created_at, str) or not isinstance(cursor_id, int):
                raise HTTPException(status_code=400, detail="Invalid cursor.")

            try:
                created_at_value = datetime.fromisoformat(cursor_created_at)
            except ValueError as exc:
                raise HTTPException(status_code=400, detail="Invalid cursor.") from exc

            pipeline.append(
                {
                    "$match": {
                        "$or": [
                            {"score": {"$lt": cursor_score}},
                            {
                                "score": cursor_score,
                                "created_at": {"$lt": created_at_value},
                            },
                            {
                                "score": cursor_score,
                                "created_at": created_at_value,
                                "id": {"$lt": cursor_id},
                            },
                        ]
                    }
                }
            )

        pipeline.extend(
            [
                {"$sort": {"score": -1, "created_at": -1, "id": -1}},
                {"$limit": fetch_limit},
                {"$project": {**project_feed_document(), "score": 1}},
            ]
        )

        docs = list(tweets.aggregate(pipeline, allowDiskUse=True))

    else:
        raise HTTPException(status_code=400, detail="Unsupported sort order.")

    has_more = len(docs) > limit
    page = docs[:limit]

    next_cursor = None
    if has_more and page:
        last_doc = page[-1]

        if sort == "latest":
            next_cursor = encode_cursor(
                {
                    "created_at": last_doc["created_at"].isoformat(),
                    "id": int(last_doc["id"]),
                }
            )
        else:
            next_cursor = encode_cursor(
                {
                    "score": int(last_doc["score"]),
                    "created_at": last_doc["created_at"].isoformat(),
                    "id": int(last_doc["id"]),
                }
            )

    if sort == "popular":
        for item in page:
            item.pop("score", None)

    return {"data": page, "nextCursor": next_cursor}

def query_top_country():
    pipeline = [
        {"$match": {
            "place": {"$ne": None},
            "place.country": {"$ne": None}
        }},
        {"$group": {
            "_id": "$place.country",
            "tweet_count": {"$sum": 1}
        }},
        {"$sort": {"tweet_count": -1}},
        {"$limit": 1},
        {"$project": {"_id": 0, "country": "$_id", "tweet_count": 1}}
    ]
    return list(tweets.aggregate(pipeline))

def query_most_active_user():
    pipeline = [
        {"$match": {"user.id": {"$ne": None}}},
        {"$group": {
            "_id": "$user.id",
            "user_name": {"$first": "$user.name"},
            "screen_name": {"$first": "$user.screen_name"},
            "tweet_count": {"$sum": 1}
        }},
        {"$sort": {"tweet_count": -1}},
        {"$limit": 1},
        {"$project": {
            "_id": 0,
            "user_id": "$_id",
            "user_name": 1,
            "screen_name": 1,
            "tweet_count": 1
        }}
    ]
    return list(tweets.aggregate(pipeline))


def query_top_hashtags(limit=100):

    pipeline = [
        {"$match": {"hashtags.0": {"$exists": True}}},
        {"$unwind": "$hashtags"},
        {"$project": {
            "tweet_id": "$id",
            "tag": {"$toLower": "$hashtags"}
        }},
        {"$group": {"_id": {"tweet_id": "$tweet_id", "tag": "$tag"}}}, #multiple tags per tweet, either the same twice, or some other
        {"$group": {"_id": "$_id.tag", "tweet_count": {"$sum": 1}}},
        {"$sort": {"tweet_count": -1}},
        {"$limit": limit},
        {"$project": {"_id": 0, "hashtag": "$_id", "tweet_count": 1}}
    ]
    return list(tweets.aggregate(pipeline, allowDiskUse=True))