import unittest

from ..validate_transactions import validate_transactions
from beancount.core import data
from beancount.parser import options
from beancount import loader


class TestValidateOwedTransactions(unittest.TestCase):

    @loader.load_doc()
    def test_valid_owed_transaction_to_expense_account(self, entries, _, options_map):
        """
        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open  Expenses:Leyna:Souvenirs
        2000-01-01 * "Gift Shop" "Leyna bought a souvenir" #owed-by-leyna #holiday
          Assets:Francis:Bank        1 GBP
          Expenses:Leyna:Souvenirs    -1 GBP
        """
        _, errors = validate_transactions(entries, options_map)
        self.assertEqual(0, len(errors))

    @loader.load_doc()
    def test_valid_owed_transaction_to_assets_receivables_account(self, entries, _, options_map):
        """
        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open  Assets:Leyna:Receivables:Work
        2000-01-01 * "Workplace" "Leyna bought something for work" #owed-by-leyna
          Assets:Francis:Bank        1 GBP
          Assets:Leyna:Receivables:Work    -1 GBP
        """
        _, errors = validate_transactions(entries, options_map)
        self.assertEqual(0, len(errors))

    @loader.load_doc()
    def test_valid_owed_transaction_expense_and_assets_receivables_account(
        self, entries, _, options_map
    ):
        """
        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open  Assets:Leyna:Receivables:Work
        2000-01-01 open  Expenses:Leyna:Souvenirs
        2000-01-01 * "Multiple" "Leyna bought something for work and a souvenir" #owed-by-leyna
          Assets:Francis:Bank        2 GBP
          Assets:Leyna:Receivables:Work    -1 GBP
          Expenses:Leyna:Souvenirs    -1 GBP
        """
        _, errors = validate_transactions(entries, options_map)
        self.assertEqual(0, len(errors))

    @loader.load_doc()
    def test_valid_owed_transaction_multiple_parties(self, entries, _, options_map):
        """
        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open  Assets:Leyna:Receivables:Work
        2000-01-01 open  Expenses:Shared:Souvenirs
        2000-01-01 * "Multiple" "Leyna bought something for work and we bought a souvenir" #owed-by-leyna #owed-by-shared #holiday
          Assets:Francis:Bank        2 GBP
          Assets:Leyna:Receivables:Work    -1 GBP
          Expenses:Shared:Souvenirs    -1 GBP
        """
        _, errors = validate_transactions(entries, options_map)
        self.assertEqual(0, len(errors))

    @loader.load_doc()
    def test_invalid_owed_transaction_tag(self, entries, _, options_map):
        """
        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open  Expenses:Leyna:Souvenirs
        2000-01-01 * "Gift Shop" "Leyna bought a souvenir" #owed-by #holiday
          Assets:Francis:Bank        1 GBP
          Expenses:Leyna:Souvenirs    -1 GBP
        """
        _, errors = validate_transactions(entries, options_map)
        self.assertEqual(1, len(errors))
        self.assertEqual(errors[0].message, "Invalid owed tag: owed-by")

    @loader.load_doc()
    def test_invalid_owed_transaction_tag_same_party(self, entries, _, options_map):
        """
        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open  Expenses:Leyna:Souvenirs
        2000-01-01 * "Gift Shop" "Leyna bought a souvenir" #owed-by-francis #holiday
          Assets:Francis:Bank        1 GBP
          Expenses:Leyna:Souvenirs    -1 GBP
        """
        _, errors = validate_transactions(entries, options_map)
        self.assertEqual(1, len(errors))
        self.assertEqual(errors[0].message, "Owed tag must be for another party")

    @loader.load_doc()
    def test_invalid_owed_transaction_missing_account(self, entries, _, options_map):
        """
        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open  Expenses:Francis:Souvenirs
        2000-01-01 * "Gift Shop" "Leyna bought a souvenir" #owed-by-leyna #holiday
          Assets:Francis:Bank        1 GBP
          Expenses:Francis:Souvenirs    -1 GBP
        """
        _, errors = validate_transactions(entries, options_map)
        self.assertEqual(1, len(errors))
        self.assertEqual(
            errors[0].message,
            "Expected at least one posting to an account starting with: ['Expenses:Leyna', 'Assets:Leyna:Receivables']",
        )

    @loader.load_doc()
    def test_invalid_owed_transaction_wrong_expense_account(self, entries, _, options_map):
        """
        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open  Expenses:Leyna:Souvenirs
        2000-01-01 open  Expenses:OtherParty:Souvenirs
        2000-01-01 * "Gift Shop" "Leyna bought a souvenir" #owed-by-leyna #holiday
          Assets:Francis:Bank        2 GBP
          Expenses:Leyna:Souvenirs    -1 GBP
          Expenses:OtherParty:Souvenirs    -1 GBP
        """
        _, errors = validate_transactions(entries, options_map)
        self.assertEqual(1, len(errors))
        self.assertEqual(
            errors[0].message,
            "Posting to an account that does not belong to the party: Francis, or to any of the owed parties' allowed accounts: ['Expenses:Leyna', 'Assets:Leyna:Receivables']. If this was intentional, please use the appropriate tags.",
        )

    @loader.load_doc()
    def test_invalid_owed_transaction_wrong_receivables_account(self, entries, _, options_map):
        """
        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open  Expenses:Leyna:Souvenirs
        2000-01-01 open  Assets:Receivables:OtherParty:Work
        2000-01-01 * "Gift Shop" "Leyna bought a souvenir" #owed-by-leyna #holiday
          Assets:Francis:Bank        2 GBP
          Expenses:Leyna:Souvenirs    -1 GBP
          Assets:Receivables:OtherParty:Work    -1 GBP
        """
        _, errors = validate_transactions(entries, options_map)
        self.assertEqual(1, len(errors))
        self.assertEqual(
            errors[0].message,
            "Posting to an account that does not belong to the party: Francis, or to any of the owed parties' allowed accounts: ['Expenses:Leyna', 'Assets:Leyna:Receivables']. If this was intentional, please use the appropriate tags.",
        )


if __name__ == "__main__":
    unittest.main()
