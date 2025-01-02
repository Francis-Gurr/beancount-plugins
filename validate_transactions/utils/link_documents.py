import uuid
import os

from beancount.core import data as core_data

from .common import any_posting_has_metadata_key
from .errors import FileNotFoundError

def get_full_filepath(entry, filename):
    err = None

    cwd = os.path.abspath(os.getcwd())
    filepath = os.path.normpath(filename)
    full_filepath = os.path.join(cwd, filepath)

    if not os.path.isfile(full_filepath):
        err = FileNotFoundError(
            entry.meta,
            f"File not found: {full_filepath}",
            entry,
        )

    return full_filepath, err


def create_document_entries(entry):
    errors = []
    document_entries = []

    if "statement" in entry.meta:
        full_filepath, err = get_full_filepath(entry, entry.meta["statement"])
        if err:
            errors.append(err)

        document_entries.append(
            core_data.Document(
                meta={
                    "filename": entry.meta["filename"],
                    "lineno": entry.meta["lineno"],
                },
                date=entry.date,
                account=entry.account,
                filename=full_filepath,
                tags={"statement"},
                links=set(),
            )
        )
    if "payslip" in entry.meta:
        # link = str(uuid.uuid4())
        # entry.links.append(link)

        full_filepath, err = get_full_filepath(entry, entry.meta["payslip"])
        if err:
            errors.append(err)

        document_entries.append(
            core_data.Document(
                meta={
                    "filename": entry.meta["filename"],
                    "lineno": entry.meta["lineno"],
                },
                date=entry.date,
                account=entry.postings[1].account,
                filename=full_filepath,
                tags={"payslip"},
                links=set(),
            )
        )
    if isinstance(entry, core_data.Transaction) and any_posting_has_metadata_key(entry.postings, "receipt"):
        for posting in entry.postings:
            if "receipt" in posting.meta:
                # link = str(uuid.uuid4())
                # entry.links.append(link)

                full_filepath, err = get_full_filepath(entry, posting.meta["receipt"])
                if err:
                    errors.append(err)

                document_entries.append(
                    core_data.Document(
                        meta={
                            "filename": posting.meta["receipt"],
                            "lineno": posting.meta["lineno"],
                        },
                        date=entry.date,
                        account=posting.account,
                        filename=full_filepath,
                        tags={"receipt"},
                        links=set(),
                    )
                )

    return document_entries, errors


