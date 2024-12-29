from beancount.core import data as core_data
from beancount.core import account as core_account

from .errors import InvalidTransferTransaction, PostingToAnotherPartyError, InvalidValuablesTransaction

def check_default_transaction(entry, party):
    errors = []
    # If entry has a posting with an account that has a component of "Transfers" it is not a valid default transaction (should be a transfer transaction)
    if core_data.has_entry_account_component(entry, "Transfers"):
        errors.append(
            InvalidTransferTransaction(
                entry.meta,
                f"Missing required tags for a transaction to a transfer account",
                entry,
            )
        )

    for posting in entry.postings[1:]:
        # If the posting account does not belong to the party, it is not a valid default transaction (should be a transfer or owed transaction)
        party_of_posting = core_account.split(posting.account)[1]

        if not party_of_posting == party:
            errors.append(
                PostingToAnotherPartyError(
                    posting.meta,
                    f"Posting to an account that does not belong to the party: {party}. If this was intentional, please use the appropriate tags",
                    posting,
                )
            )

        # If the posting has metadata of "receipt", it is not a valid default transaction (should be a valuables transaction)
        if "receipt" in posting.meta:
            errors.append(
                InvalidValuablesTransaction(
                    entry.meta,
                    f"Transactions with receipt metadata must have the 'valuables' tag",
                    entry,
                )
            )

    return errors
