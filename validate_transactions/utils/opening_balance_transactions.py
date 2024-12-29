from beancount.core import account as core_account

from .errors import OpeningBalanceTransactionError

def is_opening_balance_transaction(entry):
    return "opening-balance" in entry.tags


def validate_opening_balance_transaction(entry):
    errors = []

    if not len(entry.tags) == 1:
        errors.append(
            OpeningBalanceTransactionError(
                entry.meta,
                f"Journal opening balance transaction must have exactly one tag",
                entry,
            )
        )
    if not len(entry.postings) == 2:
        errors.append(
            OpeningBalanceTransactionError(
                entry.meta,
                f"Journal opening balance transaction must have exactly two postings",
                entry,
            )
        )
    if not core_account.root(1, entry.postings[1].account) == "Equity":
        errors.append(
            OpeningBalanceTransactionError(
                entry.meta,
                f"Equity account must be the second posting",
                entry,
            )
        )
    if not core_account.has_component(entry.postings[1].account, "OpeningBalances"):
        errors.append(
            OpeningBalanceTransactionError(
                entry.meta,
                f"Second posting account must have a component of OpeningBalances",
                entry,
            )
        )

    return errors