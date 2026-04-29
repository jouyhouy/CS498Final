from __future__ import annotations

import argparse
import json
import os
from datetime import date, datetime
from pathlib import Path
from typing import Any

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import CollectionInvalid, PyMongoError
from dotenv import load_dotenv
from bson import Int64

load_dotenv()  # Load environment variables from .env file

MONGO_SCHEMA_VALIDATOR: dict[str, Any] = {
	"$jsonSchema": {
		"bsonType": "object",
		"title": "Tweet document validation",
		"required": ["id", "created_at", "text", "user", "entities"],
		"properties": {
			"id": {"bsonType": ["int", "long"]},
			"id_str": {"bsonType": ["string"]},
			"created_at": {"bsonType": ["string", "date"]},
			"timestamp_ms": {"bsonType": ["string", "long"]},
			"text": {"bsonType": "string"},
			"source": {"bsonType": ["string", "null"]},
			"truncated": {"bsonType": ["bool", "null"]},
			"in_reply_to_status_id": {"bsonType": ["int", "long", "null"]},
			"in_reply_to_user_id": {"bsonType": ["int", "long", "null"]},
			"in_reply_to_screen_name": {"bsonType": ["string", "null"]},
			"is_quote_status": {"bsonType": ["bool", "null"]},
			"quoted_status_id": {"bsonType": ["int", "long", "null"]},
			"quoted_status": {"bsonType": ["object", "null"]},
			"retweeted_status": {"bsonType": ["object", "null"]},
			"lang": {"bsonType": ["string", "null"]},
			"reply_count": {"bsonType": ["int", "long", "null"]},
			"retweet_count": {"bsonType": ["int", "long", "null"]},
			"favorite_count": {"bsonType": ["int", "long", "null"]},
			"quote_count": {"bsonType": ["int", "long", "null"]},
			"metrics": {
				"bsonType": ["object", "null"],
				"properties": {
					"likes": {"bsonType": ["int", "long", "null"]},
					"replies": {"bsonType": ["int", "long", "null"]},
					"retweets": {"bsonType": ["int", "long", "null"]},
					"favorites": {"bsonType": ["int", "long", "null"]},
				},
			},
			"user": {
				"bsonType": "object",
				"required": ["id", "name", "screen_name"],
				"properties": {
					"id": {"bsonType": ["int", "long"]},
					"id_str": {"bsonType": ["string", "null"]},
					"name": {"bsonType": "string"},
					"screen_name": {"bsonType": "string"},
					"verified": {"bsonType": ["bool", "null"]},
				},
			},
			"place": {
				"bsonType": ["object", "null"],
				"properties": {
					"country": {"bsonType": ["string", "null"]},
					"full_name": {"bsonType": ["string", "null"]},
					"place_type": {"bsonType": ["string", "null"]},
				},
			},
			"entities": {
				"bsonType": "object",
				"required": ["hashtags"],
				"properties": {
					"hashtags": {
						"bsonType": "array",
						"items": {"bsonType": "object", "properties": {"text": {"bsonType": "string"}}},
					},
					"urls": {"bsonType": ["array", "null"]},
					"user_mentions": {"bsonType": ["array", "null"]},
					"symbols": {"bsonType": ["array", "null"]},
				},
			},
		},
	}
}


def is_int_like(value: Any) -> bool:
	return isinstance(value, int) and not isinstance(value, bool)


def matches_bson_type(value: Any, bson_type: Any) -> bool:
	if isinstance(bson_type, list):
		return any(matches_bson_type(value, candidate) for candidate in bson_type)

	if bson_type == "null":
		return value is None
	if bson_type in {"int", "long"}:
		return is_int_like(value)
	if bson_type == "string":
		return isinstance(value, str)
	if bson_type == "bool":
		return isinstance(value, bool)
	if bson_type == "object":
		return isinstance(value, dict)
	if bson_type == "array":
		return isinstance(value, list)
	if bson_type == "date":
		return isinstance(value, (datetime, date))

	return False


