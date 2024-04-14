import unittest

from ..validate_transactions import validate_transactions
from beancount.core import data
from beancount.parser import options
from beancount import loader


class TestValidateOpeningBalanceTransactions(unittest.TestCase):

    @loader.load_doc()
    def test_valid_opening_balance_transaction(self, entries, _, options_map):
        """
        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP
        """
        _, errors = validate_transactions(entries, options_map)
        self.assertEqual(0, len(errors))

    @loader.load_doc()
    def test_invalid_opening_balance_transaction_tags(self, entries, _, options_map):
        """
        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance #opening-extra-tag
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP
        """
        _, errors = validate_transactions(entries, options_map)
        self.assertEqual(1, len(errors))
        self.assertEqual(
            errors[0].message,
            "Journal opening balance transaction must have exactly one tag",
        )

    @loader.load_doc()
    def test_invalid_opening_balance_transaction_multiple_postings(self, entries, _, options_map):
        """
        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Assets:Francis:OtherBank
        2000-01-01 open  Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -2 GBP
          Assets:Francis:OtherBank        1 GBP
        """
        _, errors = validate_transactions(entries, options_map)
        self.assertEqual(1, len(errors))
        self.assertEqual(
            errors[0].message,
            "Journal opening balance transaction must have exactly two postings",
        )

    @loader.load_doc()
    def test_invalid_opening_balance_transaction_not_equity(self, entries, _, options_map):
        """
        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Assets:Francis:OtherBank
        2000-01-01 open  Expenses:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Expenses:Francis:OpeningBalances    -1 GBP
        """
        _, errors = validate_transactions(entries, options_map)
        self.assertEqual(1, len(errors))
        self.assertEqual(
            errors[0].message,
            "Equity account must be the second posting",
        )

    @loader.load_doc()
    def test_invalid_opening_balance_transaction_not_opening_balance_component(
        self, entries, _, options_map
    ):
        """
        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Assets:Francis:OtherBank
        2000-01-01 open  Equity:Francis:Opening
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:Opening    -1 GBP
        """
        _, errors = validate_transactions(entries, options_map)
        self.assertEqual(1, len(errors))
        self.assertEqual(
            errors[0].message,
            "Second posting account must have a component of OpeningBalances",
        )

    @loader.load_doc()
    def test_invalid_opening_balance_transaction_no_opening_balance(self, entries, _, options_map):
        """
        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Expenses:Francis
        2000-01-01 *
          Assets:Francis:Bank        -1 GBP
          Expenses:Francis    1 GBP
        """
        _, errors = validate_transactions(entries, options_map)
        self.assertEqual(1, len(errors))
        self.assertEqual(
            errors[0].message,
            "Journal opening balance transaction must be specified before transactions",
        )


if __name__ == "__main__":
    unittest.main()
