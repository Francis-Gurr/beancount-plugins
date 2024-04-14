# beancount-plugins
Custom beancount plugins

## Validate shared ratio
Calculates the correct ratio for the share policy `shared` and throws an error if it is incorrect.

1. Calculates the total income for Francis as:\
The total amount into accounts with root `Assets:Francis:Bank` from accounts with root `Income:Francis:GrossPay`
3. Calculates the total income for Leyna as:\
The total amount into accounts with root `Assets:Leyna:Bank` from accounts with root `Income:Leyna:GrossPay`
4. Calculates the income ratio `Francis:Leyna` in the form `a:b` where `(a = 1 and b < 1) or (a < 1 and b = 1)`
5. Throws an error if the calculated ratio is not the same as the ratio defined using the autobean share policy directive:
   ```
   2000-01-01 custom "autobean.share.policy" "shared"
          share-Francis: a
          share-Leyna: b
          share_enforced: TRUE
          share_prorated_included: FALSE
   ```

## Validate transactions
Validates that transactions follow certain rules.

1. Every journal should be for a real account (e.g. bank or credit card) and start with the custom directive `2000-01-01 custom "journal account name" "<account:name>".
2. For every transaction the first posting should be to the account defined by the above directive.
3. For a transaction that includes an account with the component `Transfers` it should have the appropriate required tags.
4. If a transaction posts to an account that belongs to someone else, this should have the appropriate tags.
5. Transfer transactions must follow the following rules
   - Have only one of the following tags: `transfer-to-self`, `transfer-to-francis`, `transfer-to-leyna`, `transfer-from-self`, `transfer-from-francis`, `transfer-from-leyna`.
   - The payee must be `Self`, `Francis`, `Leyna` or `Shared` respectively.
   - The narration must start with `Transfer to self`, `Transfer to Francis`, `Transfer to Leyna`, `Transfer to Shared` respectively.
   - Can only have two postings.
   - The second posting must be to `Assets:Francis:Transfers:<Self || FromLeyna || FromShared>`, `Assets:Leyna:Transfers:<Self || FromFrancis || FromShared>`, `Assets:Shared:Transfers:<Self || FromFrancis || FromLeyna>` respecively.
   - If it is a transfer from, the first posting amount must be positive.
   - If it is a transfer to, the first posting amount must be negative.
6. Owed transactions must follow the following rules:
   - Must include one or more of the following tags: `owed-by-francis`, `owed-by-leyna`, `owed-by-shared`.
   - Owed tag must be for another party.
   - Entry must include at least one posting to an expense account for the party that is owed.
   - Cannot post to any other party's account that is not owed.
   - Can only post to an expense account for the owed party.
