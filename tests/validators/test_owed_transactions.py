from beancount_plugins.validators.transactions import validate_transactions


def test_valid_owed_transaction_to_expense_account(load_doc):
    entries, options_map = load_doc("""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"

        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open  Expenses:Leyna:Souvenirs
        2000-01-01 * "Gift Shop" "Leyna bought a souvenir" #owed-by-leyna #holiday
          Assets:Francis:Bank        1 GBP
          Expenses:Leyna:Souvenirs    -1 GBP
    """)
    _, errors = validate_transactions(entries, options_map)
    assert len(errors) == 0


def test_valid_owed_transaction_to_assets_receivables_account(load_doc):
    entries, options_map = load_doc("""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"

        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open  Assets:Leyna:Receivables:Work
        2000-01-01 * "Workplace" "Leyna bought something for work" #owed-by-leyna
          Assets:Francis:Bank        1 GBP
          Assets:Leyna:Receivables:Work    -1 GBP
    """)
    _, errors = validate_transactions(entries, options_map)
    assert len(errors) == 0


def test_valid_owed_transaction_expense_and_assets_receivables_account(load_doc):
    entries, options_map = load_doc("""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"

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
    """)
    _, errors = validate_transactions(entries, options_map)
    assert len(errors) == 0


def test_valid_owed_transaction_multiple_parties(load_doc):
    entries, options_map = load_doc("""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"

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
    """)
    _, errors = validate_transactions(entries, options_map)
    assert len(errors) == 0


def test_invalid_owed_transaction_tag(load_doc):
    entries, options_map = load_doc("""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"

        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open  Expenses:Leyna:Souvenirs
        2000-01-01 * "Gift Shop" "Leyna bought a souvenir" #owed-by #holiday
          Assets:Francis:Bank        1 GBP
          Expenses:Leyna:Souvenirs    -1 GBP
    """)
    _, errors = validate_transactions(entries, options_map)
    assert len(errors) == 1
    assert errors[0].message == "Invalid owed tag: owed-by"


def test_invalid_owed_transaction_tag_same_party(load_doc):
    entries, options_map = load_doc("""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"

        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open  Expenses:Leyna:Souvenirs
        2000-01-01 * "Gift Shop" "Leyna bought a souvenir" #owed-by-francis #holiday
          Assets:Francis:Bank        1 GBP
          Expenses:Leyna:Souvenirs    -1 GBP
    """)
    _, errors = validate_transactions(entries, options_map)
    assert len(errors) == 1
    assert errors[0].message == "Owed tag must be for another party"


def test_invalid_owed_transaction_missing_account(load_doc):
    entries, options_map = load_doc("""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"

        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open  Expenses:Francis:Souvenirs
        2000-01-01 * "Gift Shop" "Leyna bought a souvenir" #owed-by-leyna #holiday
          Assets:Francis:Bank        1 GBP
          Expenses:Francis:Souvenirs    -1 GBP
    """)
    _, errors = validate_transactions(entries, options_map)
    assert len(errors) == 1
    assert errors[0].message == (
        "Expected at least one posting to an account starting with: ['Expenses:Leyna', 'Assets:Leyna:Receivables']"
    )


def test_invalid_owed_transaction_wrong_expense_account(load_doc):
    entries, options_map = load_doc("""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"

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
    """)
    _, errors = validate_transactions(entries, options_map)
    assert len(errors) == 1
    assert errors[0].message == (
        "Posting to an account that does not belong to the party: Francis, "
        "or to any of the owed parties' allowed accounts: "
        "['Expenses:Leyna', 'Assets:Leyna:Receivables']. "
        "If this was intentional, please use the appropriate tags."
    )


def test_invalid_owed_transaction_wrong_receivables_account(load_doc):
    entries, options_map = load_doc("""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"

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
    """)
    _, errors = validate_transactions(entries, options_map)
    assert len(errors) == 1
    assert errors[0].message == (
        "Posting to an account that does not belong to the party: Francis, "
        "or to any of the owed parties' allowed accounts: "
        "['Expenses:Leyna', 'Assets:Leyna:Receivables']. "
        "If this was intentional, please use the appropriate tags."
    )
