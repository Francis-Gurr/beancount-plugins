import unittest

from ..validate_transactions import validate_transactions
from beancount.core import data
from beancount.parser import options
from beancount import loader


class TestValidateTransferTransactions(unittest.TestCase):

    @loader.load_doc()
    def test_valid_from_transfer_transaction(self, entries, _, options_map):
        """
        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open  Assets:Francis:Transfers:Self
        2000-01-01 * "Self" "Transfer from self: Other Bank" #transfer-from-self
          Assets:Francis:Bank        1 GBP
          Assets:Francis:Transfers:Self    -1 GBP
        """
        _, errors = validate_transactions(entries, options_map)
        self.assertEqual(0, len(errors))

    @loader.load_doc()
    def test_valid_to_transfer_transaction(self, entries, _, options_map):
        """
        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open  Assets:Francis:Transfers:Self
        2000-01-01 * "Self" "Transfer to self: Other Bank" #transfer-to-self
          Assets:Francis:Bank        -1 GBP
          Assets:Francis:Transfers:Self    1 GBP
        """
        _, errors = validate_transactions(entries, options_map)
        self.assertEqual(0, len(errors))

    @loader.load_doc()
    def test_invalid_transfer_transaction_multiple_tags(self, entries, _, options_map):
        """
        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open  Assets:Francis:Transfers:Self
        2000-01-01 * "Self" "Transfer to self: Other Bank" #transfer-to-self #savings
          Assets:Francis:Bank        -1 GBP
          Assets:Francis:Transfers:Self    1 GBP
        """
        _, errors = validate_transactions(entries, options_map)
        self.assertEqual(1, len(errors))
        self.assertEqual(errors[0].message, "Transfer transaction must have exactly one tag")

    @loader.load_doc()
    def test_invalid_transfer_transaction_tag(self, entries, _, options_map):
        """
        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open  Assets:Francis:Transfers:Self
        2000-01-01 * "Self" "Transfer to self: Other Bank" #transfer-tag
          Assets:Francis:Bank        -1 GBP
          Assets:Francis:Transfers:Self    1 GBP
        """
        _, errors = validate_transactions(entries, options_map)
        self.assertEqual(1, len(errors))
        self.assertEqual(errors[0].message, "Invalid transfer tag: transfer-tag")

    @loader.load_doc()
    def test_invalid_transfer_transaction_payee(self, entries, _, options_map):
        """
        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open  Assets:Francis:Transfers:Self
        2000-01-01 * "Francis" "Transfer to self: Other Bank" #transfer-to-self
          Assets:Francis:Bank        -1 GBP
          Assets:Francis:Transfers:Self    1 GBP
        """
        _, errors = validate_transactions(entries, options_map)
        self.assertEqual(1, len(errors))
        self.assertEqual(errors[0].message, "Payee must be Self")

    @loader.load_doc()
    def test_invalid_transfer_transaction_narration(self, entries, _, options_map):
        """
        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open  Assets:Francis:Transfers:Self
        2000-01-01 * "Self" "Transfer to Other Bank" #transfer-to-self
          Assets:Francis:Bank        -1 GBP
          Assets:Francis:Transfers:Self    1 GBP
        """
        _, errors = validate_transactions(entries, options_map)
        self.assertEqual(1, len(errors))
        self.assertEqual(errors[0].message, "Narration must start with Transfer to self: ")

    @loader.load_doc()
    def test_invalid_transfer_transaction_multiple_postings(self, entries, _, options_map):
        """
        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open  Assets:Francis:OtherBank
        2000-01-01 open  Assets:Francis:Transfers:Self
        2000-01-01 * "Self" "Transfer to self: Other Bank" #transfer-to-self
          Assets:Francis:Bank        -1 GBP
          Assets:Francis:OtherBank    1 GBP
        """
        _, errors = validate_transactions(entries, options_map)
        self.assertEqual(1, len(errors))
        self.assertEqual(
            errors[0].message, "Second posting must be to: Assets:Francis:Transfers:Self"
        )

    @loader.load_doc()
    def test_invalid_transfer_transaction_second_posting_account(self, entries, _, options_map):
        """
        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open  Assets:Francis:OtherBank
        2000-01-01 open  Assets:Francis:Transfers:Self
        2000-01-01 * "Self" "Transfer to self: Other Bank" #transfer-to-self
          Assets:Francis:Bank        -2 GBP
          Assets:Francis:Transfers:Self    1 GBP
          Assets:Francis:OtherBank    1 GBP
        """
        _, errors = validate_transactions(entries, options_map)
        self.assertEqual(1, len(errors))
        self.assertEqual(errors[0].message, "Transfer transaction must have exactly two postings")

    @loader.load_doc()
    def test_invalid_from_transfer_transaction_second_posting_amount_sign(
        self, entries, _, options_map
    ):
        """
        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open  Assets:Francis:Transfers:Self
        2000-01-01 * "Self" "Transfer from self: Other Bank" #transfer-from-self
          Assets:Francis:Bank        -1 GBP
          Assets:Francis:Transfers:Self    1 GBP
        """
        _, errors = validate_transactions(entries, options_map)
        self.assertEqual(1, len(errors))
        self.assertEqual(
            errors[0].message, "First posting amount must be positive for transfer from"
        )

    @loader.load_doc()
    def test_invalid_to_transfer_transaction_second_posting_amount_sign(
        self, entries, _, options_map
    ):
        """
        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open  Assets:Francis:Transfers:Self
        2000-01-01 * "Self" "Transfer to self: Other Bank" #transfer-to-self
          Assets:Francis:Bank        1 GBP
          Assets:Francis:Transfers:Self    -1 GBP
        """
        _, errors = validate_transactions(entries, options_map)
        self.assertEqual(1, len(errors))
        self.assertEqual(errors[0].message, "First posting amount must be negative for transfer to")


if __name__ == "__main__":
    unittest.main()
