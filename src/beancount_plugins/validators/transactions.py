from beancount.core import data

from ._transactions.balance_assertions import validate_balance_assertion
from ._transactions.errors import (
    FirstPostingIsNotToSpecifiedAccountError,
    JournalError,
    MissingOpeningBalanceError,
)
from ._transactions.events import (
    get_event_id,
    is_event_transaction,
    is_linked_event,
    validate_event,
    validate_event_transaction,
)
from ._transactions.link_documents import create_document_entries
from ._transactions.opening_balance import is_opening_balance_transaction, validate_opening_balance_transaction
from ._transactions.owed import is_owed_transaction, validate_owed_transaction
from ._transactions.payslip import is_payslip_transaction, validate_payslip_transaction
from ._transactions.receipt import is_receipt_transaction, validate_receipt_transaction
from ._transactions.transfer import is_transfer_transaction, validate_transfer_transaction

__plugins__ = ("validate_transactions",)


def get_transaction_filename(
    entry: data.Transaction, file_account_map: dict[str, dict[str, str]]
) -> tuple[str, JournalError | None]:
    err = None

    transaction_filename = entry.meta["filename"]
    if transaction_filename not in file_account_map:
        err = JournalError(
            entry.meta,
            "Journal party and account must be specified before all following transactions using custom directive",
            entry,
        )

    return transaction_filename, err


def validate_first_posting_account(
    entry: data.Transaction, account: str
) -> FirstPostingIsNotToSpecifiedAccountError | None:
    err = None
    if entry.postings[0].account != account:
        err = FirstPostingIsNotToSpecifiedAccountError(
            entry.meta,
            f"The first posting should be to the account: {account}",
            entry,
        )
    return err


def should_skip(entry: data.Directive) -> bool:
    transaction_filename = entry.meta["filename"]
    is_excluded_transaction = isinstance(entry, data.Transaction) and "exclude-entry-from-validation" in entry.tags
    return transaction_filename.endswith("transfers.beancount") or is_excluded_transaction


def _validate_transaction(
    entry: data.Transaction, party: str, account: str, event_ids: list[str]
) -> tuple[list[object], bool]:
    """Run all per-transaction validators. Return (errors, needs_document_entries)."""
    errors: list[object] = []
    needs_documents = False

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
        needs_documents = True

    if is_payslip_transaction(entry):
        errors.extend(validate_payslip_transaction(entry, party))
        needs_documents = True

    if is_event_transaction(entry):
        errors.extend(validate_event_transaction(entry, event_ids))

    return errors, needs_documents


def _check_missing_opening_balance(
    entry: data.Transaction,
    transaction_filename: str,
    files_seen: set[str],
) -> list[MissingOpeningBalanceError]:
    is_first = transaction_filename not in files_seen
    files_seen.add(transaction_filename)
    if is_first and not is_opening_balance_transaction(entry):
        return [
            MissingOpeningBalanceError(
                entry.meta,
                "Journal opening balance transaction must be specified before transactions",
                entry,
            )
        ]
    return []


def _process_event(entry: data.Event, event_ids: list[str]) -> list[object]:
    errors: list[object] = list(validate_event(entry))
    if is_linked_event(entry):
        event_id, err = get_event_id(entry, event_ids)
        if err:
            errors.append(err)
        elif event_id is not None:
            event_ids.append(event_id)
    return errors


def validate_transactions(
    entries: data.Entries, _unused_options_map: data.Options
) -> tuple[data.Entries, list[object]]:
    errors: list[object] = []
    entries_with_documents: list[data.Balance | data.Transaction] = []
    event_ids: list[str] = []
    file_account_map: dict[str, dict[str, str]] = {}
    files_with_first_transaction_seen: set[str] = set()

    for entry in entries:
        if should_skip(entry):
            continue

        if isinstance(entry, data.Balance):
            errors.extend(validate_balance_assertion(entry))
            entries_with_documents.append(entry)

        elif isinstance(entry, data.Custom) and entry.type == "initialise_journal_file":
            filename = entry.meta["filename"]
            file_account_map[filename] = {
                "party": entry.values[0].value,
                "account": entry.values[1].value,
            }

        elif isinstance(entry, data.Event):
            errors.extend(_process_event(entry, event_ids))

        elif isinstance(entry, data.Transaction):
            transaction_filename, err = get_transaction_filename(entry, file_account_map)
            if err:
                errors.append(err)
                continue

            errors.extend(
                _check_missing_opening_balance(entry, transaction_filename, files_with_first_transaction_seen)
            )

            party = file_account_map[transaction_filename]["party"]
            account = file_account_map[transaction_filename]["account"]

            txn_errors, needs_documents = _validate_transaction(entry, party, account, event_ids)
            errors.extend(txn_errors)
            if needs_documents:
                entries_with_documents.append(entry)

    for entry in entries_with_documents:
        document_entries, document_errors = create_document_entries(entry)
        errors.extend(document_errors)
        entries.extend(document_entries)

    return entries, errors
