"""Create document directives from statement/payslip/receipt metadata on entries."""

from __future__ import annotations

from pathlib import Path

from beancount.core import data

from .common import any_posting_has_metadata_key
from .errors import DocumentFileNotFoundError

PLUGIN_NAME = "validate_transactions"


def get_full_filepath(
    entry: data.Balance | data.Transaction, filename: str
) -> tuple[str, DocumentFileNotFoundError | None]:
    full_filepath = (Path.cwd() / filename).resolve()
    if full_filepath.is_file():
        return str(full_filepath), None
    err = DocumentFileNotFoundError(
        data.new_metadata(PLUGIN_NAME, entry.meta["lineno"]),
        f"File not found: {full_filepath}",
        entry,
    )
    return str(full_filepath), err


def create_document_entries(
    entry: data.Balance | data.Transaction,
) -> tuple[list[data.Document], list[DocumentFileNotFoundError]]:
    errors: list[DocumentFileNotFoundError] = []
    document_entries: list[data.Document] = []

    if "statement" in entry.meta and isinstance(entry, data.Balance):
        full_filepath, err = get_full_filepath(entry, entry.meta["statement"])
        if err:
            errors.append(err)

        document_entries.append(
            data.Document(
                meta={"filename": entry.meta["filename"], "lineno": entry.meta["lineno"]},
                date=entry.date,
                account=entry.account,
                filename=full_filepath,
                tags={"statement"},
                links=set(),
            )
        )

    if "payslip" in entry.meta and isinstance(entry, data.Transaction) and len(entry.postings) > 1:
        full_filepath, err = get_full_filepath(entry, entry.meta["payslip"])
        if err:
            errors.append(err)

        document_entries.append(
            data.Document(
                meta={"filename": entry.meta["filename"], "lineno": entry.meta["lineno"]},
                date=entry.date,
                account=entry.postings[1].account,
                filename=full_filepath,
                tags={"payslip"},
                links=set(),
            )
        )

    if isinstance(entry, data.Transaction) and any_posting_has_metadata_key(entry.postings, "receipt"):
        for posting in entry.postings:
            if "receipt" not in posting.meta:
                continue
            full_filepath, err = get_full_filepath(entry, posting.meta["receipt"])
            if err:
                errors.append(err)

            document_entries.append(
                data.Document(
                    meta={"filename": posting.meta["receipt"], "lineno": posting.meta["lineno"]},
                    date=entry.date,
                    account=posting.account,
                    filename=full_filepath,
                    tags={"receipt"},
                    links=set(),
                )
            )

    return document_entries, errors
