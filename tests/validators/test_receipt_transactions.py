from beancount_plugins.validators.transactions import validate_transactions


def test_valid_valuables_transaction_with_receipt_meta(load_doc):
    entries, options_map = load_doc("""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"
        2000-01-01 open Assets:Francis:Bank
        2000-01-01 open Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open Expenses:Francis:Electronics
        2000-01-01 * "Camera shop" "New camera" #valuables
          Assets:Francis:Bank        -100 GBP
          Expenses:Francis:Electronics   100 GBP
            receipt: "receipt.pdf"
    """)
    _, errors = validate_transactions(entries, options_map)
    receipt_errors = [e for e in errors if e.__class__.__name__ == "ReceiptTransactionError"]
    assert len(receipt_errors) == 0


def test_receipt_meta_without_valuables_tag(load_doc):
    entries, options_map = load_doc("""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"
        2000-01-01 open Assets:Francis:Bank
        2000-01-01 open Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open Expenses:Francis:Electronics
        2000-01-01 * "Camera shop" "New camera"
          Assets:Francis:Bank        -100 GBP
          Expenses:Francis:Electronics   100 GBP
            receipt: "receipt.pdf"
    """)
    _, errors = validate_transactions(entries, options_map)
    receipt_errors = [e for e in errors if e.__class__.__name__ == "ReceiptTransactionError"]
    assert len(receipt_errors) == 1
    assert receipt_errors[0].message == "Missing required tag of 'valuables'"


def test_valuables_tag_without_receipt_meta(load_doc):
    entries, options_map = load_doc("""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"
        2000-01-01 open Assets:Francis:Bank
        2000-01-01 open Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open Expenses:Francis:Electronics
        2000-01-01 * "Camera shop" "New camera" #valuables
          Assets:Francis:Bank        -100 GBP
          Expenses:Francis:Electronics   100 GBP
    """)
    _, errors = validate_transactions(entries, options_map)
    receipt_errors = [e for e in errors if e.__class__.__name__ == "ReceiptTransactionError"]
    assert len(receipt_errors) == 1
    assert receipt_errors[0].message == "Missing required metadata of 'receipt'"


def test_receipt_on_non_expense_account(load_doc):
    entries, options_map = load_doc("""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"
        2000-01-01 open Assets:Francis:Bank
        2000-01-01 open Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open Assets:Francis:Valuables
        2000-01-01 * "Camera shop" "New camera" #valuables
          Assets:Francis:Bank        -100 GBP
          Assets:Francis:Valuables    100 GBP
            receipt: "receipt.pdf"
    """)
    _, errors = validate_transactions(entries, options_map)
    receipt_errors = [
        e
        for e in errors
        if e.__class__.__name__ == "ReceiptTransactionError"
        and e.message == "Transactions with receipt metadata must be to an expense account"
    ]
    assert len(receipt_errors) == 1
