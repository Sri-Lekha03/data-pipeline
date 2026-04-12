from __future__ import annotations

import io
import json
from datetime import datetime, timezone
from typing import Any

import boto3
import pyarrow as pa
import pyarrow.parquet as pq


def write_parquet_to_s3(
    records: list[dict[str, Any]],
    bucket: str,
    partition_path: str,
    filename: str = "data.parquet",
) -> str:
    """Write records as Snappy-compressed Parquet to S3."""
    table = pa.Table.from_pylist(records)

    buffer = io.BytesIO()
    pq.write_table(table, buffer, compression="snappy")
    buffer.seek(0)

    key = f"processed/{partition_path}{filename}"

    s3 = boto3.client("s3")
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=buffer.getvalue(),
    )

    return key


def write_dead_letter_to_s3(
    raw: dict[str, Any],
    error: str,
    bucket: str,
    source_key: str,
) -> str:
    """Write an invalid record to the dead-letter prefix in S3."""
    payload = {
        "raw": raw,
        "error": error,
        "failed_at": datetime.now(timezone.utc).isoformat(),
        "source_key": source_key,
    }

    key = f"dead-letter/{source_key}"

    s3 = boto3.client("s3")
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(payload),
        ContentType="application/json",
    )

    return key