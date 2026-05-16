"""Shared predicates used across the transactions validator helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from beancount.core import data


def any_posting_has_metadata_key(postings: list[data.Posting], metadata_key: str) -> bool:
    return any(metadata_key in posting.meta for posting in postings)


def any_tag_starts_with(tags: frozenset[str] | set[str], prefix: str) -> bool:
    return any(tag.startswith(prefix) for tag in tags)
