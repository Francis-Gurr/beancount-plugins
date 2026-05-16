"""Validate payslip transactions."""

from __future__ import annotations

from beancount.core import data

from .errors import PayslipTransactionError

PLUGIN_NAME = "validate_transactions"


def is_payslip_transaction(entry: data.Transaction) -> bool:
    return "payslip" in entry.tags or "payslip" in entry.meta


def validate_payslip_transaction(entry: data.Transaction, party: str) -> list[PayslipTransactionError]:
    src = data.new_metadata(PLUGIN_NAME, entry.meta["lineno"])
    errors: list[PayslipTransactionError] = []

    if "payslip" not in entry.tags:
        errors.append(
            PayslipTransactionError(
                src,
                "Missing required tag of 'payslip'",
                entry,
            )
        )

    if "payslip" not in entry.meta:
        errors.append(
            PayslipTransactionError(
                src,
                "Missing required metadata of 'payslip'",
                entry,
            )
        )

    if len(entry.postings) > 1 and entry.postings[1].account != f"Income:{party}:GrossPay:Salary":
        errors.append(
            PayslipTransactionError(
                src,
                f"Second posting account should be 'Income:{party}:GrossPay:Salary'",
                entry,
            )
        )

    return errors
