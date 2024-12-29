# from beancount.core import data as core_data

# def create_document_entry(entry):
#     return core_data.Document(
#         meta=entry.meta,
#         date=entry.date,
#         uri=document,
#     )


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