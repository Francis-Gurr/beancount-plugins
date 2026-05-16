from __future__ import annotations

from typing import TYPE_CHECKING

from .common import any_posting_has_metadata_key
from .errors import ReceiptTransactionError

if TYPE_CHECKING:
    from beancount.core import data


def is_receipt_transaction(entry: data.Transaction) -> bool:
    return "receipt" in entry.tags or any_posting_has_metadata_key(entry.postings, "receipt")


def validate_receipt_transaction(entry: data.Transaction) -> list[ReceiptTransactionError]:
    errors: list[ReceiptTransactionError] = []

    if "valuables" not in entry.tags:
        errors.append(
            ReceiptTransactionError(
                entry.meta,
                "Missing required tag of 'receipt'",
                entry,
            )
        )

    if not any_posting_has_metadata_key(entry.postings, "receipt"):
        errors.append(
            ReceiptTransactionError(
                entry.meta,
                "Missing required metadata of 'receipt'",
                entry,
            )
        )

    errors.extend(
        ReceiptTransactionError(
            entry.meta,
            "Transactions with receipt metadata must be to an expense account",
            entry,
        )
        for posting in entry.postings[1:]
        if "receipt" in posting.meta and not posting.account.startswith("Expenses")
    )

    return errors
