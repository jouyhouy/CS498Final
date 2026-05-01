import json
import os
from datetime import datetime
from typing import Any, Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from queries import query_top_countries, query_most_active_user, query_top_hashtags
from models.TweetModels import HashtagCount, HashtagCount, TweetDocument, TopCountry, UserTweetCount

load_dotenv()

mongodb_uri = os.getenv("MONGODB_URI")
if not mongodb_uri:
    raise RuntimeError("MONGODB_URI is not set.")

client: MongoClient = MongoClient(mongodb_uri)
db: Database = client["twitter"]
tweets: Collection[dict[str, Any]] = db["tweets"]


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

@app.get("/api/most-active-user", response_model=list[UserTweetCount])
def get_most_active_users():
    users = query_most_active_user(tweets)
    return [
        UserTweetCount.model_validate(user)
        for user in users
    ]


@app.get("/api/tweets-by-user", response_model=list[TweetDocument])
def get_tweets_by_user(username: str) -> list[TweetDocument]:
    user_tweets = tweets.find(
        {"user.screen_name": {"$regex": username.lower(), "$options": "i"}}
    )
    return [TweetDocument.model_validate(tweet) for tweet in user_tweets]


@app.get("/api/top-countries", response_model=list[TopCountry])
def get_top_countries():
    countries: list[TopCountry] = query_top_countries(tweets)
    return countries

@app.get("/api/top-hashtags", response_model=list[HashtagCount])
def get_top_hashtags(limit: int = 100):
    return [HashtagCount.model_validate(hashtag) for hashtag in query_top_hashtags(tweets, limit=limit)]