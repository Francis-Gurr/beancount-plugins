from .common import any_posting_has_metadata_key
from .errors import ReceiptTransactionError

def is_receipt_transaction(entry):
    return "receipt" in entry.tags or any_posting_has_metadata_key(entry.postings, "receipt")


def validate_receipt_transaction(entry):
    errors = []

    if "valuables" not in entry.tags:
        errors.append(
            ReceiptTransactionError(
                entry.meta,
                f"Missing required tag of 'receipt'",
                entry,
            )
        )

    if not any_posting_has_metadata_key(entry.postings, "receipt"):
        errors.append(
            ReceiptTransactionError(
                entry.meta,
                f"Missing required metadata of 'receipt'",
                entry,
            )
        )

    for posting in entry.postings[1:]:
        if "receipt" in posting.meta and not posting.account.startswith(f"Expenses"):
                errors.append(
                    ReceiptTransactionError(
                        entry.meta,
                        f"Transactions with receipt metadata must be to an expense account",
                        entry,
                    )
                )

    return errors