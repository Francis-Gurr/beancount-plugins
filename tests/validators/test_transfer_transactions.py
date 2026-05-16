from beancount_plugins.validators.transactions import validate_transactions


def test_valid_from_transfer_transaction(load_doc):
    entries, options_map = load_doc("""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"

        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open  Assets:Francis:Transfers:Self
        2000-01-01 * "Self" "Transfer from self: Other Bank" #transfer-from-self
          Assets:Francis:Bank        1 GBP
          Assets:Francis:Transfers:Self    -1 GBP
    """)
    _, errors = validate_transactions(entries, options_map)
    assert len(errors) == 0


def test_valid_to_transfer_transaction(load_doc):
    entries, options_map = load_doc("""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"

        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open  Assets:Francis:Transfers:Self
        2000-01-01 * "Self" "Transfer to self: Other Bank" #transfer-to-self
          Assets:Francis:Bank        -1 GBP
          Assets:Francis:Transfers:Self    1 GBP
    """)
    _, errors = validate_transactions(entries, options_map)
    assert len(errors) == 0


def test_invalid_transfer_transaction_multiple_tags(load_doc):
    entries, options_map = load_doc("""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"

        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open  Assets:Francis:Transfers:Self
        2000-01-01 * "Self" "Transfer to self: Other Bank" #transfer-to-self #savings
          Assets:Francis:Bank        -1 GBP
          Assets:Francis:Transfers:Self    1 GBP
    """)
    _, errors = validate_transactions(entries, options_map)
    assert len(errors) == 1
    assert errors[0].message == "Transfer transaction must have exactly one tag"


def test_invalid_transfer_transaction_tag(load_doc):
    entries, options_map = load_doc("""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"

        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open  Assets:Francis:Transfers:Self
        2000-01-01 * "Self" "Transfer to self: Other Bank" #transfer-tag
          Assets:Francis:Bank        -1 GBP
          Assets:Francis:Transfers:Self    1 GBP
    """)
    _, errors = validate_transactions(entries, options_map)
    assert len(errors) == 1
    assert errors[0].message == "Invalid transfer tag: transfer-tag"


def test_invalid_transfer_transaction_payee(load_doc):
    entries, options_map = load_doc("""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"

        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open  Assets:Francis:Transfers:Self
        2000-01-01 * "Francis" "Transfer to self: Other Bank" #transfer-to-self
          Assets:Francis:Bank        -1 GBP
          Assets:Francis:Transfers:Self    1 GBP
    """)
    _, errors = validate_transactions(entries, options_map)
    assert len(errors) == 1
    assert errors[0].message == "Payee must be Self"


def test_invalid_transfer_transaction_narration(load_doc):
    entries, options_map = load_doc("""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"

        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open  Assets:Francis:Transfers:Self
        2000-01-01 * "Self" "Transfer to Other Bank" #transfer-to-self
          Assets:Francis:Bank        -1 GBP
          Assets:Francis:Transfers:Self    1 GBP
    """)
    _, errors = validate_transactions(entries, options_map)
    assert len(errors) == 1
    assert errors[0].message == "Narration must start with Transfer to self: "


def test_invalid_transfer_transaction_multiple_postings(load_doc):
    entries, options_map = load_doc("""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"

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
    """)
    _, errors = validate_transactions(entries, options_map)
    assert len(errors) == 1
    assert errors[0].message == "Second posting must be to: Assets:Francis:Transfers:Self"


def test_invalid_transfer_transaction_second_posting_account(load_doc):
    entries, options_map = load_doc("""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"

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
    """)
    _, errors = validate_transactions(entries, options_map)
    assert len(errors) == 1
    assert errors[0].message == "Transfer transaction must have exactly two postings"


def test_invalid_from_transfer_transaction_second_posting_amount_sign(load_doc):
    entries, options_map = load_doc("""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"

        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open  Assets:Francis:Transfers:Self
        2000-01-01 * "Self" "Transfer from self: Other Bank" #transfer-from-self
          Assets:Francis:Bank        -1 GBP
          Assets:Francis:Transfers:Self    1 GBP
    """)
    _, errors = validate_transactions(entries, options_map)
    assert len(errors) == 1
    assert errors[0].message == "First posting amount must be positive for transfer from"


def test_invalid_to_transfer_transaction_second_posting_amount_sign(load_doc):
    entries, options_map = load_doc("""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"

        2000-01-01 open  Assets:Francis:Bank
        2000-01-01 open  Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-01-01 open  Assets:Francis:Transfers:Self
        2000-01-01 * "Self" "Transfer to self: Other Bank" #transfer-to-self
          Assets:Francis:Bank        1 GBP
          Assets:Francis:Transfers:Self    -1 GBP
    """)
    _, errors = validate_transactions(entries, options_map)
    assert len(errors) == 1
    assert errors[0].message == "First posting amount must be negative for transfer to"
