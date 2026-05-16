from beancount_plugins.validators.transactions import validate_transactions


def test_valid_simple_event(load_doc):
    entries, options_map = load_doc("""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"
        2000-01-01 open Assets:Francis:Bank
        2000-01-01 open Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-02-01 event "address" "10 Downing Street"
        2000-03-01 event "employment" "Acme Inc"
        2000-04-01 event "relationship" "Married"
    """)
    _, errors = validate_transactions(entries, options_map)
    event_errors = [e for e in errors if "Event" in e.__class__.__name__]
    assert len(event_errors) == 0


def test_invalid_event_type(load_doc):
    entries, options_map = load_doc("""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"
        2000-01-01 open Assets:Francis:Bank
        2000-01-01 open Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-02-01 event "not-a-known-event" "Some description"
    """)
    _, errors = validate_transactions(entries, options_map)
    event_errors = [e for e in errors if e.__class__.__name__ == "EventError"]
    assert len(event_errors) == 1
    assert event_errors[0].message == "Event type 'not-a-known-event' is invalid"


def test_valid_linked_event_with_id(load_doc):
    entries, options_map = load_doc("""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"
        2000-01-01 open Assets:Francis:Bank
        2000-01-01 open Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-02-01 event "trip" "Paris weekend"
          id: "paris-2000"
        2000-02-15 event "work_trip" "Berlin conference"
          id: "berlin-2000"
    """)
    _, errors = validate_transactions(entries, options_map)
    event_errors = [e for e in errors if "Event" in e.__class__.__name__]
    assert len(event_errors) == 0


def test_linked_event_missing_id(load_doc):
    entries, options_map = load_doc("""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"
        2000-01-01 open Assets:Francis:Bank
        2000-01-01 open Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-02-01 event "trip" "Paris weekend"
    """)
    _, errors = validate_transactions(entries, options_map)
    event_errors = [e for e in errors if e.__class__.__name__ == "EventError"]
    assert len(event_errors) == 1
    assert event_errors[0].message == "Missing 'id' field in meta"


def test_duplicate_linked_event_id(load_doc):
    entries, options_map = load_doc("""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"
        2000-01-01 open Assets:Francis:Bank
        2000-01-01 open Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-02-01 event "trip" "Paris weekend"
          id: "shared-id"
        2000-03-01 event "trip" "London weekend"
          id: "shared-id"
    """)
    _, errors = validate_transactions(entries, options_map)
    event_errors = [e for e in errors if e.__class__.__name__ == "EventError"]
    assert len(event_errors) == 1
    assert event_errors[0].message == "Duplicate event id"


def test_event_transaction_references_existing_event(load_doc):
    entries, options_map = load_doc("""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"
        2000-01-01 open Assets:Francis:Bank
        2000-01-01 open Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-02-01 event "trip" "Paris weekend"
          id: "paris-2000"

        2000-02-02 open Expenses:Francis:Food
        2000-02-02 * "Restaurant" "Lunch" #event-paris-2000
          Assets:Francis:Bank        -10 GBP
          Expenses:Francis:Food       10 GBP
    """)
    _, errors = validate_transactions(entries, options_map)
    event_txn_errors = [e for e in errors if e.__class__.__name__ == "EventTransactionError"]
    assert len(event_txn_errors) == 0


def test_event_transaction_references_unknown_event(load_doc):
    entries, options_map = load_doc("""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"
        2000-01-01 open Assets:Francis:Bank
        2000-01-01 open Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-02-02 open Expenses:Francis:Food
        2000-02-02 * "Restaurant" "Lunch" #event-unknown-id
          Assets:Francis:Bank        -10 GBP
          Expenses:Francis:Food       10 GBP
    """)
    _, errors = validate_transactions(entries, options_map)
    event_txn_errors = [e for e in errors if e.__class__.__name__ == "EventTransactionError"]
    assert len(event_txn_errors) == 1
    assert event_txn_errors[0].message == "Linked event not found"


def test_event_transaction_with_multiple_event_tags(load_doc):
    entries, options_map = load_doc("""
        2000-01-01 custom "initialise_journal_file" "Francis" "Assets:Francis:Bank"
        2000-01-01 open Assets:Francis:Bank
        2000-01-01 open Equity:Francis:OpeningBalances
        2000-01-01 * #journal-opening-balance
          Assets:Francis:Bank        1 GBP
          Equity:Francis:OpeningBalances    -1 GBP

        2000-02-01 event "trip" "Paris weekend"
          id: "paris-2000"
        2000-02-15 event "trip" "London weekend"
          id: "london-2000"

        2000-02-20 open Expenses:Francis:Food
        2000-02-20 * "Restaurant" "Lunch" #event-paris-2000 #event-london-2000
          Assets:Francis:Bank        -10 GBP
          Expenses:Francis:Food       10 GBP
    """)
    _, errors = validate_transactions(entries, options_map)
    event_txn_errors = [e for e in errors if e.__class__.__name__ == "EventTransactionError"]
    assert len(event_txn_errors) == 1
    assert event_txn_errors[0].message == "Cannot have multiple event tags"
