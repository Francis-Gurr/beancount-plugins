import uuid
import os

from beancount.core import data as core_data

from .errors import FileNotFoundError

    # # Check that the statement is a valid file
    # cwd = os.path.abspath(os.getcwd())
    # statement_path = os.path.normpath(entry.meta["statement"])
    # full_file_path = os.path.join(cwd, statement_path)
    # print("\nfull-file-path: ", full_file_path)
    # if os.path.isfile(full_file_path):
    #     print("file exists")
    #     relative_file_path = os.path.relpath(full_file_path, start=os.path.dirname(entry.meta["filename"]))
    #     print("relative-file-path: ", relative_file_path)
    #     # entry.meta["document"] = relative_file_path.replace("\\", "/") # Add a document field to the posting meta for fava to display the statement
    #     if entry.meta["statement"] == "francis/2024/documents/bank-statements/starling/2024-08-31.pdf":
    #         print("setting document")
    #         entry.meta["document"] = "francis/2024/documents/bank-statements/starling/2024-08-31.pdf"
    # else:
    #     print(entry)
    #     errors.append(
    #         BalanceAssertionError(
    #             entry.meta,
    #             f"Invalid statement file path",
    #             entry,
    #         )
    #     )

def get_full_filepath(entry, filename):
    err = None

    cwd = os.path.abspath(os.getcwd())
    filepath = os.path.normpath(filename)
    full_filepath = os.path.join(cwd, filepath)

    # print("\ncwd: ", cwd)
    # print("\nfilename: ", filename)
    # print("\nfilepath: ", filepath)
    # print("\nfull-file-path: ", full_filepath)
    if not os.path.isfile(full_filepath):
        # print("file does not exist")
        err = FileNotFoundError(
            entry.meta,
            f"File not found: {full_filepath}",
            entry,
        )

    return full_filepath, err


def create_document_entries(entry):
    # print("\n\n *********************************")
    # print("\n entry: ", entry)

    errors = []
    document_entries = []

    if "statement" in entry.meta:
        full_filepath, err = get_full_filepath(entry, entry.meta["statement"])
        if err:
            # print("\n error: ", err)
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
        # print("\ndocument entry: ", document_entries[-1])
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
    if "receipt" in entry.meta:
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


