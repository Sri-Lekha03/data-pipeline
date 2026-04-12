from __future__ import annotations

import json
from uuid import uuid4

import boto3
import pytest
from moto import mock_aws

from pipeline.handler import run_pipeline


SOURCE_BUCKET = "test-source"
DEST_BUCKET = "test-dest"


def make_raw_event(**kwargs) -> dict:
    base = {
        "event_id": str(uuid4()),
        "event_type": "click",
        "user_id": "user_123",
        "timestamp": "2026-04-11T10:00:00",
        "metadata": {"source": "web", "geo": {"city": "NY"}},
        "value": 9.99,
    }
    base.update(kwargs)
    return base


@pytest.fixture
def aws_setup(aws_credentials):
    """Create mock S3 buckets and upload test data."""
    with mock_aws():
        s3 = boto3.client("s3", region_name="us-east-1")

        # Create buckets
        s3.create_bucket(Bucket=SOURCE_BUCKET)
        s3.create_bucket(Bucket=DEST_BUCKET)

        yield s3


def upload_events(s3, events: list[dict], prefix: str = "raw/2026/04/11/") -> None:
    """Upload a list of events as newline-delimited JSON to S3."""
    body = "\n".join(json.dumps(e) for e in events)
    s3.put_object(
        Bucket=SOURCE_BUCKET,
        Key=f"{prefix}events.json",
        Body=body,
    )


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_pipeline_processes_valid_records(aws_setup):
    """Valid records should be processed and written as Parquet."""
    s3 = aws_setup
    events = [make_raw_event() for _ in range(3)]
    upload_events(s3, events)

    with mock_aws():
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket=SOURCE_BUCKET)
        s3.create_bucket(Bucket=DEST_BUCKET)

        body = "\n".join(json.dumps(e) for e in events)
        s3.put_object(
            Bucket=SOURCE_BUCKET,
            Key="raw/2026/04/11/events.json",
            Body=body,
        )

        result = run_pipeline(
            source_bucket=SOURCE_BUCKET,
            dest_bucket=DEST_BUCKET,
            prefix="raw/2026/04/11/",
        )

    assert result["records_processed"] == 3
    assert result["records_failed"] == 0


def test_pipeline_sends_invalid_to_dead_letter(aws_credentials):
    """Invalid records should go to dead-letter and not be processed."""
    with mock_aws():
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket=SOURCE_BUCKET)
        s3.create_bucket(Bucket=DEST_BUCKET)

        invalid_event = {"bad_field": "no_schema_match"}
        body = json.dumps(invalid_event)
        s3.put_object(
            Bucket=SOURCE_BUCKET,
            Key="raw/2026/04/11/events.json",
            Body=body,
        )

        result = run_pipeline(
            source_bucket=SOURCE_BUCKET,
            dest_bucket=DEST_BUCKET,
            prefix="raw/2026/04/11/",
        )

    assert result["records_failed"] == 1
    assert result["records_processed"] == 0


def test_pipeline_mixed_records(aws_credentials):
    """Mix of valid and invalid records should be handled correctly."""
    with mock_aws():
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket=SOURCE_BUCKET)
        s3.create_bucket(Bucket=DEST_BUCKET)

        events = [
            make_raw_event(),                          # valid
            {"bad": "record"},                         # invalid
            make_raw_event(event_type="purchase"),     # valid
            make_raw_event(value=None),                # valid - null value
            make_raw_event(event_type="unknown_type"), # invalid
        ]

        body = "\n".join(json.dumps(e) for e in events)
        s3.put_object(
            Bucket=SOURCE_BUCKET,
            Key="raw/2026/04/11/events.json",
            Body=body,
        )

        result = run_pipeline(
            source_bucket=SOURCE_BUCKET,
            dest_bucket=DEST_BUCKET,
            prefix="raw/2026/04/11/",
        )

    assert result["records_processed"] == 3
    assert result["records_failed"] == 2