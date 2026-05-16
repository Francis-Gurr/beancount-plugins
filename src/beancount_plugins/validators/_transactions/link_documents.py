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
    entry_lineno = entry.meta["lineno"] if entry.meta is not None else 0
    err = DocumentFileNotFoundError(
        data.new_metadata(PLUGIN_NAME, entry_lineno),
        f"File not found: {full_filepath}",
        entry,
    )
    return str(full_filepath), err


def _document_meta(entry: data.Balance | data.Transaction) -> data.Meta:
    meta = entry.meta or {}
    return {"filename": meta.get("filename", "<unknown>"), "lineno": meta.get("lineno", 0)}


def create_document_entries(
    entry: data.Balance | data.Transaction,
) -> tuple[list[data.Document], list[DocumentFileNotFoundError]]:
    errors: list[DocumentFileNotFoundError] = []
    document_entries: list[data.Document] = []

    if entry.meta is not None and "statement" in entry.meta and isinstance(entry, data.Balance):
        full_filepath, err = get_full_filepath(entry, entry.meta["statement"])
        if err:
            errors.append(err)

        document_entries.append(
            data.Document(
                meta=_document_meta(entry),
                date=entry.date,
                account=entry.account,
                filename=full_filepath,
                tags=frozenset({"statement"}),
                links=frozenset(),
            )
        )

    if (
        entry.meta is not None
        and "payslip" in entry.meta
        and isinstance(entry, data.Transaction)
        and len(entry.postings) > 1
    ):
        full_filepath, err = get_full_filepath(entry, entry.meta["payslip"])
        if err:
            errors.append(err)

        document_entries.append(
            data.Document(
                meta=_document_meta(entry),
                date=entry.date,
                account=entry.postings[1].account,
                filename=full_filepath,
                tags=frozenset({"payslip"}),
                links=frozenset(),
            )
        )

    if isinstance(entry, data.Transaction) and any_posting_has_metadata_key(entry.postings, "receipt"):
        for posting in entry.postings:
            if posting.meta is None or "receipt" not in posting.meta:
                continue
            full_filepath, err = get_full_filepath(entry, posting.meta["receipt"])
            if err:
                errors.append(err)

            document_entries.append(
                data.Document(
                    meta={
                        "filename": posting.meta["receipt"],
                        "lineno": posting.meta.get("lineno", 0),
                    },
                    date=entry.date,
                    account=posting.account,
                    filename=full_filepath,
                    tags=frozenset({"receipt"}),
                    links=frozenset(),
                )
            )

    return document_entries, errors
