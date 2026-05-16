from beancount.core import data

from .common import any_tag_starts_with
from .errors import TransferTransactionError

EXPECTED_POSTINGS = 2


def is_transfer_transaction(entry: data.Transaction) -> bool:
    return any_tag_starts_with(entry.tags, "transfer") or data.has_entry_account_component(entry, "Transfers")


def validate_transfer_transaction(entry: data.Transaction, party: str) -> list[TransferTransactionError]:
    transfer_types = {
        "transfer-to-self": {
            "payee": "Self",
            "narration_prefix": "Transfer to self: ",
            "account": f"Assets:{party}:Transfers:Self",
        },
        "transfer-to-francis": {
            "payee": "Francis",
            "narration_prefix": "Transfer to Francis: ",
            "account": f"Assets:Francis:Transfers:From{party}",
        },
        "transfer-to-leyna": {
            "payee": "Leyna",
            "narration_prefix": "Transfer to Leyna: ",
            "account": f"Assets:Leyna:Transfers:From{party}",
        },
        "transfer-to-shared": {
            "payee": "Shared",
            "narration_prefix": "Transfer to Shared: ",
            "account": f"Assets:Shared:Transfers:From{party}",
        },
        "transfer-from-self": {
            "payee": "Self",
            "narration_prefix": "Transfer from self: ",
            "account": f"Assets:{party}:Transfers:Self",
        },
        "transfer-from-francis": {
            "payee": "Francis",
            "narration_prefix": "Transfer from Francis: ",
            "account": f"Assets:{party}:Transfers:FromFrancis",
        },
        "transfer-from-leyna": {
            "payee": "Leyna",
            "narration_prefix": "Transfer from Leyna: ",
            "account": f"Assets:{party}:Transfers:FromLeyna",
        },
        "transfer-from-shared": {
            "payee": "Shared",
            "narration_prefix": "Transfer from Shared: ",
            "account": f"Assets:{party}:Transfers:FromShared",
        },
    }

    if len(entry.tags) != 1:
        return [
            TransferTransactionError(
                entry.meta,
                "Transfer transaction must have exactly one tag",
                entry,
            )
        ]

    type_key = next(iter(entry.tags))
    if type_key not in transfer_types:
        return [
            TransferTransactionError(
                entry.meta,
                f"Invalid transfer tag: {type_key}",
                entry,
            )
        ]

    transfer_type = transfer_types[type_key]
    errors: list[TransferTransactionError] = []

    if entry.payee != transfer_type["payee"]:
        errors.append(
            TransferTransactionError(
                entry.meta,
                f"Payee must be {transfer_type['payee']}",
                entry,
            )
        )

    if not entry.narration.startswith(transfer_type["narration_prefix"]):
        errors.append(
            TransferTransactionError(
                entry.meta,
                f"Narration must start with {transfer_type['narration_prefix']}",
                entry,
            )
        )

    if len(entry.postings) != EXPECTED_POSTINGS:
        errors.append(
            TransferTransactionError(
                entry.meta,
                "Transfer transaction must have exactly two postings",
                entry,
            )
        )
        return errors

    if entry.postings[1].account != transfer_type["account"]:
        errors.append(
            TransferTransactionError(
                entry.postings[1].meta,
                f"Second posting must be to: {transfer_type['account']}",
                entry.postings[1],
            )
        )

    if "from" in type_key and entry.postings[0].units.number < 0:
        errors.append(
            TransferTransactionError(
                entry.postings[0].meta,
                "First posting amount must be positive for transfer from",
                entry.postings[0],
            )
        )

    if "to" in type_key and entry.postings[0].units.number > 0:
        errors.append(
            TransferTransactionError(
                entry.postings[0].meta,
                "First posting amount must be negative for transfer to",
                entry.postings[0],
            )
        )

    return errors
