from beancount_plugins.validators.transactions import validate_transactions


def test_valid_default_transaction(load_doc):
    entries, options_map = load_doc("""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"

        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open  Expenses:Francis
        2000-01-01 *
          Assets:Francis:Bank        1 GBP
          Expenses:Francis        -1 GBP
    """)
    _, errors = validate_transactions(entries, options_map)
    assert len(errors) == 0


def test_invalid_default_transaction_order(load_doc):
    entries, options_map = load_doc("""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"

        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open  Expenses:Francis
        2000-01-01 *
          Expenses:Francis        -1 GBP
          Assets:Francis:Bank        1 GBP
    """)
    _, errors = validate_transactions(entries, options_map)
    assert len(errors) == 1
    assert errors[0].message == "The first posting should be to the account: Assets:Francis:Bank"


def test_invalid_default_transaction_to_transfer_account(load_doc):
    entries, options_map = load_doc("""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"

        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open  Assets:Francis:Transfers:Elsewhere
        2000-01-01 *
          Assets:Francis:Bank        1 GBP
          Assets:Francis:Transfers:Elsewhere -1 GBP
    """)
    _, errors = validate_transactions(entries, options_map)
    assert len(errors) == 1
    assert errors[0].message == "Transfer transaction must have exactly one tag"


def test_invalid_default_transaction_to_another_party(load_doc):
    entries, options_map = load_doc("""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"

        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open  Assets:OtherParty:Bank
        2000-01-01 *
          Assets:Francis:Bank        1 GBP
          Assets:OtherParty:Bank -1 GBP
    """)
    _, errors = validate_transactions(entries, options_map)
    assert len(errors) == 1
    assert errors[0].message == (
        "Posting to an account that does not belong to the party: Francis, "
        "or to any of the owed parties' allowed accounts: []. "
        "If this was intentional, please use the appropriate tags."
    )


def test_invalid_default_transaction_multiple(load_doc):
    entries, options_map = load_doc("""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"

        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open  Assets:Francis:Transfers:Elsewhere
        2000-01-01 open  Assets:OtherParty:Bank
        2000-01-01 *
          Assets:Francis:Transfers:Elsewhere -1 GBP
          Assets:Francis:Bank        2 GBP
          Assets:OtherParty:Bank -1 GBP
    """)
    _, errors = validate_transactions(entries, options_map)
    assert len(errors) == 2
