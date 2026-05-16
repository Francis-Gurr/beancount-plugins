"""Validate event directives and event-tagged transactions."""

from __future__ import annotations

from beancount.core import data

from .common import any_tag_starts_with
from .errors import EventError, EventTransactionError

PLUGIN_NAME = "validate_transactions"

SIMPLE_EVENT_TYPES = frozenset({"address", "employment", "relationship"})
LINKED_EVENT_TYPES = frozenset({"trip", "work_trip"})
ALL_EVENT_TYPES = SIMPLE_EVENT_TYPES | LINKED_EVENT_TYPES


def validate_event(entry: data.Event) -> list[EventError]:
    if entry.type in ALL_EVENT_TYPES:
        return []
    return [
        EventError(
            data.new_metadata(PLUGIN_NAME, entry.meta["lineno"]),
            f"Event type '{entry.type}' is invalid",
            entry,
        )
    ]


def is_linked_event(entry: data.Event) -> bool:
    return entry.type in LINKED_EVENT_TYPES


def get_event_id(entry: data.Event, event_ids: list[str]) -> tuple[str | None, EventError | None]:
    src = data.new_metadata(PLUGIN_NAME, entry.meta["lineno"])

    if "id" not in entry.meta:
        return None, EventError(src, "Missing 'id' field in meta", entry)

    event_id = entry.meta["id"]
    if event_id in event_ids:
        return event_id, EventError(src, "Duplicate event id", entry)

    return event_id, None


def is_event_transaction(entry: data.Transaction) -> bool:
    return any_tag_starts_with(entry.tags, "event-")


def validate_event_transaction(entry: data.Transaction, event_ids: list[str]) -> list[EventTransactionError]:
    src = data.new_metadata(PLUGIN_NAME, entry.meta["lineno"])
    event_tags = [tag for tag in entry.tags if tag.startswith("event-")]

    if len(event_tags) > 1:
        return [EventTransactionError(src, "Cannot have multiple event tags", entry)]

    event_id = event_tags[0].removeprefix("event-")
    if event_id not in event_ids:
        return [EventTransactionError(src, "Linked event not found", entry)]

    return []
