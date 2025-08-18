import unittest
from unittest.mock import patch

from ..validate_transactions import validate_transactions
from beancount.core import data
from beancount.parser import options
from beancount import loader


class TestValidatePayslipTransactions(unittest.TestCase):

    @loader.load_doc()
    def test_valid_payslip_transaction(self, entries, _, options_map):
        """
        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Equity:Francis:OpeningBalances
        2000-01-01 * #opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open  Expenses:Francis:Test
        2000-01-01 * #payslip
          payslip: "mock/path/to/payslip"
          Assets:Francis:Bank        1 GBP
          Expenses:Francis:Test        -1 GBP
        """
        with patch('os.path.isfile') as mock_os_is_file:
            mock_os_is_file.return_value = True

            _, errors = validate_transactions(entries, options_map)
            self.assertEqual(0, len(errors))

    @loader.load_doc()
    def test_invalid_payslip_transaction_missing_payslip_metadata(self, entries, _, options_map):
        """
        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Equity:Francis:OpeningBalances
        2000-01-01 * #opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open  Income:Francis:Job
        2000-01-01 * #payslip
          Assets:Francis:Bank        1 GBP
          Income:Francis:Job        -1 GBP
        """
        with patch('os.path.isfile') as mock_os_is_file:
            mock_os_is_file.return_value = True

            _, errors = validate_transactions(entries, options_map)
            self.assertEqual(1, len(errors))
            self.assertEqual(
                errors[0].message, "Missing required metadata of 'payslip'"
            )

    @loader.load_doc()
    def test_invalid_payslip_transaction_incorrect_filepath(self, entries, _, options_map):
        """
        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Equity:Francis:OpeningBalances
        2000-01-01 * #opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open  Income:Francis:Job
        2000-01-01 * #payslip
          payslip: "mock/incorrect/path/to/payslip"
          Assets:Francis:Bank        1 GBP
          Income:Francis:Job        -1 GBP
        """
        with patch('os.path.isfile') as mock_os_is_file:
            mock_os_is_file.return_value = False

            _, errors = validate_transactions(entries, options_map)
            self.assertEqual(1, len(errors))
            self.assertEqual(
                errors[0].message, "Invalid payslip file path"
            )

if __name__ == "__main__":
    unittest.main()
