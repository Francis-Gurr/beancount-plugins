from .common import any_posting_has_metadata_key
from .errors import PayslipTransactionError

def is_payslip_transaction(entry):
    return "payslip" in entry.tags or any_posting_has_metadata_key(entry.postings, "payslip")

def validate_payslip_transaction(entry):
    errors = []

    if "valuables" not in entry.tags:
        errors.append(
            PayslipTransactionError(
                entry.meta,
                f"Missing required tag of 'payslip'",
                entry,
            )
        )

    if not any_posting_has_metadata_key(entry.postings, "payslip"):
        errors.append(
            PayslipTransactionError(
                entry.meta,
                f"Missing required metadata of 'payslip'",
                entry,
            )
        )

    return errors