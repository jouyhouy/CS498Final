import os
import sys
from datetime import datetime
from typing import Any, Literal

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from dotenv import load_dotenv

success: bool = load_dotenv()
if not success:
    print("Failed to load .env file")
    sys.exit(1)

client: MongoClient = MongoClient(os.getenv("MONGODB_URI"))
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