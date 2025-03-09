from beancount.core import data as core_data

from .common import any_tag_starts_with
from .errors import TransferTransactionError

def is_transfer_transaction(entry):
    return any_tag_starts_with(entry.tags, "transfer") or core_data.has_entry_account_component(entry, "Transfers")

def validate_transfer_transaction(entry, party):
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

    type_key = list(entry.tags)[0]
    if type_key not in transfer_types:
        return [
            TransferTransactionError(
                entry.meta,
                f"Invalid transfer tag: {type_key}",
                entry,
            )
        ]

    type = transfer_types[type_key]
    errors = []

    if entry.payee != type["payee"]:
        errors.append(
            TransferTransactionError(
                entry.meta,
                f"Payee must be {type['payee']}",
                entry,
            )
        )

    if not entry.narration.startswith(type["narration_prefix"]):
        errors.append(
            TransferTransactionError(
                entry.meta,
                f"Narration must start with {type['narration_prefix']}",
                entry,
            )
        )

    if len(entry.postings) != 2:
        errors.append(
            TransferTransactionError(
                entry.meta,
                "Transfer transaction must have exactly two postings",
                entry,
            )
        )

    if entry.postings[1].account != type["account"]:
        errors.append(
            TransferTransactionError(
                entry.postings[1].meta,
                f"Second posting must be to: {type['account']}",
                entry.postings[1],
            )
        )

    if "from" in type_key and entry.postings[0].units.number < 0:
        errors.append(
            TransferTransactionError(
                entry.postings[0].meta,
                f"First posting amount must be positive for transfer from",
                entry.postings[0],
            )
        )

    if "to" in type_key and entry.postings[0].units.number > 0:
        errors.append(
            TransferTransactionError(
                entry.postings[0].meta,
                f"First posting amount must be negative for transfer to",
                entry.postings[0],
            )
        )

    return errors