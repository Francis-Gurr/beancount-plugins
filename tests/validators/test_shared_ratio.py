from decimal import Decimal

from beancount_plugins.validators.shared_ratio import calculate_shared_ratio, validate_shared_ratio


def test_calculate_shared_ratio_zero_income_does_not_crash():
    result = calculate_shared_ratio({"Francis": Decimal(0), "Leyna": Decimal(0)})
    assert result == {"Francis": Decimal(0), "Leyna": Decimal(0)}


def test_shared_ratio_no_income_transactions(load_doc):
    """Policy declared but no income entries to verify against — produces 'incorrect ratio' error, not a crash."""
    entries, options_map = load_doc("""
        2000-01-01 custom "autobean.share.policy" "shared"
          share-Francis: 1
          share-Leyna: 0.5
        2000-01-01 custom "journal account name" "Assets:Francis:Bank"
        2000-01-01 open  Assets:Francis:Bank
    """)
    _, errors = validate_shared_ratio(entries, options_map)
    assert len(errors) == 1
    assert "Shared ratio is incorrect" in errors[0].message


def test_valid_shared_ratio(load_doc):
    entries, options_map = load_doc("""
        2000-01-01 custom "autobean.share.policy" "shared"
          share-Francis: 1
          share-Leyna: 0.5
          share_enforced: TRUE
          share_prorated_included: FALSE


        2000-01-01 custom "journal account name" "Assets:Francis:Bank"

        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Income:Francis:GrossPay:Salary
        2000-01-01 open  Income:Francis:GrossPay:Bonus
        2000-01-01 open  Expenses:Francis:Taxes

        2000-01-01 * "Francis Payslip"
          Assets:Francis:Bank        200 GBP
          Income:Francis:GrossPay:Salary    -130 GBP
          Income:Francis:GrossPay:Bonus    -130 GBP
          Expenses:Francis:Taxes        60 GBP


        2000-01-01 custom "journal account name" "Assets:Leyna:Bank"

        2000-01-01 open  Assets:Leyna:Bank
        2000-01-01 open  Income:Leyna:GrossPay:Salary
        2000-01-01 open  Income:Leyna:GrossPay:Bonus
        2000-01-01 open  Expenses:Leyna:Taxes

        2000-01-01 * "Leyna Payslip"
          Assets:Leyna:Bank        100 GBP
          Income:Leyna:GrossPay:Salary    -65 GBP
          Income:Leyna:GrossPay:Bonus    -65 GBP
          Expenses:Leyna:Taxes        30 GBP
    """)
    _, errors = validate_shared_ratio(entries, options_map)
    assert len(errors) == 0


def test_invalid_shared_ratio_missing_policy(load_doc):
    entries, options_map = load_doc("""
        2000-01-01 custom "journal account name" "Assets:Francis:Bank"

        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Income:Francis:GrossPay:Salary
        2000-01-01 open  Income:Francis:GrossPay:Bonus
        2000-01-01 open  Expenses:Francis:Taxes

        2000-01-01 * "Francis Payslip"
          Assets:Francis:Bank        200 GBP
          Income:Francis:GrossPay:Salary    -130 GBP
          Income:Francis:GrossPay:Bonus    -130 GBP
          Expenses:Francis:Taxes        60 GBP

        2000-01-01 custom "journal account name" "Assets:Leyna:Bank"

        2000-01-01 open  Assets:Leyna:Bank
        2000-01-01 open  Income:Leyna:GrossPay:Salary
        2000-01-01 open  Income:Leyna:GrossPay:Bonus
        2000-01-01 open  Expenses:Leyna:Taxes

        2000-01-01 * "Leyna Payslip"
          Assets:Leyna:Bank        100 GBP
          Income:Leyna:GrossPay:Salary    -65 GBP
          Income:Leyna:GrossPay:Bonus    -65 GBP
          Expenses:Leyna:Taxes        30 GBP
    """)
    _, errors = validate_shared_ratio(entries, options_map)
    assert len(errors) == 1
    assert errors[0].message == (
        "Shared ratio is not provided. Provide the shared ratio using the custom autobean.share.policy directive."
    )


def test_invalid_shared_ratio_incorrect_ratio(load_doc):
    entries, options_map = load_doc("""
        2000-01-01 custom "autobean.share.policy" "shared"
          share-Francis: 1
          share-Leyna: 0.6
          share_enforced: TRUE
          share_prorated_included: FALSE

        2000-01-01 custom "journal account name" "Assets:Francis:Bank"

        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Income:Francis:GrossPay:Salary
        2000-01-01 open  Income:Francis:GrossPay:Bonus
        2000-01-01 open  Expenses:Francis:Taxes

        2000-01-01 * "Francis Payslip"
          Assets:Francis:Bank        200 GBP
          Income:Francis:GrossPay:Salary    -130 GBP
          Income:Francis:GrossPay:Bonus    -130 GBP
          Expenses:Francis:Taxes        60 GBP

        2000-01-01 custom "journal account name" "Assets:Leyna:Bank"

        2000-01-01 open  Assets:Leyna:Bank
        2000-01-01 open  Income:Leyna:GrossPay:Salary
        2000-01-01 open  Income:Leyna:GrossPay:Bonus
        2000-01-01 open  Expenses:Leyna:Taxes

        2000-01-01 * "Leyna Payslip"
          Assets:Leyna:Bank        100 GBP
          Income:Leyna:GrossPay:Salary    -65 GBP
          Income:Leyna:GrossPay:Bonus    -65 GBP
          Expenses:Leyna:Taxes        30 GBP
    """)
    _, errors = validate_shared_ratio(entries, options_map)
    assert len(errors) == 1
    assert errors[0].message == (
        "Shared ratio is incorrect. Actual: {'Francis': '1', 'Leyna': '0.5'}, "
        "Provided: {'Francis': '1', 'Leyna': '0.6'}"
    )
