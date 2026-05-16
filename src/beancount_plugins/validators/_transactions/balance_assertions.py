"""Validate beancount Balance directives have a matching statement document."""

from __future__ import annotations

import datetime

from beancount.core import data
from dateutil.relativedelta import relativedelta

from .errors import BalanceAssertionError

PLUGIN_NAME = "validate_transactions"


def validate_balance_assertion(entry: data.Balance) -> list[BalanceAssertionError]:
    src = data.new_metadata(PLUGIN_NAME, entry.meta["lineno"])
    errors: list[BalanceAssertionError] = []

    if "statement" not in entry.meta:
        return [
            BalanceAssertionError(
                src,
                "Missing required metadata of 'statement'",
                entry,
            )
        ]

    valid_statement_date = entry.date + relativedelta(months=+1) - datetime.timedelta(days=1)
    date_is_in_the_future = valid_statement_date > datetime.datetime.now(tz=datetime.UTC).date()
    if (
        not entry.meta["statement"].endswith(f"{valid_statement_date}.pdf")
        and not entry.meta["statement"].endswith("_closing-statement.pdf")
        and not date_is_in_the_future
    ):
        errors.append(
            BalanceAssertionError(
                src,
                f"Statement file must be date one month from the balance assertion date "
                f"({valid_statement_date}.pdf), or a closing statement (_closing-statement.pdf)",
                entry,
            )
        )

    # Strip the statement meta on future-dated balances so the document link
    # doesn't reference a file that doesn't exist yet.
    if date_is_in_the_future:
        del entry.meta["statement"]

    return errors
