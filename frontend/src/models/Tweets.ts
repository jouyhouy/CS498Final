export type TweetType = "simple" | "reply" | "retweet" | "quote";

export interface TweetUser {
	id: number;
	name: string;
	screen_name: string;
	verified: boolean;
}

export interface TweetReply {
	status_id: number | null;
	user_id: number | null;
	screen_name: string | null;
}

export interface TweetPlace {
	country: string | null;
	full_name: string | null;
	place_type: string | null;
}

export interface TweetMetrics {
	likes: number;
	favorites: number;
	replies: number;
	retweets: number;
}

export interface TweetDocument {
	_id: number;
	id: number;
	created_at: string;
	text: string;
	lang: string | null;
	tweet_type: TweetType;
	user: TweetUser;
	reply: TweetReply | null;
	retweeted_status_id: number | null;
	quoted_status_id: number | null;
	place: TweetPlace | null;
	hashtags: string[];
	metrics: TweetMetrics | null;
	raw: Record<string, unknown> | null;
}

export type TweetDocuments = TweetDocument[];
