"""Validate that valuables transactions have receipt metadata."""

from __future__ import annotations

from beancount.core import data

from .common import any_posting_has_metadata_key
from .errors import ReceiptTransactionError

PLUGIN_NAME = "validate_transactions"


def is_receipt_transaction(entry: data.Transaction) -> bool:
    return "valuables" in entry.tags or any_posting_has_metadata_key(entry.postings, "receipt")


def validate_receipt_transaction(entry: data.Transaction) -> list[ReceiptTransactionError]:
    src = data.new_metadata(PLUGIN_NAME, entry.meta["lineno"])
    errors: list[ReceiptTransactionError] = []

    if "valuables" not in entry.tags:
        errors.append(
            ReceiptTransactionError(
                src,
                "Missing required tag of 'valuables'",
                entry,
            )
        )

    if not any_posting_has_metadata_key(entry.postings, "receipt"):
        errors.append(
            ReceiptTransactionError(
                src,
                "Missing required metadata of 'receipt'",
                entry,
            )
        )

    errors.extend(
        ReceiptTransactionError(
            src,
            "Transactions with receipt metadata must be to an expense account",
            entry,
        )
        for posting in entry.postings[1:]
        if "receipt" in posting.meta and not posting.account.startswith("Expenses")
    )

    return errors
