import collections

OpeningBalanceTransactionError = collections.namedtuple(
    "OpeningBalanceTransactionError", "source message entry"
)
FirstPostingIsNotToSpecifiedAccountError = collections.namedtuple(
    "FirstPostingIsNotToSpecifiedAccountError", "source message entry"
)
PostingToAnotherPartyError = collections.namedtuple(
    "PostingToAnotherPartyError", "source message entry"
)
BalanceAssertionError = collections.namedtuple(
    "BalanceAssertionError", "source message entry"
)
TransferTransactionError = collections.namedtuple(
    "TransferTransactionError", "source message entry"
)
ReceiptTransactionError = collections.namedtuple(
    "ReceiptTransactionError", "source message entry"
)
PayslipTransactionError = collections.namedtuple(
    "PayslipTransactionError", "source message entry"
)
OwedTransactionError = collections.namedtuple("OwedTransactionError", "source message entry")
FileNotFoundError = collections.namedtuple("FileNotFoundError", "source message entry")