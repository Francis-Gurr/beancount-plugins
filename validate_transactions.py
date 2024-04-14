"""This plugin validates that there are no unused accounts.
"""

import collections

from beancount.core import data
from beancount.core import getters
from beancount.core import account

__plugins__ = ("validate_transactions",)

MissingJournalAccountName = collections.namedtuple(
    "MissingJournalAccountName", "source message entry"
)
FirstPostingIsNotToSpecifiedAccountError = collections.namedtuple(
    "FirstPostingIsNotToSpecifiedAccountError", "source message entry"
)
PostingToAnotherPartyError = collections.namedtuple(
    "PostingToAnotherPartyError", "source message entry"
)
InvalidTransferTransaction = collections.namedtuple(
    "InvalidTransferTransaction", "source message entry"
)
InvalidOwedTransaction = collections.namedtuple("InvalidOwedTransaction", "source message entry")


def is_transfer_transaction(entry):
    for tag in entry.tags:
        if tag.startswith("transfer"):
            return True
    return False


def check_transfer_transaction(entry, party):
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
            InvalidTransferTransaction(
                entry.meta,
                "Transfer transaction must have exactly one tag",
                entry,
            )
        ]

    type_key = list(entry.tags)[0]
    if type_key not in transfer_types:
        return [
            InvalidTransferTransaction(
                entry.meta,
                f"Invalid transfer tag: {type_key}",
                entry,
            )
        ]

    type = transfer_types[type_key]
    errors = []

    if entry.payee != type["payee"]:
        errors.append(
            InvalidTransferTransaction(
                entry.meta,
                f"Payee must be {type['payee']}",
                entry,
            )
        )

    if not entry.narration.startswith(type["narration_prefix"]):
        errors.append(
            InvalidTransferTransaction(
                entry.meta,
                f"Narration must start with {type['narration_prefix']}",
                entry,
            )
        )

    if len(entry.postings) != 2:
        errors.append(
            InvalidTransferTransaction(
                entry.meta,
                "Transfer transaction must have exactly two postings",
                entry,
            )
        )

    if entry.postings[1].account != type["account"]:
        errors.append(
            InvalidTransferTransaction(
                entry.postings[1].meta,
                f"Second posting must be to: {type['account']}",
                entry.postings[1],
            )
        )

    if "from" in type_key and entry.postings[0].units.number < 0:
        errors.append(
            InvalidTransferTransaction(
                entry.postings[0].meta,
                f"First posting amount must be positive for transfer from",
                entry.postings[0],
            )
        )

    if "to" in type_key and entry.postings[0].units.number > 0:
        errors.append(
            InvalidTransferTransaction(
                entry.postings[0].meta,
                f"First posting amount must be negative for transfer to",
                entry.postings[0],
            )
        )

    return errors


def is_owed_transaction(entry):
    for tag in entry.tags:
        if tag.startswith("owed"):
            return True
    return False


def check_owed_transaction(entry, party):
    owed_types = {
        "owed-by-francis": {
            "extra_allowed_account_prefix": "Expenses:Francis",
            "tags": ["owed", "owed-by-francis"],
        },
        "owed-by-leyna": {
            "extra_allowed_account_prefix": "Expenses:Leyna",
            "tags": ["owed", "owed-by-leyna"],
        },
        "owed-by-shared": {
            "extra_allowed_account_prefix": "Expenses:Shared",
            "tags": ["owed", "owed-by-shared"],
        },
    }

    other_allowed_account_prefixes = []
    errors = []

    for tag in entry.tags:
        if tag.startswith("owed"):
            if tag not in owed_types:
                return [
                    InvalidOwedTransaction(
                        entry.meta,
                        f"Invalid owed tag: {tag}",
                        entry,
                    )
                ]

            # Cannot owe to self
            if tag == f"owed-by-{party.lower()}":
                return [
                    InvalidOwedTransaction(
                        entry.meta,
                        f"Owed tag must be for another party",
                        entry,
                    )
                ]

            hasExpectedExpenseAccount = data.has_entry_account_component(
                entry, owed_types[tag]["extra_allowed_account_prefix"]
            )

            # Must have an expense account for the party that is owed
            if not hasExpectedExpenseAccount:
                errors.append(
                    InvalidOwedTransaction(
                        entry.meta,
                        f"Expected an expense account for the party that is owed: {owed_types[tag]['extra_allowed_account_prefix']}",
                        entry,
                    )
                )

            other_allowed_account_prefixes.append(owed_types[tag]["extra_allowed_account_prefix"])

    for posting in entry.postings[1:]:
        accountSplit = account.split(posting.account)
        party_of_posting = accountSplit[1]

        # Can only post to an account belonging to a different party if it is one of the allowed accounts
        if (
            not party_of_posting == party
            and account.root(2, posting.account) not in other_allowed_account_prefixes
        ):
            errors.append(
                PostingToAnotherPartyError(
                    posting.meta,
                    f"Posting to an account that does not belong to the party: {party}, or to any of the owed party's expense accounts: {other_allowed_account_prefixes}. If this was intentional, please use the appropriate tags.",
                    posting,
                )
            )

    return errors


def check_default_transaction(entry, party):
    errors = []
    # If entry has a posting with an account that has a component of "Transfers" it is not a valid default transaction
    if data.has_entry_account_component(entry, "Transfers"):
        errors.append(
            InvalidTransferTransaction(
                entry.meta,
                f"Missing required tags for a transaction to a transfer account",
                entry,
            )
        )

    for posting in entry.postings[1:]:
        party_of_posting = account.split(posting.account)[1]

        if not party_of_posting == party:
            errors.append(
                PostingToAnotherPartyError(
                    posting.meta,
                    f"Posting to an account that does not belong to the party: {party}. If this was intentional, please use the appropriate tags",
                    posting,
                )
            )

    return errors


def validate_transactions(entries, unused_options_map):
    errors = []

    currentFile = ""
    main_account = ""
    main_party = ""

    for entry in entries:
        if not currentFile == entry.meta["filename"]:
            currentFile = entry.meta["filename"]
            main_account = ""
            main_party = ""
        if isinstance(entry, data.Custom) and entry.type == "journal account name":
            main_account = entry.values[0].value
            main_party = account.split(main_account)[1]
        elif isinstance(entry, data.Transaction):
            if not main_account or not main_party:
                errors.append(
                    MissingJournalAccountName(
                        entry.meta,
                        "Journal account name must be specified before transactions using the custom directive",
                        entry,
                    )
                )
                continue
            if not entry.postings[0].account == main_account:
                errors.append(
                    FirstPostingIsNotToSpecifiedAccountError(
                        entry.meta,
                        f"The first posting should be to the account: {main_account}",
                        entry,
                    )
                )

            if is_transfer_transaction(entry):
                transfer_transaction_errors = check_transfer_transaction(entry, main_party)
                errors.extend(transfer_transaction_errors)
            elif is_owed_transaction(entry):
                owed_transaction_errors = check_owed_transaction(entry, main_party)
                errors.extend(owed_transaction_errors)
            else:
                default_transaction_errors = check_default_transaction(entry, main_party)
                errors.extend(default_transaction_errors)

    return entries, errors
