"""This plugin validates that there are no unused accounts.
"""

import collections

from beancount.core import data as core_data
from beancount.core import account as core_account

__plugins__ = ("validate_transactions",)

InvalidJournalOpeningBalance = collections.namedtuple(
    "InvalidJournalOpeningBalance", "source message entry"
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
            "extra_allowed_account_prefixes": ["Expenses:Francis", "Assets:Francis:Receivables"],
            "tags": ["owed", "owed-by-francis"],
        },
        "owed-by-leyna": {
            "extra_allowed_account_prefixes": ["Expenses:Leyna", "Assets:Leyna:Receivables"],
            "tags": ["owed", "owed-by-leyna"],
        },
        "owed-by-shared": {
            "extra_allowed_account_prefixes": ["Expenses:Shared", "Assets:Shared:Receivables"],
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

            hasExpectedAccountWithPrefix = False
            for allowed_account_prefix in owed_types[tag]["extra_allowed_account_prefixes"]:
                hasExpectedAccountWithPrefix = (
                    hasExpectedAccountWithPrefix
                    or core_data.has_entry_account_component(entry, allowed_account_prefix)
                )

            # Must have a posting to Expenses:OwedPart or Assets:OwedPart:Receivables
            if not hasExpectedAccountWithPrefix:
                errors.append(
                    InvalidOwedTransaction(
                        entry.meta,
                        f"Expected at least one posting to an account starting with: {owed_types[tag]['extra_allowed_account_prefixes']}",
                        entry,
                    )
                )

            other_allowed_account_prefixes = (
                other_allowed_account_prefixes + owed_types[tag]["extra_allowed_account_prefixes"]
            )

    for posting in entry.postings[1:]:
        accountSplit = core_account.split(posting.account)
        party_of_posting = accountSplit[1]

        postingPartyIsNotEntryParty = not party_of_posting == party
        postingAccountIsNotExpected = False
        for allowed_account_prefix in other_allowed_account_prefixes:
            postingAccountIsNotExpected = postingAccountIsNotExpected or posting.account.startswith(
                allowed_account_prefix
            )

        # Cannot post to any account that does not belong to the party or to Expenses:OwedParties or Assets:OwedParties:Receivables
        if postingPartyIsNotEntryParty and not postingAccountIsNotExpected:
            errors.append(
                PostingToAnotherPartyError(
                    posting.meta,
                    f"Posting to an account that does not belong to the party: {party}, or to any of the owed parties' allowed accounts: {other_allowed_account_prefixes}. If this was intentional, please use the appropriate tags.",
                    posting,
                )
            )

    return errors


def check_default_transaction(entry, party):
    errors = []
    # If entry has a posting with an account that has a component of "Transfers" it is not a valid default transaction
    if core_data.has_entry_account_component(entry, "Transfers"):
        errors.append(
            InvalidTransferTransaction(
                entry.meta,
                f"Missing required tags for a transaction to a transfer account",
                entry,
            )
        )

    # If entry has tag of #valuables, check that it has metadata of "receipt" and vice versa
    for posting in entry.postings[1:]:
        party_of_posting = core_account.split(posting.account)[1]

        if not party_of_posting == party:
            errors.append(
                PostingToAnotherPartyError(
                    posting.meta,
                    f"Posting to an account that does not belong to the party: {party}. If this was intentional, please use the appropriate tags",
                    posting,
                )
            )

    return errors


def is_journal_opening_balance(entry):
    return "journal-opening-balance" in entry.tags


def check_journal_opening_balance(entry):
    errors = []

    if not len(entry.tags) == 1:
        errors.append(
            InvalidJournalOpeningBalance(
                entry.meta,
                f"Journal opening balance transaction must have exactly one tag",
                entry,
            )
        )
    if not len(entry.postings) == 2:
        errors.append(
            InvalidJournalOpeningBalance(
                entry.meta,
                f"Journal opening balance transaction must have exactly two postings",
                entry,
            )
        )
    if not core_account.root(1, entry.postings[1].account) == "Equity":
        errors.append(
            InvalidJournalOpeningBalance(
                entry.meta,
                f"Equity account must be the second posting",
                entry,
            )
        )
    if not core_account.has_component(entry.postings[1].account, "OpeningBalances"):
        errors.append(
            InvalidJournalOpeningBalance(
                entry.meta,
                f"Second posting account must have a component of OpeningBalances",
                entry,
            )
        )

    filename = entry.meta["filename"]
    account = entry.postings[0].account
    party = core_account.split(account)[1]

    return filename, account, party, errors


def check_first_posting_account(entry, account):
    errors = []

    if not entry.postings[0].account == account:
        errors.append(
            FirstPostingIsNotToSpecifiedAccountError(
                entry.meta,
                f"The first posting should be to the account: {account}",
                entry,
            )
        )

    return errors


def should_skip(entry):
    return "skip-validation" in entry.tags


def validate_transactions(entries, unused_options_map):
    errors = []
    fileAccountMap = {}

    for entry in entries:
        if isinstance(entry, core_data.Transaction):
            if should_skip(entry):
                continue

            if is_journal_opening_balance(entry):
                filename, account, party, err = check_journal_opening_balance(entry)
                fileAccountMap[filename] = {
                    "account": account,
                    "party": party,
                }
                errors.extend(err)
                continue

            transaction_filename = entry.meta["filename"]
            if transaction_filename not in fileAccountMap:
                errors.append(
                    InvalidJournalOpeningBalance(
                        entry.meta,
                        "Journal opening balance transaction must be specified before transactions",
                        entry,
                    )
                )
                continue
            transaction_account = fileAccountMap[transaction_filename]["account"]
            transaction_party = fileAccountMap[transaction_filename]["party"]

            first_posting_errors = check_first_posting_account(entry, transaction_account)
            errors.extend(first_posting_errors)

            if is_transfer_transaction(entry):
                transfer_transaction_errors = check_transfer_transaction(entry, transaction_party)
                errors.extend(transfer_transaction_errors)
            elif is_owed_transaction(entry):
                owed_transaction_errors = check_owed_transaction(entry, transaction_party)
                errors.extend(owed_transaction_errors)
            else:
                default_transaction_errors = check_default_transaction(entry, transaction_party)
                errors.extend(default_transaction_errors)

    return entries, errors
