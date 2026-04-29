from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED_FIELDS = {"created_at", "id", "id_str", "text", "user"}
ENTITY_REQUIRED_FIELDS = {"hashtags"}
USER_REQUIRED_FIELDS = {"id", "name", "screen_name"}


def is_valid_record(record: object) -> bool:
	if not isinstance(record, dict):
		return False
	if not REQUIRED_FIELDS.issubset(record):
		return False

	user = record.get("user")
	if not isinstance(user, dict) or not USER_REQUIRED_FIELDS.issubset(user):
		return False

	entities = record.get("entities")
	if not isinstance(entities, dict) or not ENTITY_REQUIRED_FIELDS.issubset(entities):
		return False

	hashtags = entities.get("hashtags")
	if not isinstance(hashtags, list):
		return False
	for hashtag in hashtags:
		if not isinstance(hashtag, dict) or "text" not in hashtag:
			return False

	return True


def normalize_record(record: dict) -> dict:
	normalized = dict(record)
	metrics = {}
	metrics_source = normalized.get("retweeted_status")
	if not isinstance(metrics_source, dict):
		metrics_source = normalized.get("quoted_status")
	if not isinstance(metrics_source, dict):
		metrics_source = normalized

	favorite_count = metrics_source.get("favorite_count")
	if favorite_count is not None:
		metrics["likes"] = favorite_count
		metrics["favorites"] = favorite_count

	reply_count = metrics_source.get("reply_count")
	if reply_count is not None:
		metrics["replies"] = reply_count

	retweet_count = metrics_source.get("retweet_count")
	if retweet_count is not None:
		metrics["retweets"] = retweet_count

	if metrics:
		normalized["metrics"] = metrics

	return normalized


def clean_file(input_path: Path, output_path: Path) -> tuple[int, int]:
	kept = 0
	skipped = 0
	seen_ids = set()

	with input_path.open("r", encoding="utf-8", errors="replace") as source, output_path.open(
		"w", encoding="utf-8", newline="\n"
	) as destination:
		for raw_line in source:
			line = raw_line.strip().lstrip("\ufeff")
			if not line:
				continue

			try:
				record = json.loads(line)
			except json.JSONDecodeError:
				skipped += 1
				continue

			if not is_valid_record(record):
				skipped += 1
				continue

			record_id = record.get("id")
			if record_id in seen_ids:
				skipped += 1
				continue
			seen_ids.add(record_id)

			destination.write(json.dumps(normalize_record(record), ensure_ascii=False, separators=(",", ":")))
			destination.write("\n")
			kept += 1

	return kept, skipped


def build_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(description="Clean a newline-delimited Twitter JSON export.")
	parser.add_argument(
		"input",
		nargs="?",
		default="dataset/Eurovision3.json",
		help="Path to the raw JSONL file.",
	)
	parser.add_argument(
		"output",
		nargs="?",
		help="Path to the cleaned output file. Defaults to <input>.cleaned.json.",
	)
	return parser


def main() -> None:
	parser = build_parser()
	args = parser.parse_args()

	input_path = Path(args.input)
	output_path = Path(args.output) if args.output else input_path.with_name(f"{input_path.stem}.cleaned.json")

	kept, skipped = clean_file(input_path, output_path)
	print(f"Wrote {kept} cleaned records to {output_path}")
	print(f"Skipped {skipped} invalid, incomplete, or duplicate records")


if __name__ == "__main__":
	main()
