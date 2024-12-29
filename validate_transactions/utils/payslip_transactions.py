from .common import any_posting_has_metadata_key
from .errors import PayslipTransactionError

def is_payslip_transaction(entry):
    return "payslip" in entry.tags or any_posting_has_metadata_key(entry.postings, "payslip")

def validate_payslip_transaction(entry, party):
    errors = []

    if "payslip" not in entry.tags:
        errors.append(
            PayslipTransactionError(
                entry.meta,
                f"Missing required tag of 'payslip'",
                entry,
            )
        )

    if not "payslip" in entry.meta:
        errors.append(
            PayslipTransactionError(
                entry.meta,
                f"Missing required metadata of 'payslip'",
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