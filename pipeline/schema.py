from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


class Event(BaseModel):
    event_id: UUID
    event_type: Literal["click", "view", "purchase"]
    user_id: str
    timestamp: datetime
    metadata: dict[str, Any]
    value: float | None = None


class DeadLetterRecord(BaseModel):
    raw: dict[str, Any]
    error: str
    failed_at: datetime = Field(default_factory=datetime.utcnow)