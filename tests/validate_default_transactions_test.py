import unittest

from ..validate_transactions import validate_transactions
from beancount.core import data
from beancount.parser import options
from beancount import loader


class TestValidateDefaultTransactions(unittest.TestCase):

    @loader.load_doc()
    def test_valid_default_transaction(self, entries, _, options_map):
        """
        2000-01-01 custom "journal account name" "Assets:Francis:Bank"
        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Equity:Francis:OpeningBalances

        2000-01-01 *
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP
        """
        _, errors = validate_transactions(entries, options_map)
        self.assertEqual(0, len(errors))

    @loader.load_doc()
    def test_invalid_default_transaction_missing_directive(self, entries, _, options_map):
        """
        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Equity:Francis:OpeningBalances

        2000-01-01 *
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP
        """
        _, errors = validate_transactions(entries, options_map)
        self.assertEqual(1, len(errors))
        self.assertEqual(
            errors[0].message,
            "Journal account name must be specified before transactions using the custom directive",
        )

    @loader.load_doc()
    def test_invalid_default_transaction_order(self, entries, _, options_map):
        """
        2000-01-01 custom "journal account name" "Assets:Francis:Bank"
        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Equity:Francis:OpeningBalances

        2000-01-01 *
          Equity:Francis:OpeningBalances    -1 GBP
          Assets:Francis:Bank        1 GBP
        """
        _, errors = validate_transactions(entries, options_map)
        self.assertEqual(1, len(errors))
        self.assertEqual(
            errors[0].message, "The first posting should be to the account: Assets:Francis:Bank"
        )

    @loader.load_doc()
    def test_invalid_default_transaction_to_transfer_account(self, entries, _, options_map):
        """
        2000-01-01 custom "journal account name" "Assets:Francis:Bank"
        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Assets:Francis:Transfers:Elsewhere

        2000-01-01 *
          Assets:Francis:Bank        1 GBP
          Assets:Francis:Transfers:Elsewhere -1 GBP
        """
        _, errors = validate_transactions(entries, options_map)
        self.assertEqual(1, len(errors))
        self.assertEqual(
            errors[0].message, "Missing required tags for a transaction to a transfer account"
        )

    @loader.load_doc()
    def test_invalid_default_transaction_to_another_party(self, entries, _, options_map):
        """
        2000-01-01 custom "journal account name" "Assets:Francis:Bank"
        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Assets:OtherParty:Bank

        2000-01-01 *
          Assets:Francis:Bank        1 GBP
          Assets:OtherParty:Bank -1 GBP
        """
        _, errors = validate_transactions(entries, options_map)
        self.assertEqual(1, len(errors))
        self.assertEqual(
            errors[0].message,
            "Posting to an account that does not belong to the party: Francis. If this was intentional, please use the appropriate tags",
        )

    @loader.load_doc()
    def test_invalid_default_transaction_multiple(self, entries, _, options_map):
        """
        2000-01-01 custom "journal account name" "Assets:Francis:Bank"
        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Assets:Francis:Transfers:Elsewhere
        2000-01-01 open  Assets:OtherParty:Bank

        2000-01-01 *
          Assets:Francis:Transfers:Elsewhere -1 GBP
          Assets:Francis:Bank        2 GBP
          Assets:OtherParty:Bank -1 GBP
        """
        _, errors = validate_transactions(entries, options_map)
        self.assertEqual(3, len(errors))


if __name__ == "__main__":
    unittest.main()
