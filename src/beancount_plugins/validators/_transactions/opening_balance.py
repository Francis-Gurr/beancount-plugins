"""Validate journal-opening-balance transactions."""

from __future__ import annotations

from beancount.core import account as core_account
from beancount.core import data

from .errors import OpeningBalanceTransactionError

PLUGIN_NAME = "validate_transactions"
EXPECTED_POSTINGS = 2


def is_opening_balance_transaction(entry: data.Transaction) -> bool:
    return "journal-opening-balance" in entry.tags


def validate_opening_balance_transaction(
    entry: data.Transaction,
) -> list[OpeningBalanceTransactionError]:
    src = data.new_metadata(PLUGIN_NAME, entry.meta["lineno"])
    errors: list[OpeningBalanceTransactionError] = []

    if len(entry.tags) != 1:
        errors.append(
            OpeningBalanceTransactionError(
                src,
                "Journal opening balance transaction must have exactly one tag",
                entry,
            )
        )
    if len(entry.postings) != EXPECTED_POSTINGS:
        errors.append(
            OpeningBalanceTransactionError(
                src,
                "Journal opening balance transaction must have exactly two postings",
                entry,
            )
        )
        return errors

    if core_account.root(1, entry.postings[1].account) != "Equity":
        errors.append(
            OpeningBalanceTransactionError(
                src,
                "Equity account must be the second posting",
                entry,
            )
        )
    if not core_account.has_component(entry.postings[1].account, "OpeningBalances"):
        errors.append(
            OpeningBalanceTransactionError(
                src,
                "Second posting account must have a component of OpeningBalances",
                entry,
            )
        )

    return errors
