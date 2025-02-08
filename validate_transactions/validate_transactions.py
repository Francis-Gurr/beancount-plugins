from beancount.core import data as core_data
from beancount.core import account as core_account

from .utils.balance_assertions import validate_balance_assertion
from .utils.errors import FirstPostingIsNotToSpecifiedAccountError, JournalError
from .utils.link_documents import create_document_entries
from .utils.opening_balance_transactions import is_opening_balance_transaction, validate_opening_balance_transaction
from .utils.owed_transactions import is_owed_transaction, validate_owed_transaction
from .utils.payslip_transactions import is_payslip_transaction, validate_payslip_transaction
from .utils.receipt_transactions import is_receipt_transaction, validate_receipt_transaction
from .utils.transfer_transactions import is_transfer_transaction, validate_transfer_transaction

__plugins__ = ("validate_transactions",)

fileAccountMap = {}

def get_transaction_filename(entry):
    err = None

    transaction_filename = entry.meta["filename"]
    if transaction_filename not in fileAccountMap:
        err = JournalError(
                entry.meta,
                "Journal party and account must be specified before all following transactions using custom directive",
                entry,
            )

    return transaction_filename, err

def validate_first_posting_account(entry, account):
    err = None
    if not entry.postings[0].account == account:
        err = FirstPostingIsNotToSpecifiedAccountError(
                entry.meta,
                f"The first posting should be to the account: {account}",
                entry,
            )
    return err

def should_skip(entry):
    transaction_filename = entry.meta["filename"]
    is_excluded_transaction = isinstance(entry, core_data.Transaction) and "exclude-entry-from-validation" in entry.tags
    return transaction_filename.endswith("transfers.beancount") or is_excluded_transaction


def validate_transactions(entries, unused_options_map):
    errors = []

    entries_with_documents = []
    events = []
    trip_transactions = []

    for entry in entries:
        if should_skip(entry):
            continue

        if isinstance(entry, core_data.Balance):
            errors.extend(validate_balance_assertion(entry))
            entries_with_documents.append(entry)

        elif isinstance(entry, core_data.Custom) and entry.type == "initialise_journal_file":
            filename = entry.meta["filename"]
            fileAccountMap[filename] = {
                "party": entry.values[0].value,
                "account": entry.values[1].value,
            }

        elif isinstance(entry, core_data.Transaction):
            transaction_filename, err = get_transaction_filename(entry)
            if err:
                errors.append(err)
                continue

            party = fileAccountMap[transaction_filename]["party"]
            account = fileAccountMap[transaction_filename]["account"]

            err = validate_first_posting_account(entry, account)
            if err:
                errors.append(err)

            if is_opening_balance_transaction(entry):
                errors.extend(validate_opening_balance_transaction(entry))

            if is_transfer_transaction(entry):
                errors.extend(validate_transfer_transaction(entry, party))

            if is_owed_transaction(entry, party):
                errors.extend(validate_owed_transaction(entry, party))

            if is_receipt_transaction(entry):
                errors.extend(validate_receipt_transaction(entry))
                entries_with_documents.append(entry)

            if is_payslip_transaction(entry):
                errors.extend(validate_payslip_transaction(entry, party))
                entries_with_documents.append(entry)

    for entry in entries_with_documents:
        document_entries, document_errors = create_document_entries(entry)
        errors.extend(document_errors)
        entries.extend(document_entries)

    return entries, errors
