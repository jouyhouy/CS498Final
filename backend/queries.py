# Query 1
from pymongo.auth import Any
from pymongo.collection import Collection

from models.TweetModels import TopCountry, UserTweetCount


def query_top_countries(tweets_collection: Collection[dict[str, Any]]) -> list[TopCountry]:
    """
    Returns a list of countries ranked by the number of tweets originating from them.
    """
    pipeline = [
        {"$match": {"place.country": {"$exists": True, "$ne": None}}},
        {"$group": {"_id": "$place.country", "tweet_count": {"$sum": 1}}},
        {"$project": {"_id": 0, "country": "$_id", "tweet_count": 1}},
        {"$sort": {"tweet_count": -1}},
    ]

    return [
        TopCountry.model_validate(country)
        for country in tweets_collection.aggregate(pipeline, allowDiskUse=True)
    ]

# Query 2
def query_most_active_user(tweets_collection: Collection[dict[str, Any]]) -> list[UserTweetCount]:
    """
    Return a list of the most active user(s) based on tweet count.
    """
    pipeline = [
        {
            "$group": {
                "_id": "$user.id",
                "user_name": {"$first": "$user.name"},
                "screen_name": {"$first": "$user.screen_name"},
                "tweet_count": {"$sum": 1},
            }
        },
        {"$sort": {"tweet_count": -1}},
        {"$limit": 50},
        {
            "$project": {
                "_id": 0,
                "user_id": "$_id",
                "user_name": 1,
                "screen_name": 1,
                "tweet_count": 1,
            }
        },
    ]
    return [
        UserTweetCount.model_validate(user)
        for user in tweets_collection.aggregate(pipeline)
    ]

# Query 3
def query_top_hashtags(tweets_collection: Collection[dict[str, Any]],limit: int = 100):
    pipeline = [
        {"$unwind": "$entities.hashtags"},
        {"$addFields": {"normalizedHashtag": {"$toLower": "$entities.hashtags.text"}}},
        {"$group": {"_id": "$normalizedHashtag", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": limit},
        {"$project": {"_id": 0, "hashtag": "$_id", "count": 1}},
    ]
    return list(tweets_collection.aggregate(pipeline, allowDiskUse=True))
