import datetime

from beancount_plugins.validators.transactions import validate_transactions


def test_valid_balance_assertion_with_correct_statement_date(load_doc, tmp_path):
    # entry.date + 1 month - 1 day = 2000-04-30
    statement = tmp_path / "2000-04-30.pdf"
    statement.touch()
    entries, options_map = load_doc(f"""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"
        2000-01-01 open Assets:Francis:Bank
        2000-01-01 open Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-04-01 balance Assets:Francis:Bank 1 GBP
          statement: "{statement}"
    """)
    _, errors = validate_transactions(entries, options_map)
    assert len(errors) == 0


def test_valid_balance_assertion_with_closing_statement(load_doc, tmp_path):
    closing = tmp_path / "account_closing-statement.pdf"
    closing.touch()
    entries, options_map = load_doc(f"""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"
        2000-01-01 open Assets:Francis:Bank
        2000-01-01 open Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-04-01 balance Assets:Francis:Bank 1 GBP
          statement: "{closing}"
    """)
    _, errors = validate_transactions(entries, options_map)
    assert len(errors) == 0


def test_balance_assertion_missing_statement_meta(load_doc):
    entries, options_map = load_doc("""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"
        2000-01-01 open Assets:Francis:Bank
        2000-01-01 open Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-04-01 balance Assets:Francis:Bank 1 GBP
    """)
    _, errors = validate_transactions(entries, options_map)
    assert len(errors) == 1
    assert errors[0].message == "Missing required metadata of 'statement'"


def test_balance_assertion_wrong_statement_date(load_doc, tmp_path):
    statement = tmp_path / "wrong-date.pdf"
    statement.touch()
    entries, options_map = load_doc(f"""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"
        2000-01-01 open Assets:Francis:Bank
        2000-01-01 open Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-04-01 balance Assets:Francis:Bank 1 GBP
          statement: "{statement}"
    """)
    _, errors = validate_transactions(entries, options_map)
    assert len(errors) == 1
    assert "Statement file must be date one month from the balance assertion date" in errors[0].message


def test_balance_assertion_in_the_future_drops_statement_meta(load_doc, tmp_path):
    future_date = datetime.datetime.now(tz=datetime.UTC).date() + datetime.timedelta(days=365)
    statement = tmp_path / "future.pdf"
    statement.touch()
    entries, options_map = load_doc(f"""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"
        2000-01-01 open Assets:Francis:Bank
        2000-01-01 open Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        {future_date} balance Assets:Francis:Bank 1 GBP
          statement: "{statement}"
    """)
    extended_entries, errors = validate_transactions(entries, options_map)
    assert len(errors) == 0
    balance_entries = [e for e in extended_entries if e.__class__.__name__ == "Balance"]
    assert "statement" not in balance_entries[0].meta
