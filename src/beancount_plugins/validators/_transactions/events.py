from __future__ import annotations

from typing import TYPE_CHECKING

from .common import any_tag_starts_with
from .errors import EventError, EventTransactionError

if TYPE_CHECKING:
    from beancount.core import data

SIMPLE_EVENT_TYPES = frozenset({"address", "employment", "relationship"})
LINKED_EVENT_TYPES = frozenset({"trip", "work_trip"})
ALL_EVENT_TYPES = SIMPLE_EVENT_TYPES | LINKED_EVENT_TYPES


def validate_event(entry: data.Event) -> list[EventError]:
    if entry.type not in ALL_EVENT_TYPES:
        return [
            EventError(
                entry.meta,
                f"Event type '{entry.type}' is invalid",
                entry,
            )
        ]
    return []


def is_linked_event(entry: data.Event) -> bool:
    return entry.type in LINKED_EVENT_TYPES


def get_event_id(entry: data.Event, event_ids: list[str]) -> tuple[str | None, EventError | None]:
    if "id" not in entry.meta:
        return None, EventError(
            entry.meta,
            "Missing 'id' field in meta",
            entry,
        )

    event_id = entry.meta["id"]

    if event_id in event_ids:
        return event_id, EventError(
            entry.meta,
            "Duplicate event id",
            entry,
        )

    return event_id, None


def is_event_transaction(entry: data.Transaction) -> bool:
    return any_tag_starts_with(entry.tags, "event-")


def validate_event_transaction(entry: data.Transaction, event_ids: list[str]) -> list[EventTransactionError]:
    event_tags = [tag for tag in entry.tags if tag.startswith("event-")]

    if len(event_tags) > 1:
        return [
            EventTransactionError(
                entry.meta,
                "Cannot have multiple event tags",
                entry,
            )
        ]

    event_id = event_tags[0].removeprefix("event-")

    if event_id not in event_ids:
        return [
            EventTransactionError(
                entry.meta,
                "Linked event not found",
                entry,
            )
        ]

    return []
