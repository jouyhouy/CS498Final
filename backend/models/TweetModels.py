from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime
from typing import Any, Literal

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


class ThreadTweet(BaseModel):
    tweet: str
    time: Any
    id: int
    in_reply_to_id: int | None = None
    user_name: str
    screen_name: str


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
    id_: str | None = Field(default=None, alias="_id")
    id: int
    created_at: datetime
    text: str
    lang: str | None = None
    tweet_type: Literal["simple", "reply", "retweet", "quote"] | None = None
    user: TweetUser
    reply: TweetReply | None = None
    in_reply_to_status_id: int | None = None
    in_reply_to_user_id: int | None = None
    in_reply_to_screen_name: str | None = None
    retweeted_status_id: int | None = None
    quoted_status_id: int | None = None
    place: TweetPlace | None = None
    entities: TweetEntities
    metrics: TweetMetrics | None = None
    raw: dict[str, Any] | None = None

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("id_", mode="before")
    @classmethod
    def stringify_mongo_id(cls, value: Any) -> str | None:
        if value is None:
            return None

        return str(value)

    @field_validator("created_at", mode="before")
    @classmethod
    def parse_created_at(cls, value: Any) -> Any:
        if not isinstance(value, str):
            return value

        try:
            return datetime.strptime(value, "%a %b %d %H:%M:%S %z %Y")
        except ValueError:
            return value
        
class TopCountry(BaseModel):
    tweet_count: int
    country: str

class UserTweetCount(BaseModel):
    user_id: int
    user_name: str
    screen_name: str
    tweet_count: int

class HashtagCount(BaseModel):
    hashtag: str
    count: int

class EngagementBreakdown(BaseModel):
    user_name: str
    screen_name: str
    total_tweets: int
    simple_percent: float
    retweet_percent: float
    quote_percent: float
    reply_percent: float