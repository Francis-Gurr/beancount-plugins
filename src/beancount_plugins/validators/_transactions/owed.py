from beancount.core import account as core_account
from beancount.core import data

from .common import any_tag_starts_with
from .errors import OwedTransactionError, PostingToAnotherPartyError


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
        "owed-to-shared": {
            "extra_allowed_account_prefixes": ["Income:Shared:GiftsReceived"],
            "tags": ["owed", "owed-to-shared"],
        },
    }

    other_allowed_account_prefixes: list[str] = []
    errors: list[OwedTransactionError | PostingToAnotherPartyError] = []

    for tag in entry.tags:
        if tag.startswith("owed"):
            if tag not in owed_types:
                return [
                    OwedTransactionError(
                        entry.meta,
                        f"Invalid owed tag: {tag}",
                        entry,
                    )
                ]

            # Cannot owe to self
            if tag == f"owed-by-{party.lower()}":
                return [
                    OwedTransactionError(
                        entry.meta,
                        "Owed tag must be for another party",
                        entry,
                    )
                ]

            has_expected_account_with_prefix = False
            for allowed_account_prefix in owed_types[tag]["extra_allowed_account_prefixes"]:
                has_expected_account_with_prefix = has_expected_account_with_prefix or data.has_entry_account_component(
                    entry, allowed_account_prefix
                )

            # Must have a posting to Expenses:OwedPart or Assets:OwedPart:Receivables
            if not has_expected_account_with_prefix:
                errors.append(
                    OwedTransactionError(
                        entry.meta,
                        f"Expected at least one posting to an account starting with: "
                        f"{owed_types[tag]['extra_allowed_account_prefixes']}",
                        entry,
                    )
                )

            other_allowed_account_prefixes = (
                other_allowed_account_prefixes + owed_types[tag]["extra_allowed_account_prefixes"]
            )

    for posting in entry.postings[1:]:
        account_split = core_account.split(posting.account)
        party_of_posting = account_split[1]

        posting_party_is_not_entry_party = party_of_posting != party
        posting_account_is_not_expected = False
        for allowed_account_prefix in other_allowed_account_prefixes:
            posting_account_is_not_expected = posting_account_is_not_expected or posting.account.startswith(
                allowed_account_prefix
            )

        # Cannot post to any account that does not belong to the party or to Expenses:OwedParties
        # or Assets:OwedParties:Receivables
        if posting_party_is_not_entry_party and not posting_account_is_not_expected:
            errors.append(
                PostingToAnotherPartyError(
                    posting.meta,
                    f"Posting to an account that does not belong to the party: {party}, "
                    f"or to any of the owed parties' allowed accounts: "
                    f"{other_allowed_account_prefixes}. "
                    "If this was intentional, please use the appropriate tags.",
                    posting,
                )
            )

    return errors
