from dateutil.relativedelta import relativedelta
import datetime

from .errors import BalanceAssertionError

def validate_balance_assertion(entry):
    errors = []

    if "statement" not in entry.meta:
        return[
            BalanceAssertionError(
                entry.meta,
                f"Missing required metadata of 'statement'",
                entry,
            )
        ]

    valid_statement_date = entry.date + relativedelta(months=+1) - datetime.timedelta(days=1)
    date_is_in_the_future = valid_statement_date > datetime.datetime.now().date()
    if not entry.meta["statement"].endswith(f"{valid_statement_date}.pdf") and not entry.meta["statement"].endswith("_closing-statement.pdf") and not date_is_in_the_future:
        errors.append(
            BalanceAssertionError(
                entry.meta,
                f"Statement file must be date one month from the balance assertion date ({valid_statement_date}.pdf), or a closing statement (_closing-statement.pdf)",
                entry,
            )
        )

    # Statement meta should be removed if date is in the future so that the document link is not created for a non-existent statement
    if date_is_in_the_future:
        del entry.meta["statement"]

    return errors