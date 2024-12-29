# beancount-plugins

Custom beancount plugins

## Validate shared ratio

Calculates the correct ratio for the share policy `shared` and throws an error if it is incorrect.

1. Calculates the total income for Francis as:\
   The total amount into accounts with root `Assets:Francis:Bank` from accounts with root `Income:Francis:GrossPay`
2. Calculates the total income for Leyna as:\
   The total amount into accounts with root `Assets:Leyna:Bank` from accounts with root `Income:Leyna:GrossPay`
3. Calculates the income ratio `Francis:Leyna` in the form `a:b` where `(a = 1 and b < 1) or (a < 1 and b = 1)`
4. Throws an error if the calculated ratio is not the same as the ratio defined using the autobean share policy directive:
   ```
   2000-01-01 custom "autobean.share.policy" "shared"
          share-Francis: a
          share-Leyna: b
          share_enforced: TRUE
          share_prorated_included: FALSE
   ```

## Validate transactions

Validates that transactions follow certain rules.

### Opening balances
- Every journal should be for a real account (e.g. bank or credit card) and start with an opening balance transaction with the `#journal-opening-balance` tag.
- For every following transaction in the journal the first posting should be to the same account as in the `#journal-opening-balance` transaction.

### Transfers between accounts
- Have only one of the following tags: `transfer-to-self`, `transfer-to-francis`, `transfer-to-leyna`, `transfer-from-self`, `transfer-from-francis`, `transfer-from-leyna`.
- The transaction should include an account with the component `Transfers`.
- The payee must be `Self`, `Francis`, `Leyna` or `Shared` respectively.
- The narration must start with `Transfer to self: `, `Transfer to Francis: `, `Transfer to Leyna: `, `Transfer to Shared: ` respectively and the colon should be followed by the account name.
- Can only have two postings.
- The second posting must be to `Assets:Francis:Transfers:<Self || FromLeyna || FromShared>`, `Assets:Leyna:Transfers:<Self || FromFrancis || FromShared>`, `Assets:Shared:Transfers:<Self || FromFrancis || FromLeyna>` respecively.
- If it is a transfer from, the first posting amount must be positive.
- If it is a transfer to, the first posting amount must be negative.

### Owed transactions
- Must include one or more of the following tags: `owed-by-francis`, `owed-by-leyna`, `owed-by-shared`.
- Owed tag must be for another party.
- Entry must include at least one posting to an expense account or a receivables account for the party that is owed.
- Cannot post to any other party's account that is not owed.
- Can only post to an expense account for the owed party.

### Expense transaction for an item that should be covered by insurance
- Must have the `valuables` tag.
- The expense posting must include the meta `receipt` with a file path to the receipt document.

### Payslip
- Must have the `payslip` tag.
- The transaction must include the meta `payslip` with a file path to the payslip.
