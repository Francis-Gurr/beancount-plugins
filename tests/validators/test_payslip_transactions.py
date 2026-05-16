from beancount_plugins.validators.transactions import validate_transactions


def test_valid_payslip_transaction(load_doc):
    entries, options_map = load_doc("""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"
        2000-01-01 open Assets:Francis:Bank
        2000-01-01 open Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open Income:Francis:GrossPay:Salary
        2000-01-01 * "Employer" "January salary" #payslip
          payslip: "jan.pdf"
          Assets:Francis:Bank             1000 GBP
          Income:Francis:GrossPay:Salary -1000 GBP
    """)
    _, errors = validate_transactions(entries, options_map)
    payslip_errors = [e for e in errors if e.__class__.__name__ == "PayslipTransactionError"]
    assert len(payslip_errors) == 0


def test_payslip_missing_tag(load_doc):
    entries, options_map = load_doc("""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"
        2000-01-01 open Assets:Francis:Bank
        2000-01-01 open Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open Income:Francis:GrossPay:Salary
        2000-01-01 * "Employer" "January salary"
          payslip: "jan.pdf"
          Assets:Francis:Bank             1000 GBP
          Income:Francis:GrossPay:Salary -1000 GBP
    """)
    _, errors = validate_transactions(entries, options_map)
    payslip_errors = [e for e in errors if e.__class__.__name__ == "PayslipTransactionError"]
    assert len(payslip_errors) == 1
    assert payslip_errors[0].message == "Missing required tag of 'payslip'"


def test_payslip_missing_meta(load_doc):
    entries, options_map = load_doc("""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"
        2000-01-01 open Assets:Francis:Bank
        2000-01-01 open Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open Income:Francis:GrossPay:Salary
        2000-01-01 * "Employer" "January salary" #payslip
          Assets:Francis:Bank             1000 GBP
          Income:Francis:GrossPay:Salary -1000 GBP
    """)
    _, errors = validate_transactions(entries, options_map)
    payslip_errors = [e for e in errors if e.__class__.__name__ == "PayslipTransactionError"]
    assert len(payslip_errors) == 1
    assert payslip_errors[0].message == "Missing required metadata of 'payslip'"


def test_payslip_wrong_salary_account(load_doc):
    entries, options_map = load_doc("""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"
        2000-01-01 open Assets:Francis:Bank
        2000-01-01 open Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open Income:Francis:Wages
        2000-01-01 * "Employer" "January salary" #payslip
          payslip: "jan.pdf"
          Assets:Francis:Bank   1000 GBP
          Income:Francis:Wages -1000 GBP
    """)
    _, errors = validate_transactions(entries, options_map)
    payslip_errors = [e for e in errors if e.__class__.__name__ == "PayslipTransactionError"]
    assert len(payslip_errors) == 1
    assert payslip_errors[0].message == "Second posting account should be 'Income:Francis:GrossPay:Salary'"
