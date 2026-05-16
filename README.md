# beancount-plugins

Custom validators for a [beancount v3](https://github.com/beancount/beancount) ledger.

Enforces conventions for a two-party shared-finance ledger: opening balances, transfers, owed (cross-party) transactions, payslips, valuables/receipts, balance assertions, and events. See each module's docstring under [`src/beancount_plugins/validators/`](src/beancount_plugins/validators/) for the specific rules.

## Use in your ledger

```bash
uv pip install "beancount-plugins @ git+https://github.com/Francis-Gurr/beancount-plugins.git"
```

```beancount
plugin "beancount_plugins.validators.shared_ratio"
plugin "beancount_plugins.validators.transactions"
```

## Development

```bash
uv sync                    # install runtime + dev dependencies
uv run pytest              # run the test suite
uv run ruff check .        # lint
uv run ruff format .       # format
uv run ty check            # type-check
uv run pre-commit install  # one-time: install the git pre-commit hook
```

## License

[MIT](LICENSE).
