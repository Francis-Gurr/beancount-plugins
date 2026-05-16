"""Validate transfer transactions between accounts."""

from __future__ import annotations

from dataclasses import dataclass

from beancount.core import data

from .common import any_tag_starts_with
from .errors import TransferTransactionError

PLUGIN_NAME = "validate_transactions"
EXPECTED_POSTINGS = 2


@dataclass(frozen=True, slots=True)
class TransferType:
    payee: str
    narration_prefix: str
    account_template: str

    def account_for(self, party: str) -> str:
        return self.account_template.format(party=party)


TRANSFER_TYPES: dict[str, TransferType] = {
    "transfer-to-self": TransferType(
        payee="Self",
        narration_prefix="Transfer to self: ",
        account_template="Assets:{party}:Transfers:Self",
    ),
    "transfer-to-francis": TransferType(
        payee="Francis",
        narration_prefix="Transfer to Francis: ",
        account_template="Assets:Francis:Transfers:From{party}",
    ),
    "transfer-to-leyna": TransferType(
        payee="Leyna",
        narration_prefix="Transfer to Leyna: ",
        account_template="Assets:Leyna:Transfers:From{party}",
    ),
    "transfer-to-shared": TransferType(
        payee="Shared",
        narration_prefix="Transfer to Shared: ",
        account_template="Assets:Shared:Transfers:From{party}",
    ),
    "transfer-from-self": TransferType(
        payee="Self",
        narration_prefix="Transfer from self: ",
        account_template="Assets:{party}:Transfers:Self",
    ),
    "transfer-from-francis": TransferType(
        payee="Francis",
        narration_prefix="Transfer from Francis: ",
        account_template="Assets:{party}:Transfers:FromFrancis",
    ),
    "transfer-from-leyna": TransferType(
        payee="Leyna",
        narration_prefix="Transfer from Leyna: ",
        account_template="Assets:{party}:Transfers:FromLeyna",
    ),
    "transfer-from-shared": TransferType(
        payee="Shared",
        narration_prefix="Transfer from Shared: ",
        account_template="Assets:{party}:Transfers:FromShared",
    ),
}


def is_transfer_transaction(entry: data.Transaction) -> bool:
    return any_tag_starts_with(entry.tags, "transfer") or data.has_entry_account_component(entry, "Transfers")


def validate_transfer_transaction(entry: data.Transaction, party: str) -> list[TransferTransactionError]:
    src = data.new_metadata(PLUGIN_NAME, entry.meta["lineno"])

    if len(entry.tags) != 1:
        return [TransferTransactionError(src, "Transfer transaction must have exactly one tag", entry)]

    type_key = next(iter(entry.tags))
    if type_key not in TRANSFER_TYPES:
        return [TransferTransactionError(src, f"Invalid transfer tag: {type_key}", entry)]

    transfer_type = TRANSFER_TYPES[type_key]
    expected_account = transfer_type.account_for(party)
    errors: list[TransferTransactionError] = []

    if entry.payee != transfer_type.payee:
        errors.append(TransferTransactionError(src, f"Payee must be {transfer_type.payee}", entry))

    narration = entry.narration or ""
    if not narration.startswith(transfer_type.narration_prefix):
        errors.append(
            TransferTransactionError(
                src,
                f"Narration must start with {transfer_type.narration_prefix}",
                entry,
            )
        )

    if len(entry.postings) != EXPECTED_POSTINGS:
        errors.append(TransferTransactionError(src, "Transfer transaction must have exactly two postings", entry))
        return errors

    posting_0, posting_1 = entry.postings[0], entry.postings[1]
    posting_0_lineno = posting_0.meta["lineno"] if posting_0.meta is not None else 0
    posting_1_lineno = posting_1.meta["lineno"] if posting_1.meta is not None else 0

    if posting_1.account != expected_account:
        errors.append(
            TransferTransactionError(
                data.new_metadata(PLUGIN_NAME, posting_1_lineno),
                f"Second posting must be to: {expected_account}",
                posting_1,
            )
        )

    posting_0_number = posting_0.units.number if posting_0.units is not None else None
    if posting_0_number is not None:
        if type_key.startswith("transfer-from") and posting_0_number < 0:
            errors.append(
                TransferTransactionError(
                    data.new_metadata(PLUGIN_NAME, posting_0_lineno),
                    "First posting amount must be positive for transfer from",
                    posting_0,
                )
            )
        if type_key.startswith("transfer-to") and posting_0_number > 0:
            errors.append(
                TransferTransactionError(
                    data.new_metadata(PLUGIN_NAME, posting_0_lineno),
                    "First posting amount must be negative for transfer to",
                    posting_0,
                )
            )

    return errors
