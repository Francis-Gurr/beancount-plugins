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

    # Check that the statement date is the day before the balance assertion date
    valid_statement_date = entry.date - datetime.timedelta(days=1)
    if not entry.meta["statement"].endswith(f"{valid_statement_date}.pdf"):
        errors.append(
            BalanceAssertionError(
                entry.meta,
                f"Statement date must be the day before the balance assertion date ({valid_statement_date})",
                entry,
            )
        )

    return errors