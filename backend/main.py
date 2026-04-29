import json
import os
from datetime import datetime
from typing import Any, Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
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
db: Database = client["twitter"]
tweets: Collection[dict[str, Any]] = db["tweets"]
tweets.create_index([("created_at", -1), ("id", -1)], name="created_at_id_desc")
tweets.create_index([("favorite_count", -1), ("id", -1)], name="favorite_count_id_desc")

sample_created_at_document = tweets.find_one({"created_at": {"$exists": True}}, {"created_at": 1})
created_at_storage_is_datetime = bool(
    sample_created_at_document
    and isinstance(sample_created_at_document.get("created_at"), datetime)
)

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


class TweetHashtag(BaseModel):
    text: str


class TweetEntities(BaseModel):
    hashtags: list[TweetHashtag]
    urls: list[Any] | None = None
    user_mentions: list[Any] | None = None
    symbols: list[Any] | None = None


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
    tweet_type: Literal["simple", "reply", "retweet", "quote"] | None = None
    user: TweetUser
    reply: TweetReply | None = None
    retweeted_status_id: int | None = None
    quoted_status_id: int | None = None
    place: TweetPlace | None = None
    entities: TweetEntities
    metrics: TweetMetrics | None = None
    raw: dict[str, Any] | None = None

    model_config = ConfigDict(populate_by_name=True)



app = FastAPI()

cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ALLOW_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
            {
                "$ifNull": [
                    "$metrics.favorite_count",
                    {"$ifNull": ["$favorite_count", 0]},
                ]
            },
            {
                "$multiply": [
                    {
                        "$ifNull": [
                            "$metrics.retweet_count",
                            {"$ifNull": ["$retweet_count", 0]},
                        ]
                    },
                    2,
                ]
            },
            {
                "$ifNull": [
                    "$metrics.reply_count",
                    {"$ifNull": ["$reply_count", 0]},
                ]
            },
        ]
    }


def parse_cursor_created_at(value: str) -> datetime | str:
    if created_at_storage_is_datetime:
        return datetime.fromisoformat(value)

    return value


def cursor_created_at_to_text(value: datetime | str) -> str:
    if isinstance(value, datetime):
        return value.isoformat()

    return value


def build_latest_feed_query(cursor_data: dict[str, Any] | None) -> dict[str, Any]:
    if cursor_data is None:
        return {}

    cursor_created_at = cursor_data.get("created_at")
    cursor_id = cursor_data.get("id")

    if not isinstance(cursor_created_at, str) or not isinstance(cursor_id, int):
        raise HTTPException(status_code=400, detail="Invalid cursor.")

    try:
        created_at_value = parse_cursor_created_at(cursor_created_at)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid cursor.") from exc

    return {
        "$or": [
            {"created_at": {"$lt": created_at_value}},
            {"created_at": created_at_value, "id": {"$lt": cursor_id}},
        ]
    }


def build_likes_feed_query(cursor_data: dict[str, Any] | None) -> dict[str, Any]:
    if cursor_data is None:
        return {}

    cursor_favorite_count = cursor_data.get("favorite_count")
    cursor_id = cursor_data.get("id")

    if not isinstance(cursor_favorite_count, int) or not isinstance(cursor_id, int):
        raise HTTPException(status_code=400, detail="Invalid cursor.")

    return {
        "$or": [
            {"favorite_count": {"$lt": cursor_favorite_count}},
            {"favorite_count": cursor_favorite_count, "id": {"$lt": cursor_id}},
        ]
    }


def feed_projection() -> dict[str, Any]:
    return {
        "_id": 0,
        "id": 1,
        "created_at": 1,
        "favorite_count": 1,
        "text": 1,
        "lang": 1,
        "tweet_type": 1,
        "user": 1,
        "reply": 1,
        "retweeted_status_id": 1,
        "quoted_status_id": 1,
        "place": 1,
        "entities": 1,
        "hashtags": {
            "$map": {
                "input": {"$ifNull": ["$entities.hashtags", []]},
                "as": "hashtag",
                "in": "$$hashtag.text",
            }
        },
        "metrics": 1,
        "raw": 1,
    }


def normalize_feed_document(document: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(document)
    hashtags: list[str] = []

    raw_hashtags = normalized.get("hashtags")
    if isinstance(raw_hashtags, list) and all(isinstance(tag, str) for tag in raw_hashtags):
        hashtags = raw_hashtags
    else:
        entities = normalized.get("entities")
        if isinstance(entities, dict):
            entity_hashtags = entities.get("hashtags")
            if isinstance(entity_hashtags, list):
                for hashtag in entity_hashtags:
                    if isinstance(hashtag, dict):
                        text = hashtag.get("text")
                        if isinstance(text, str):
                            hashtags.append(text)

    normalized["hashtags"] = hashtags
    return normalized


@app.get("/api/tweets")
def read_tweets_feed(
    sort: Literal["latest", "likes", "popular"] = Query(default="latest"),
    limit: int = Query(default=20, ge=1, le=100),
    cursor: str | None = Query(default=None),
):
    cursor_data = decode_cursor(cursor)
    fetch_limit = limit + 1

    if sort == "latest":
        query = build_latest_feed_query(cursor_data)
        docs = list(
            tweets.find(query, projection=feed_projection())
            .sort([("created_at", -1), ("id", -1)])
            .limit(fetch_limit)
        )
        docs = [normalize_feed_document(document) for document in docs]

    elif sort in {"likes", "popular"}:
        query = build_likes_feed_query(cursor_data)
        docs = list(
            tweets.find(query, projection=feed_projection())
            .sort([("favorite_count", -1), ("id", -1)])
            .limit(fetch_limit)
        )
        docs = [normalize_feed_document(document) for document in docs]

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
                    "created_at": cursor_created_at_to_text(last_doc["created_at"]),
                    "id": int(last_doc["id"]),
                }
            )
        else:
            next_cursor = encode_cursor(
                {
                    "favorite_count": int(last_doc.get("favorite_count") or 0),
                    "id": int(last_doc["id"]),
                }
            )

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
        {"$addFields": {
            "hashtags": {
                "$map": {
                    "input": {"$ifNull": ["$entities.hashtags", []]},
                    "as": "hashtag",
                    "in": {"$toLower": "$$hashtag.text"}
                }
            }
        }},
        {"$match": {"hashtags.0": {"$exists": True}}},
        {"$unwind": "$hashtags"},
        {"$project": {
            "tweet_id": "$id",
            "tag": "$hashtags"
        }},
        {"$group": {"_id": {"tweet_id": "$tweet_id", "tag": "$tag"}}}, #multiple tags per tweet, either the same twice, or some other
        {"$group": {"_id": "$_id.tag", "tweet_count": {"$sum": 1}}},
        {"$sort": {"tweet_count": -1}},
        {"$limit": limit},
        {"$project": {"_id": 0, "hashtag": "$_id", "tweet_count": 1}}
    ]
    return list(tweets.aggregate(pipeline, allowDiskUse=True))