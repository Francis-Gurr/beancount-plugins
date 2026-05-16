"""Tests for orchestrator-level concerns of validate_transactions."""

from beancount_plugins.validators.transactions import validate_transactions


def test_exclude_entry_from_validation_skips_entry(load_doc):
    """A transaction tagged #exclude-entry-from-validation produces no errors regardless of content."""
    entries, options_map = load_doc("""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"
        2000-01-01 open Assets:Francis:Bank
        2000-01-01 open Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open Assets:Francis:Transfers:Elsewhere
        2000-01-01 open Assets:OtherParty:Bank
        2000-01-01 * #exclude-entry-from-validation
          Assets:Francis:Transfers:Elsewhere -1 GBP
          Assets:Francis:Bank        2 GBP
          Assets:OtherParty:Bank -1 GBP
    """)
    _, errors = validate_transactions(entries, options_map)
    assert len(errors) == 0


def test_missing_journal_init_produces_error(load_doc):
    """A Transaction with no preceding initialise_journal_file directive yields a JournalError."""
    entries, options_map = load_doc("""
        2000-01-01 open Assets:Francis:Bank
        2000-01-01 open Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP
    """)
    _, errors = validate_transactions(entries, options_map)
    journal_errors = [e for e in errors if e.__class__.__name__ == "JournalError"]
    assert len(journal_errors) == 1
    assert "Journal party and account must be specified" in journal_errors[0].message


def test_first_transaction_must_be_opening_balance(load_doc):
    """The first Transaction in a file must be the opening balance."""
    entries, options_map = load_doc("""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"
        2000-01-01 open Assets:Francis:Bank
        2000-01-01 open Expenses:Francis
        2000-01-01 *
          Assets:Francis:Bank        -1 GBP
          Expenses:Francis            1 GBP
    """)
    _, errors = validate_transactions(entries, options_map)
    missing_ob_errors = [e for e in errors if e.__class__.__name__ == "MissingOpeningBalanceError"]
    assert len(missing_ob_errors) == 1


def test_missing_opening_balance_only_fires_once_per_file(load_doc):
    """If the first transaction is not an opening balance, only the first one is flagged."""
    entries, options_map = load_doc("""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"
        2000-01-01 open Assets:Francis:Bank
        2000-01-01 open Expenses:Francis
        2000-01-01 *
          Assets:Francis:Bank        -1 GBP
          Expenses:Francis            1 GBP
        2000-01-02 *
          Assets:Francis:Bank        -1 GBP
          Expenses:Francis            1 GBP
    """)
    _, errors = validate_transactions(entries, options_map)
    missing_ob_errors = [e for e in errors if e.__class__.__name__ == "MissingOpeningBalanceError"]
    assert len(missing_ob_errors) == 1
