import unittest

from ..validate_shared_ratio import validate_shared_ratio
from beancount.core import data
from beancount.parser import options
from beancount import loader


class TestValidateSharedRatio(unittest.TestCase):

    @loader.load_doc()
    def test_valid_shared_ratio(self, entries, _, options_map):
        """
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

        """
        _, errors = validate_shared_ratio(entries, options_map)
        self.assertEqual(0, len(errors))

    @loader.load_doc()
    def test_invalid_shared_ratio_missing_policy(self, entries, _, options_map):
        """
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

        """
        _, errors = validate_shared_ratio(entries, options_map)
        self.assertEqual(1, len(errors))
        self.assertEqual(
            errors[0].message,
            "Shared ratio is not provided. Provide the shared ratio using the custom autobean.share.policy directive.",
        )

    @loader.load_doc()
    def test_invalid_shared_ratio_incorrect_ratio(self, entries, _, options_map):
        """
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

        """
        _, errors = validate_shared_ratio(entries, options_map)
        self.assertEqual(1, len(errors))
        self.assertEqual(
            errors[0].message,
            "Shared ratio is incorrect. Actual: {'Francis': '1', 'Leyna': '0.5'}, Provided: {'Francis': '1', 'Leyna': '0.6'}",
        )


if __name__ == "__main__":
    unittest.main()
