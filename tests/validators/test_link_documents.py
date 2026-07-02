from beancount_plugins.validators.transactions import validate_transactions


def test_statement_creates_document_entry(load_doc, tmp_path):
    statement = tmp_path / "2000-04-30.pdf"
    statement.touch()
    entries, options_map = load_doc(f"""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"
        2000-01-01 open Assets:Francis:Bank
        2000-01-01 open Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-04-01 balance Assets:Francis:Bank 1 GBP
          statement: "{statement}"
    """)
    extended_entries, errors = validate_transactions(entries, options_map)
    docs = [e for e in extended_entries if e.__class__.__name__ == "Document"]
    assert len(docs) == 1
    assert "statement" in docs[0].tags
    assert docs[0].account == "Assets:Francis:Bank"
    assert len(errors) == 0


def test_payslip_creates_document_entry(load_doc, tmp_path):
    payslip = tmp_path / "jan.pdf"
    payslip.touch()
    entries, options_map = load_doc(f"""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"
        2000-01-01 open Assets:Francis:Bank
        2000-01-01 open Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-15 open Income:Francis:GrossPay:Salary
        2000-01-15 * "Employer" "January salary" #payslip
          payslip: "{payslip}"
          Assets:Francis:Bank             1000 GBP
          Income:Francis:GrossPay:Salary -1000 GBP
    """)
    extended_entries, errors = validate_transactions(entries, options_map)
    docs = [e for e in extended_entries if e.__class__.__name__ == "Document"]
    assert len(docs) == 1
    assert "payslip" in docs[0].tags
    assert docs[0].account == "Income:Francis:GrossPay:Salary"
    payslip_errors = [e for e in errors if e.__class__.__name__ == "PayslipTransactionError"]
    assert len(payslip_errors) == 0


def test_receipt_creates_document_entry(load_doc, tmp_path):
    receipt = tmp_path / "camera.pdf"
    receipt.touch()
    entries, options_map = load_doc(f"""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"
        2000-01-01 open Assets:Francis:Bank
        2000-01-01 open Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-02 open Expenses:Francis:Electronics
        2000-01-02 * "Camera shop" "New camera" #valuables
          Assets:Francis:Bank        -100 GBP
          Expenses:Francis:Electronics   100 GBP
            receipt: "{receipt}"
    """)
    extended_entries, errors = validate_transactions(entries, options_map)
    docs = [e for e in extended_entries if e.__class__.__name__ == "Document"]
    assert len(docs) == 1
    assert "receipt" in docs[0].tags
    assert docs[0].account == "Expenses:Francis:Electronics"
    receipt_errors = [e for e in errors if e.__class__.__name__ == "ReceiptTransactionError"]
    assert len(receipt_errors) == 0


def test_missing_statement_file_produces_error(load_doc, tmp_path):
    missing = tmp_path / "does-not-exist.pdf"
    # not creating the file
    entries, options_map = load_doc(f"""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"
        2000-01-01 open Assets:Francis:Bank
        2000-01-01 open Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-04-01 balance Assets:Francis:Bank 1 GBP
          statement: "{missing}"
    """)
    _, errors = validate_transactions(entries, options_map)
    not_found_errors = [e for e in errors if e.__class__.__name__ == "DocumentFileNotFoundError"]
    assert len(not_found_errors) == 1
    assert "File not found" in not_found_errors[0].message
