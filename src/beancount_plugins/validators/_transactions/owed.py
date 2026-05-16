"""Validate owed transactions (cross-party expenses)."""

from __future__ import annotations

from beancount.core import account as core_account
from beancount.core import data

from .common import any_tag_starts_with
from .errors import OwedTransactionError, PostingToAnotherPartyError

PLUGIN_NAME = "validate_transactions"

OWED_TYPES: dict[str, tuple[str, ...]] = {
    "owed-by-francis": ("Expenses:Francis", "Assets:Francis:Receivables"),
    "owed-by-leyna": ("Expenses:Leyna", "Assets:Leyna:Receivables"),
    "owed-by-shared": ("Expenses:Shared", "Assets:Shared:Receivables"),
    "owed-to-shared": ("Income:Shared:GiftsReceived",),
}


def any_posting_has_different_party(postings: list[data.Posting], party: str) -> bool:
    return any(core_account.split(posting.account)[1] != party for posting in postings)


def is_owed_transaction(entry: data.Transaction, party: str) -> bool:
    return any_tag_starts_with(entry.tags, "owed") or (
        any_posting_has_different_party(entry.postings, party)
        and not data.has_entry_account_component(entry, "Transfers")
    )


def validate_owed_transaction(
    entry: data.Transaction, party: str
) -> list[OwedTransactionError | PostingToAnotherPartyError]:
    src = data.new_metadata(PLUGIN_NAME, entry.meta["lineno"])
    errors: list[OwedTransactionError | PostingToAnotherPartyError] = []
    other_allowed_account_prefixes: list[str] = []

    for tag in entry.tags:
        if not tag.startswith("owed"):
            continue

        if tag not in OWED_TYPES:
            return [OwedTransactionError(src, f"Invalid owed tag: {tag}", entry)]

        # Cannot owe to self
        if tag == f"owed-by-{party.lower()}":
            return [OwedTransactionError(src, "Owed tag must be for another party", entry)]

        allowed_prefixes = OWED_TYPES[tag]
        has_expected_account = any(data.has_entry_account_component(entry, prefix) for prefix in allowed_prefixes)
        if not has_expected_account:
            errors.append(
                OwedTransactionError(
                    src,
                    f"Expected at least one posting to an account starting with: {list(allowed_prefixes)}",
                    entry,
                )
            )

        other_allowed_account_prefixes.extend(allowed_prefixes)

    for posting in entry.postings[1:]:
        party_of_posting = core_account.split(posting.account)[1]
        posting_account_is_allowed = any(
            posting.account.startswith(prefix) for prefix in other_allowed_account_prefixes
        )

        if party_of_posting != party and not posting_account_is_allowed:
            posting_lineno = posting.meta["lineno"] if posting.meta is not None else 0
            posting_src = data.new_metadata(PLUGIN_NAME, posting_lineno)
            errors.append(
                PostingToAnotherPartyError(
                    posting_src,
                    f"Posting to an account that does not belong to the party: {party}, "
                    f"or to any of the owed parties' allowed accounts: "
                    f"{other_allowed_account_prefixes}. "
                    "If this was intentional, please use the appropriate tags.",
                    posting,
                )
            )

    return errors
