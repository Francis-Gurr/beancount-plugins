from beancount.core import account as core_account
from beancount.core import data

from .errors import OpeningBalanceTransactionError

EXPECTED_POSTINGS = 2


def is_opening_balance_transaction(entry: data.Transaction) -> bool:
    return "opening-balance" in entry.tags


def validate_opening_balance_transaction(entry: data.Transaction) -> list[OpeningBalanceTransactionError]:
    errors = []

    if len(entry.tags) != 1:
        errors.append(
            OpeningBalanceTransactionError(
                entry.meta,
                "Journal opening balance transaction must have exactly one tag",
                entry,
            )
        )
    if len(entry.postings) != EXPECTED_POSTINGS:
        errors.append(
            OpeningBalanceTransactionError(
                entry.meta,
                "Journal opening balance transaction must have exactly two postings",
                entry,
            )
        )
    if core_account.root(1, entry.postings[1].account) != "Equity":
        errors.append(
            OpeningBalanceTransactionError(
                entry.meta,
                "Equity account must be the second posting",
                entry,
            )
        )
    if not core_account.has_component(entry.postings[1].account, "OpeningBalances"):
        errors.append(
            OpeningBalanceTransactionError(
                entry.meta,
                "Second posting account must have a component of OpeningBalances",
                entry,
            )
        )

    return errors
