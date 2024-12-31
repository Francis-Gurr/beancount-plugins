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
    if not entry.meta["statement"].endswith(f"{valid_statement_date}.pdf"):
        errors.append(
            BalanceAssertionError(
                entry.meta,
                f"Statement file must be date one month from the balance assertion date ({valid_statement_date}.pdf)",
                entry,
            )
        )

    return errors