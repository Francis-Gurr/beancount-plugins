import unittest
from unittest.mock import patch

from ..validate_transactions import validate_transactions
from beancount.core import data
from beancount.parser import options
from beancount import loader


class TestValidateValuablesTransactions(unittest.TestCase):

    @loader.load_doc()
    def test_valid_valuables_transaction(self, entries, _, options_map):
        """
        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Equity:Francis:OpeningBalances
        2000-01-01 * #opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open  Expenses:Francis:Test
        2000-01-01 * #valuables
          Assets:Francis:Bank        1 GBP
          Expenses:Francis:Test        -1 GBP
            receipt: "mock/path/to/receipt"
        """
        with patch('os.path.isfile') as mock_os_is_file:
            mock_os_is_file.return_value = True

            _, errors = validate_transactions(entries, options_map)
            self.assertEqual(0, len(errors))

    @loader.load_doc()
    def test_invalid_valuables_transaction_missing_receipt_metadata(self, entries, _, options_map):
        """
        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Equity:Francis:OpeningBalances
        2000-01-01 * #opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open  Expenses:Francis:Test
        2000-01-01 * #valuables
          Assets:Francis:Bank        1 GBP
          Expenses:Francis:Test        -1 GBP
        """
        with patch('os.path.isfile') as mock_os_is_file:
            mock_os_is_file.return_value = True

            _, errors = validate_transactions(entries, options_map)
            self.assertEqual(1, len(errors))
            self.assertEqual(
                errors[0].message, "Missing required metadata of 'receipt' for valuables"
            )

    @loader.load_doc()
    def test_invalid_valuables_transaction_metadata_not_on_expense_account(self, entries, _, options_map):
        """
        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Assets:Francis:Other
        2000-01-01 open  Equity:Francis:OpeningBalances
        2000-01-01 * #opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open  Expenses:Francis:Test
        2000-01-01 * #valuables
          Assets:Francis:Bank        2 GBP
          Assets:Francis:Other       -1 GBP
            receipt: "mock/path/to/receipt"
          Expenses:Francis:Test        -1 GBP
        """
        with patch('os.path.isfile') as mock_os_is_file:
            mock_os_is_file.return_value = True

            _, errors = validate_transactions(entries, options_map)
            self.assertEqual(1, len(errors))
            self.assertEqual(
                errors[0].message, "Transactions with receipt metadata must be to an account starting with 'Expenses:Francis'"
            )

    @loader.load_doc()
    def test_invalid_valuables_transaction_incorrect_filepath(self, entries, _, options_map):
        """
        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Equity:Francis:OpeningBalances
        2000-01-01 * #opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open  Expenses:Francis:Test
        2000-01-01 * #valuables
          Assets:Francis:Bank        1 GBP
          Expenses:Francis:Test        -1 GBP
            receipt: "mock/incorrect/path/to/receipt"
        """
        with patch('os.path.isfile') as mock_os_is_file:
            mock_os_is_file.return_value = False

            _, errors = validate_transactions(entries, options_map)
            self.assertEqual(1, len(errors))
            self.assertEqual(
                errors[0].message, "Invalid receipt file path"
            )

if __name__ == "__main__":
    unittest.main()
