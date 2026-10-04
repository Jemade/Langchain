"""Consistent SQLite online backups to an operator-owned, private S3 bucket."""

import argparse
import sqlite3
import tempfile
from pathlib import Path

import boto3


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", default="runtime")
    parser.add_argument("--bucket", required=True)
    args = parser.parse_args()
    s3 = boto3.client("s3")
    for name in ("requests.sqlite", "checkpoints.sqlite"):
        source = Path(args.directory) / name
        if not source.is_file():
            raise SystemExit(f"Missing database: {source}")
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / name
            with sqlite3.connect(source) as src, sqlite3.connect(target) as dst:
                src.backup(dst)
            s3.upload_file(
                str(target),
                args.bucket,
                "backups/" + name,
                ExtraArgs={"ServerSideEncryption": "AES256"},
            )
    print("Backups uploaded. Restore requires the service to be stopped.")


if __name__ == "__main__":
    main()
