from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from pipeline.schema import Event
from pipeline.transform import (
    flatten_metadata,
    get_partition_path,
    normalize_timestamp,
    transform_event,
)


# ── normalize_timestamp ───────────────────────────────────────────────────────

def test_normalize_timestamp_naive():
    """Naive datetime should be treated as UTC."""
    ts = datetime(2026, 4, 11, 10, 30, 0)
    result = normalize_timestamp(ts)
    assert result == "2026-04-11T10:30:00+00:00"


def test_normalize_timestamp_with_tz():
    """Timezone-aware datetime should be converted to UTC."""
    from datetime import timedelta
    tz = timezone(timedelta(hours=5))
    ts = datetime(2026, 4, 11, 15, 30, 0, tzinfo=tz)
    result = normalize_timestamp(ts)
    assert result == "2026-04-11T10:30:00+00:00"


# ── flatten_metadata ──────────────────────────────────────────────────────────

def test_flatten_metadata_flat():
    """Already flat metadata should be unchanged."""
    result = flatten_metadata({"key": "value"})
    assert result == {"key": "value"}


def test_flatten_metadata_nested():
    """Nested dicts should be flattened with __ separator."""
    result = flatten_metadata({"geo": {"city": "NY", "country": "US"}})
    assert result == {"geo__city": "NY", "geo__country": "US"}


def test_flatten_metadata_empty():
    """Empty metadata should return empty dict."""
    assert flatten_metadata({}) == {}


# ── transform_event ───────────────────────────────────────────────────────────

def make_event(**kwargs) -> Event:
    defaults = {
        "event_id": uuid4(),
        "event_type": "click",
        "user_id": "user_123",
        "timestamp": datetime(2026, 4, 11, 10, 0, 0),
        "metadata": {"source": "web"},
        "value": 9.99,
    }
    defaults.update(kwargs)
    return Event(**defaults)


def test_transform_event_keys():
    """Transformed record must contain required keys."""
    event = make_event()
    result = transform_event(event)
    assert "event_id" in result
    assert "processed_at" in result
    assert "timestamp" in result
    assert "source" in result  # flattened metadata


def test_transform_event_null_value():
    """value=None should be preserved."""
    event = make_event(value=None)
    result = transform_event(event)
    assert result["value"] is None


# ── get_partition_path ────────────────────────────────────────────────────────

@pytest.mark.parametrize("event_type,expected", [
    ("click",    "event_type=click/year=2026/month=04/day=11/"),
    ("view",     "event_type=view/year=2026/month=04/day=11/"),
    ("purchase", "event_type=purchase/year=2026/month=04/day=11/"),
])
def test_get_partition_path(event_type, expected):
    event = make_event(
        event_type=event_type,
        timestamp=datetime(2026, 4, 11, tzinfo=timezone.utc),
    )
    assert get_partition_path(event) == expected