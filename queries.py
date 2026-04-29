import os
from pymongo import MongoClient

MONGO_URL = "mongodb://127.0.0.1:27017"
MONGO = os.getenv("MONGO", MONGO_URL)
client = MongoClient(MONGO, serverSelectionTimeoutMS=5000)
db = client.twitter_project
tweets = db.tweets
def engagement_breakdown(limit=None):
    pipeline = [
        {"$match": {"user.verified": True}},
        {"$group": {
            "_id": "$user.id",
            "user_name":   {"$first": "$user.name"},
            "screen_name": {"$first": "$user.screen_name"},
            "total":   {"$sum": 1},
            "retweets":{"$sum": {"$cond": [{"$eq": ["$tweet_type", "retweet"]}, 1, 0]}},
            "quotes":  {"$sum": {"$cond": [{"$eq": ["$tweet_type", "quote"]},   1, 0]}},
            "replies": {"$sum": {"$cond": [{"$eq": ["$tweet_type", "reply"]},   1, 0]}},
            "simples": {"$sum": {"$cond": [{"$eq": ["$tweet_type", "tweet"]},   1, 0]}},
        }},
        {"$project": {
            "_id": 0,
            "user_name": 1,
            "screen_name": 1,
            "total_tweets": "$total",
            "simple_percent":  {"$multiply": [{"$divide": ["$simples",  "$total"]}, 100]},
            "retweet_percent": {"$multiply": [{"$divide": ["$retweets", "$total"]}, 100]},
            "quote_percent":   {"$multiply": [{"$divide": ["$quotes",   "$total"]}, 100]},
            "reply_percent":   {"$multiply": [{"$divide": ["$replies",  "$total"]}, 100]},
        }},
        {"$sort": {"total_tweets": -1}}
    ]
    if limit:
        pipeline.append({"$limit": limit})
    return list(tweets.aggregate(pipeline))



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