def validate_schema(value: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
	errors: list[str] = []
	bson_type = schema.get("bsonType")
	if bson_type is not None and not matches_bson_type(value, bson_type):
		errors.append(f"{path}: expected {bson_type}, got {type(value).__name__}")
		return errors

	if isinstance(value, dict):
		required = schema.get("required", [])
		for field in required:
			if field not in value:
				errors.append(f"{path}.{field}: missing required field")

		properties = schema.get("properties", {})
		for field, field_schema in properties.items():
			if field in value:
				errors.extend(validate_schema(value[field], field_schema, f"{path}.{field}"))

	elif isinstance(value, list):
		item_schema = schema.get("items")
		if isinstance(item_schema, dict):
			for index, item in enumerate(value):
				errors.extend(validate_schema(item, item_schema, f"{path}[{index}]"))

	return errors


def is_valid_tweet_document(record: Any) -> tuple[bool, list[str]]:
	if not isinstance(record, dict):
		return False, ["record is not a JSON object"]

	schema = MONGO_SCHEMA_VALIDATOR["$jsonSchema"]
	errors = validate_schema(record, schema)
	return not errors, errors


def ensure_tweets_collection(collection: Collection) -> None:
	validator = MONGO_SCHEMA_VALIDATOR
	command = {
		"collMod": collection.name,
		"validator": validator,
		"validationLevel": "strict",
		"validationAction": "error",
	}

	try:
		collection.database.command(command)
		return
	except PyMongoError:
		pass

	try:
		collection.database.create_collection(
			collection.name,
			validator=validator,
			validationLevel="strict",
			validationAction="error",
		)
		create_tweets_indexes(collection)
	except CollectionInvalid:
		pass


def create_tweets_indexes(collection: Collection) -> None:
	collection.create_index([("id", 1)], unique=True)
	collection.create_index([("user.screen_name", 1), ("created_at", 1)])
	collection.create_index([("in_reply_to_status_id", 1)])
	collection.create_index([("user.id", 1)])
	collection.create_index([("user.verified", 1)])
	collection.create_index([("place.country", 1)])
	collection.create_index([("entities.hashtags.text", 1)])


def load_jsonl_file(
	input_path: Path,
	collection: Collection,
	progress_every: int = 1000,
) -> tuple[int, int, int]:
	inserted = 0
	skipped_invalid = 0
	skipped_parse = 0
	processed = 0
	batch: list[dict[str, Any]] = []
	batch_lines: list[int] = []
	batch_size = getattr(collection, "__batch_size", 1000)

	print(f"Starting import from {input_path}", flush=True)

	with input_path.open("r", encoding="utf-8", errors="replace") as source:
		for line_number, raw_line in enumerate(source, start=1):
			line = raw_line.strip().lstrip("\ufeff")
			if not line:
				continue

			processed += 1

			try:
				record = json.loads(line)
			except json.JSONDecodeError:
				skipped_parse += 1
				continue

			# Coerce numeric id/count fields to Int64 so MongoDB validators expecting long pass
			def _maybe_int64(val: Any) -> Any:
				if is_int_like(val):
					return Int64(val)
				return val

			# top-level ids/counts
			if "id" in record:
				record["id"] = _maybe_int64(record["id"])
			for key in ("in_reply_to_status_id", "in_reply_to_user_id", "quoted_status_id", "reply_count", "retweet_count", "favorite_count", "quote_count"):
				if key in record and record[key] is not None:
					record[key] = _maybe_int64(record[key])

			# user id
			if isinstance(record.get("user"), dict) and "id" in record["user"]:
				record["user"]["id"] = _maybe_int64(record["user"]["id"])

			# metrics
			if isinstance(record.get("metrics"), dict):
				for k in ("likes", "replies", "retweets", "favorites"):
					if k in record["metrics"] and record["metrics"][k] is not None:
						record["metrics"][k] = _maybe_int64(record["metrics"][k])

			is_valid, errors = is_valid_tweet_document(record)
			if not is_valid:
				skipped_invalid += 1
				print(f"Skipping line {line_number}: {'; '.join(errors)}")
				continue

			# add to batch and flush if needed
			batch.append(record)
			batch_lines.append(line_number)

			if len(batch) >= batch_size:
				try:
					result = collection.insert_many(batch, ordered=False)
					inserted += len(result.inserted_ids)
				except PyMongoError as exc:
					print(f"MongoDB rejected batch ending at line {line_number}: {exc}")
					skipped_invalid += len(batch)
				finally:
					batch = []
					batch_lines = []

			if progress_every > 0 and processed % progress_every == 0:
				print(
					(
						f"Progress for {input_path}: processed {processed} records, "
						f"inserted {inserted}, skipped {skipped_invalid} invalid, "
						f"skipped {skipped_parse} malformed"
					),
					flush=True,
				)

	return inserted, skipped_invalid, skipped_parse


def resolve_input_files(input_path: Path) -> list[Path]:
	if input_path.is_dir():
		return sorted(path for path in input_path.glob("*.json") if path.is_file())

	return [input_path]


def build_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(description="Import newline-delimited tweet JSON into MongoDB.")
	parser.add_argument(
		"input",
		nargs="?",
		default="cleaned_dataset",
		help="Path to a JSONL file or a directory containing JSONL files.",
	)
	parser.add_argument(
		"--db-conn",
		default=os.getenv("DB_CONN", os.getenv("MONGODB_URI", "mongodb://localhost:27017")),
		help="MongoDB connection string. Defaults to DB_CONN, then MONGODB_URI, then localhost.",
	)
	parser.add_argument("--database", default=os.getenv("MONGODB_DATABASE", "twitter"), help="Database name to use.")
	parser.add_argument("--collection", default="tweets", help="Collection name to insert into.")
	parser.add_argument(
		"--progress-every",
		type=int,
		default=1000,
		help="Print a progress update after this many non-empty input lines. Set to 0 to disable.",
	)
	return parser


def main() -> None:
	parser = build_parser()
	args = parser.parse_args()

	input_path = Path(args.input)
	input_files = resolve_input_files(input_path)
	client = MongoClient(args.db_conn)
	collection = client[args.database][args.collection]

	ensure_tweets_collection(collection)
	if not input_files:
		raise FileNotFoundError(f"No .json files found in {input_path}")

	total_inserted = 0
	total_skipped_invalid = 0
	total_skipped_parse = 0

	for file_path in input_files:
		inserted, skipped_invalid, skipped_parse = load_jsonl_file(file_path, collection, args.progress_every)
		total_inserted += inserted
		total_skipped_invalid += skipped_invalid
		total_skipped_parse += skipped_parse

	print(f"Inserted {total_inserted} documents into {args.database}.{args.collection}", flush=True)
	print(f"Skipped {total_skipped_invalid} schema-invalid records", flush=True)
	print(f"Skipped {total_skipped_parse} malformed JSON lines", flush=True)


if __name__ == "__main__":
	main()
