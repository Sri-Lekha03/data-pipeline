from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pipeline.schema import Event


def normalize_timestamp(ts: datetime) -> str:
    """Convert any datetime to UTC ISO-8601 string."""
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return ts.astimezone(timezone.utc).isoformat()


def flatten_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    """Flatten nested metadata dict into top-level keys with __ separator."""
    flat: dict[str, Any] = {}
    for key, value in metadata.items():
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                flat[f"{key}__{sub_key}"] = sub_value
        else:
            flat[key] = value
    return flat


def transform_event(event: Event) -> dict[str, Any]:
    """Transform a valid Event into a flat dict ready for Parquet writing."""
    flat_metadata = flatten_metadata(event.metadata)

    record: dict[str, Any] = {
        "event_id": str(event.event_id),
        "event_type": event.event_type,
        "user_id": event.user_id,
        "timestamp": normalize_timestamp(event.timestamp),
        "value": event.value,
        "processed_at": datetime.now(timezone.utc).isoformat(),
        **flat_metadata,
    }

    return record


def get_partition_path(event: Event) -> str:
    """Return the S3 partition path for an event."""
    ts = event.timestamp
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    ts = ts.astimezone(timezone.utc)

    return (
        f"event_type={event.event_type}/"
        f"year={ts.year}/"
        f"month={ts.month:02d}/"
        f"day={ts.day:02d}/"
    )