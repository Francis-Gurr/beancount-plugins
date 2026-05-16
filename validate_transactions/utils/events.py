from .errors import EventError, EventTransactionError
from .common import any_tag_starts_with

simple_event_types = ["address", "employment", "relationship"]
linked_event_types = ["trip", "work_trip"]


def validate_event(entry):
    errors = []

    event_types = simple_event_types + linked_event_types

    if entry.type not in event_types:
        errors.append(EventError(
            entry.meta,
            f"Event type '{entry.type}' is invalid",
            entry,
        ))

    return errors


def is_linked_event(entry):
    return entry.type in linked_event_types


def get_event_id(entry, event_ids):
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


def is_event_transaction(entry):
    return any_tag_starts_with(entry.tags, "event-")


def validate_event_transaction(entry, event_ids):
    event_tags = [tag for tag in entry.tags if tag.startswith("event-")]

    if len(event_tags) > 1:
        return [EventTransactionError(
            entry.meta,
            "Cannot have multiple event tags",
            entry,
        )]

    event_id = event_tags[0].removeprefix("event-")

    if event_id not in event_ids:
        return [EventTransactionError(
            entry.meta,
            "Linked event not found",
            entry,
        )]

    return []
