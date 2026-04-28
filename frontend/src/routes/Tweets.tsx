import { useEffect, useMemo, useRef, useState } from "react";
import { useInfiniteQuery } from "@tanstack/react-query";
import {
	Alert,
	Badge,
	Button,
	Card,
	CardBody,
	Col,
	Container,
	Row,
	Spinner,
} from "reactstrap";
import type { TweetDocument, TweetDocuments } from "../models/Tweets";

type FeedSort = "latest" | "popular";

interface TweetsPage {
	data: TweetDocuments;
	nextCursor: string | null;
}

interface RawTweetsResponse {
	data?: TweetDocuments;
	tweets?: TweetDocuments;
	nextCursor?: string | null;
}

const PAGE_SIZE = 20;

const popularityScore = (tweet: TweetDocument): number => {
	const favoriteCount = tweet.metrics?.favorite_count ?? 0;
	const retweetCount = tweet.metrics?.retweet_count ?? 0;
	const replyCount = tweet.metrics?.reply_count ?? 0;

	return favoriteCount + retweetCount * 2 + replyCount;
};

const toRelativeTime = (createdAt: string): string => {
	const date = new Date(createdAt);
	const deltaSeconds = Math.round((date.getTime() - Date.now()) / 1000);
	const formatter = new Intl.RelativeTimeFormat("en", { numeric: "auto" });

	const units: Array<[Intl.RelativeTimeFormatUnit, number]> = [
		["year", 60 * 60 * 24 * 365],
		["month", 60 * 60 * 24 * 30],
		["week", 60 * 60 * 24 * 7],
		["day", 60 * 60 * 24],
		["hour", 60 * 60],
		["minute", 60],
		["second", 1],
	];

	for (const [unit, secondsInUnit] of units) {
		if (Math.abs(deltaSeconds) >= secondsInUnit || unit === "second") {
			return formatter.format(Math.round(deltaSeconds / secondsInUnit), unit);
		}
	}

	return formatter.format(deltaSeconds, "second");
};

const fetchTweetsPage = async ({
	pageParam,
	sort,
}: {
	pageParam: string | null;
	sort: FeedSort;
}): Promise<TweetsPage> => {
	const params = new URLSearchParams();
	params.set("limit", String(PAGE_SIZE));
	params.set("sort", sort);

	if (pageParam) {
		params.set("cursor", pageParam);
	}

	const response = await fetch(`/api/tweets?${params.toString()}`);

	if (!response.ok) {
		throw new Error("Unable to load tweets feed.");
	}

	const raw = (await response.json()) as RawTweetsResponse | TweetDocuments;

	// Supports either array responses or paginated object responses.
	if (Array.isArray(raw)) {
		const fallbackCursor = raw.length === PAGE_SIZE ? String(raw[raw.length - 1]?.id ?? "") : null;
		return { data: raw, nextCursor: fallbackCursor || null };
	}

	const data = raw.data ?? raw.tweets ?? [];
	const fallbackCursor = data.length === PAGE_SIZE ? String(data[data.length - 1]?.id ?? "") : null;

	return {
		data,
		nextCursor: raw.nextCursor ?? fallbackCursor,
	};
};

const Tweets = (): React.JSX.Element => {
	const [sort, setSort] = useState<FeedSort>("latest");
	const loadMoreRef = useRef<HTMLDivElement | null>(null);

	const {
		data,
		error,
		fetchNextPage,
		hasNextPage,
		isFetching,
		isFetchingNextPage,
		isLoading,
	} = useInfiniteQuery({
		queryKey: ["tweets-feed", sort],
		queryFn: ({ pageParam }) => fetchTweetsPage({ pageParam, sort }),
		initialPageParam: null as string | null,
		getNextPageParam: (lastPage) => lastPage.nextCursor,
	});

	const tweets = useMemo(() => {
		const merged = data?.pages.flatMap((page) => page.data) ?? [];

		if (sort === "latest") {
			return [...merged].sort(
				(a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
			);
		}

		return [...merged].sort((a, b) => {
			const scoreDifference = popularityScore(b) - popularityScore(a);

			if (scoreDifference !== 0) {
				return scoreDifference;
			}

			return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
		});
	}, [data?.pages, sort]);

	useEffect(() => {
		if (!loadMoreRef.current || !hasNextPage) {
			return;
		}

		const observer = new IntersectionObserver(
			(entries) => {
				const [entry] = entries;
				if (entry.isIntersecting && !isFetchingNextPage) {
					void fetchNextPage();
				}
			},
			{ rootMargin: "250px" },
		);

		observer.observe(loadMoreRef.current);

		return () => observer.disconnect();
	}, [fetchNextPage, hasNextPage, isFetchingNextPage]);

	return (
		<Container className="py-4">
			<Row className="mb-3 align-items-center">
				<Col>
					<h2 className="mb-0">Tweet Timeline</h2>
				</Col>
				<Col xs="auto" className="d-flex gap-2">
					<Button
						color={sort === "latest" ? "primary" : "secondary"}
						onClick={() => setSort("latest")}
					>
						Latest
					</Button>
					<Button
						color={sort === "popular" ? "primary" : "secondary"}
						onClick={() => setSort("popular")}
					>
						Popular
					</Button>
				</Col>
			</Row>

			{isLoading && (
				<div className="py-5 text-center">
					<Spinner color="primary" />
					<p className="mt-2 mb-0">Loading tweets...</p>
				</div>
			)}

			{error instanceof Error && (
				<Alert color="danger">{error.message}</Alert>
			)}

			{!isLoading && !error && tweets.length === 0 && (
				<Alert color="light" className="text-start">
					No tweets were returned by the API.
				</Alert>
			)}

			<div className="d-flex flex-column gap-3">
				{tweets.map((tweet) => (
					<Card key={tweet.id} className="text-start">
						<CardBody>
							<div className="d-flex justify-content-between flex-wrap gap-2">
								<div>
									<strong>{tweet.user.name}</strong>{" "}
									<span className="text-muted">@{tweet.user.screen_name}</span>{" "}
									{tweet.user.verified && <Badge color="info">Verified</Badge>}
								</div>
								<small className="text-muted">{toRelativeTime(tweet.created_at)}</small>
							</div>

							<p className="mt-2 mb-3">{tweet.text}</p>

							<div className="d-flex gap-2 flex-wrap">
								<Badge pill color="light" className="text-dark border">
									Replies: {tweet.metrics?.reply_count ?? 0}
								</Badge>
								<Badge pill color="light" className="text-dark border">
									Retweets: {tweet.metrics?.retweet_count ?? 0}
								</Badge>
								<Badge pill color="light" className="text-dark border">
									Likes: {tweet.metrics?.favorite_count ?? 0}
								</Badge>
								<Badge pill color="secondary">
									Score: {popularityScore(tweet)}
								</Badge>
							</div>
						</CardBody>
					</Card>
				))}
			</div>

			<div ref={loadMoreRef} className="py-4 text-center">
				{isFetchingNextPage && (
					<>
						<Spinner size="sm" color="primary" />
						<span className="ms-2">Loading more...</span>
					</>
				)}

				{!hasNextPage && tweets.length > 0 && (
					<small className="text-muted">You have reached the end of the feed.</small>
				)}

				{hasNextPage && !isFetchingNextPage && (
					<Button color="link" onClick={() => void fetchNextPage()}>
						Load more
					</Button>
				)}

				{isFetching && !isFetchingNextPage && (
					<small className="text-muted d-block">Refreshing feed...</small>
				)}
			</div>
		</Container>
	);
};

export default Tweets;
