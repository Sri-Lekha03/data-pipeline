from __future__ import annotations

from uuid import uuid4

import pytest
from pydantic import ValidationError

from pipeline.schema import Event


def valid_payload(**kwargs) -> dict:
    base = {
        "event_id": str(uuid4()),
        "event_type": "click",
        "user_id": "user_abc",
        "timestamp": "2026-04-11T10:00:00",
        "metadata": {"source": "web"},
        "value": 1.5,
    }
    base.update(kwargs)
    return base


def test_valid_event():
    event = Event.model_validate(valid_payload())
    assert event.event_type == "click"


def test_null_value_allowed():
    event = Event.model_validate(valid_payload(value=None))
    assert event.value is None


@pytest.mark.parametrize("event_type", ["click", "view", "purchase"])
def test_valid_event_types(event_type):
    event = Event.model_validate(valid_payload(event_type=event_type))
    assert event.event_type == event_type


def test_invalid_event_type():
    with pytest.raises(ValidationError):
        Event.model_validate(valid_payload(event_type="unknown"))


def test_malformed_timestamp():
    with pytest.raises(ValidationError):
        Event.model_validate(valid_payload(timestamp="not-a-date"))


def test_missing_required_field():
    payload = valid_payload()
    del payload["user_id"]
    with pytest.raises(ValidationError):
        Event.model_validate(payload)


def test_invalid_uuid():
    with pytest.raises(ValidationError):
        Event.model_validate(valid_payload(event_id="not-a-uuid"))