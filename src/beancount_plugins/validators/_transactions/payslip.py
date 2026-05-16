from __future__ import annotations

from typing import TYPE_CHECKING

from .errors import PayslipTransactionError

if TYPE_CHECKING:
    from beancount.core import data


def is_payslip_transaction(entry: data.Transaction) -> bool:
    return "payslip" in entry.tags or "payslip" in entry.meta


def validate_payslip_transaction(entry: data.Transaction, party: str) -> list[PayslipTransactionError]:
    errors: list[PayslipTransactionError] = []

    if "payslip" not in entry.tags:
        errors.append(
            PayslipTransactionError(
                entry.meta,
                "Missing required tag of 'payslip'",
                entry,
            )
        )

    if "payslip" not in entry.meta:
        errors.append(
            PayslipTransactionError(
                entry.meta,
                "Missing required metadata of 'payslip'",
                entry,
            )
        )

    if entry.postings[1].account != f"Income:{party}:GrossPay:Salary":
        errors.append(
            PayslipTransactionError(
                entry.meta,
                f"Second posting account should be 'Income:{party}:GrossPay:Salary'",
                entry,
            )
        )

    return errors
