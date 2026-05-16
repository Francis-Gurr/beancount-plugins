"""Error tuples emitted by the transactions validator and its helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from beancount.core import data


class JournalError(NamedTuple):
    source: data.Meta | None
    message: str
    entry: data.Directive | None


class OpeningBalanceTransactionError(NamedTuple):
    source: data.Meta | None
    message: str
    entry: data.Directive | None


class MissingOpeningBalanceError(NamedTuple):
    source: data.Meta | None
    message: str
    entry: data.Directive | None


class FirstPostingIsNotToSpecifiedAccountError(NamedTuple):
    source: data.Meta | None
    message: str
    entry: data.Directive | None


class PostingToAnotherPartyError(NamedTuple):
    source: data.Meta | None
    message: str
    entry: data.Directive | data.Posting | None


class BalanceAssertionError(NamedTuple):
    source: data.Meta | None
    message: str
    entry: data.Directive | None


class TransferTransactionError(NamedTuple):
    source: data.Meta | None
    message: str
    entry: data.Directive | data.Posting | None


class ReceiptTransactionError(NamedTuple):
    source: data.Meta | None
    message: str
    entry: data.Directive | None


class PayslipTransactionError(NamedTuple):
    source: data.Meta | None
    message: str
    entry: data.Directive | None


class OwedTransactionError(NamedTuple):
    source: data.Meta | None
    message: str
    entry: data.Directive | None


class DocumentFileNotFoundError(NamedTuple):
    source: data.Meta | None
    message: str
    entry: data.Directive | None


class EventError(NamedTuple):
    source: data.Meta | None
    message: str
    entry: data.Directive | None


class EventTransactionError(NamedTuple):
    source: data.Meta | None
    message: str
    entry: data.Directive | None


type ValidationError = (
    JournalError
    | OpeningBalanceTransactionError
    | MissingOpeningBalanceError
    | FirstPostingIsNotToSpecifiedAccountError
    | PostingToAnotherPartyError
    | BalanceAssertionError
    | TransferTransactionError
    | ReceiptTransactionError
    | PayslipTransactionError
    | OwedTransactionError
    | DocumentFileNotFoundError
    | EventError
    | EventTransactionError
)
