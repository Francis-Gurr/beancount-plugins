from beancount.core import data as core_data
from beancount.core import account as core_account

from .utils.errors import FirstPostingIsNotToSpecifiedAccountError, OpeningBalanceTransactionError
from .utils.balance_assertions import validate_balance_assertion
from .utils.opening_balance_transactions import is_opening_balance_transaction, validate_opening_balance_transaction
from .utils.transfer_transactions import is_transfer_transaction, validate_transfer_transaction
from .utils.owed_transactions import is_owed_transaction, validate_owed_transaction
from .utils.receipt_transactions import is_receipt_transaction, validate_receipt_transaction
from .utils.payslip_transactions import is_payslip_transaction, validate_payslip_transaction

__plugins__ = ("validate_transactions",)

def get_transaction_filename(entry, fileAccountMap):
    err = None

    transaction_filename = entry.meta["filename"]
    if transaction_filename not in fileAccountMap:
        err = OpeningBalanceTransactionError(
                entry.meta,
                "Opening balance transaction must be specified before all following transactions",
                entry,
            )

    return transaction_filename, err

def validate_first_posting_account(entry, account):
    if not entry.postings[0].account == account:
        return FirstPostingIsNotToSpecifiedAccountError(
                entry.meta,
                f"The first posting should be to the account: {account}",
                entry,
            )

def should_skip(entry):
    return "skip-validation" in entry.tags


def validate_transactions(entries, unused_options_map):
    errors = []
    fileAccountMap = {}

    entries_with_documents = []
    events = []
    trip_transactions = []

    for entry in entries:
        if isinstance(entry, core_data.Balance):
            errors.extend(validate_balance_assertion(entry))
            entry.meta["document"] = entry.meta.get("statement", "")
            entries_with_documents.append(entry)
        elif isinstance(entry, core_data.Transaction) and is_opening_balance_transaction(entry):
            errors.extend(validate_opening_balance_transaction(entry))

            filename = entry.meta["filename"]
            account = entry.postings[0].account
            party = core_account.split(account)[1]

            fileAccountMap[filename] = {
                "account": account,
                "party": party,
            }
        elif isinstance(entry, core_data.Transaction) and not should_skip(entry):
            transaction_filename, err = get_transaction_filename(entry, fileAccountMap)
            if err:
                errors.append(err)
                continue
            account = fileAccountMap[transaction_filename]["account"]
            party = fileAccountMap[transaction_filename]["party"]

            err = validate_first_posting_account(entry, account)
            errors.append(err)

            if is_transfer_transaction(entry):
                errors.extend(validate_transfer_transaction(entry, party))

            print("***")
            print(entry, account, party)
            print("")
            if is_owed_transaction(entry, party):
                errors.extend(validate_owed_transaction(entry, party))

            if is_receipt_transaction(entry):
                errors.extend(validate_receipt_transaction(entry))
                entry.meta["document"] = entry.meta.get("receipt", "")
                entries_with_documents.append(entry)

            if is_payslip_transaction(entry):
                errors.extend(validate_payslip_transaction(entry))
                entry.meta["document"] = entry.meta.get("payslip", "")
                entries_with_documents.append(entry)

    # for entry in entries_with_documents:
    #     if "document" in entry.meta:
    #         events.append(
    #             core_data.Document(
    #                 meta=entry.meta,
    #                 date=entry.date,
    #                 uri=entry.meta["document"],
    #             )
    #         )

    return entries, errors
