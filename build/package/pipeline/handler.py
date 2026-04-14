from __future__ import annotations

import json
import uuid
from typing import Any

import boto3
from pydantic import ValidationError

from pipeline.metrics import PipelineMetrics
from pipeline.schema import Event
from pipeline.transform import get_partition_path, transform_event
from pipeline.writer import write_dead_letter_to_s3, write_parquet_to_s3


def process_file(
    s3_client: Any,
    source_bucket: str,
    dest_bucket: str,
    key: str,
    metrics: PipelineMetrics,
) -> list[dict[str, Any]]:
    """Read a single S3 file, validate and transform records."""
    response = s3_client.get_object(Bucket=source_bucket, Key=key)
    body = response["Body"].read().decode("utf-8")

    valid_records: list[dict[str, Any]] = []

    for line in body.strip().splitlines():
        try:
            raw = json.loads(line)
            event = Event.model_validate(raw)
            transformed = transform_event(event)
            partition = get_partition_path(event)
            transformed["_partition"] = partition
            valid_records.append(transformed)
            metrics.records_processed += 1

        except (ValidationError, json.JSONDecodeError) as e:
            metrics.records_failed += 1
            try:
                raw_dict = json.loads(line) if isinstance(line, str) else {}
            except Exception:
                raw_dict = {"raw_line": line}

            write_dead_letter_to_s3(
                raw=raw_dict,
                error=str(e),
                bucket=dest_bucket,
                source_key=f"{key}/{uuid.uuid4()}.json",
            )

    return valid_records


def group_by_partition(
    records: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    """Group transformed records by their partition path."""
    groups: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        partition = record.pop("_partition", "unknown/")
        groups.setdefault(partition, []).append(record)
    return groups


def run_pipeline(
    source_bucket: str,
    dest_bucket: str,
    prefix: str,
    cloudwatch_namespace: str = "DataPipeline",
) -> dict[str, Any]:
    """Main pipeline logic — usable by both Lambda and CLI."""
    s3 = boto3.client("s3")
    metrics = PipelineMetrics()

    # List all files under the prefix
    paginator = s3.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=source_bucket, Prefix=prefix)

    all_records: list[dict[str, Any]] = []

    for page in pages:
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if not key.endswith(".json"):
                continue
            records = process_file(s3, source_bucket, dest_bucket, key, metrics)
            all_records.extend(records)

    # Write grouped Parquet files
    grouped = group_by_partition(all_records)
    for partition, records in grouped.items():
        write_parquet_to_s3(
            records=records,
            bucket=dest_bucket,
            partition_path=partition,
        )

    # Emit metrics
    metrics.print_summary()
    try:
        metrics.emit_to_cloudwatch(namespace=cloudwatch_namespace)
    except Exception:
        pass  # Don't fail pipeline if CloudWatch is unavailable

    return metrics.to_dict()


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """AWS Lambda entrypoint — triggered by S3 ObjectCreated event."""
    record = event["Records"][0]
    source_bucket = record["s3"]["bucket"]["name"]
    key = record["s3"]["object"]["key"]

    # Extract date prefix from key: raw/YYYY/MM/DD/filename.json
    parts = key.split("/")
    prefix = "/".join(parts[:4]) + "/"

    import os
    dest_bucket = os.environ["DEST_BUCKET"]

    result = run_pipeline(
        source_bucket=source_bucket,
        dest_bucket=dest_bucket,
        prefix=prefix,
    )

    return {"statusCode": 200, "body": json.dumps(result)}