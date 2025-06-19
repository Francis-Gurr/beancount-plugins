from .common import any_tag_starts_with
from .errors import EventTransactionError


def is_event_transaction(entry):
    return any_tag_starts_with(entry.tags, "event")


def validate_event_transaction(entry, event_ids):
    errors = []

    tag = next(filter(lambda t: t.startswith("event"), entry.tags), None)
    id = tag.split("_")[1]

    if id not in event_ids:
        errors.append(
            EventTransactionError(
                entry.meta,
                "Event id not found",
                entry,
            )
        )

    return errors
