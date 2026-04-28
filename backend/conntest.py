import os
import sys
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from dotenv import load_dotenv

#!/usr/bin/env python3
"""
conntest.py

Simple MongoDB connection tester. Reads MONGODB_URI from the environment and
attempts a ping to verify connectivity. Exits with status 0 on success, nonzero on failure.
"""

load_dotenv()

def main():
    uri = os.getenv("MONGODB_URI")
    if not uri:
        print("Environment variable MONGODB_URI is not set.", file=sys.stderr)
        sys.exit(2)

    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        # Ping the server to verify connection
        client.admin.command("ping")
        print("Successfully connected to MongoDB.")
        client.close()
        return 0
    except PyMongoError as e:
        print(f"Failed to connect to MongoDB: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())