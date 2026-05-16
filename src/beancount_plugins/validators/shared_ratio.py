"""Validate that the autobean shared-ratio policy matches the actual income split."""

from __future__ import annotations

from decimal import Decimal
from typing import NamedTuple

from beancount.core import account, data

__plugins__ = ("validate_shared_ratio",)

PLUGIN_NAME = "validate_shared_ratio"


class IncorrectSharedRatio(NamedTuple):
    source: data.Meta | None
    message: str
    entry: data.Directive | None


PARTY_ACCOUNTS: dict[str, dict[str, str]] = {
    "Francis": {
        "from": "Income:Francis:GrossPay",
        "to": "Assets:Francis:Bank",
    },
    "Leyna": {
        "from": "Income:Leyna:GrossPay",
        "to": "Assets:Leyna:Bank",
    },
}


def calculate_shared_ratio(total_income: dict[str, Decimal]) -> dict[str, Decimal]:
    max_income = max(total_income["Francis"], total_income["Leyna"])
    if max_income == 0:
        return {"Francis": Decimal(0), "Leyna": Decimal(0)}
    return {
        "Francis": total_income["Francis"] / max_income,
        "Leyna": total_income["Leyna"] / max_income,
    }


def validate_shared_ratio(
    entries: data.Entries, _unused_options_map: data.Options
) -> tuple[data.Entries, list[IncorrectSharedRatio]]:
    src = data.new_metadata(PLUGIN_NAME, 0)
    errors: list[IncorrectSharedRatio] = []
    main_party = ""
    main_account = ""
    provided_ratio: dict[str, object] = {}
    total_income: dict[str, Decimal] = {"Francis": Decimal(0), "Leyna": Decimal(0)}

    for entry in entries:
        if (
            isinstance(entry, data.Custom)
            and entry.type == "autobean.share.policy"
            and entry.values[0].value == "shared"
        ):
            meta = entry.meta or {}
            provided_ratio = {"Francis": meta["share-Francis"], "Leyna": meta["share-Leyna"]}
        elif isinstance(entry, data.Custom) and entry.type == "journal account name":
            main_account = entry.values[0].value
            main_party = account.split(main_account)[1]
        elif (
            isinstance(entry, data.Transaction)
            and main_party in PARTY_ACCOUNTS
            and main_account.startswith(PARTY_ACCOUNTS[main_party]["to"])
            and data.has_entry_account_component(entry, PARTY_ACCOUNTS[main_party]["from"])
        ):
            units = entry.postings[0].units
            if units is not None and units.number is not None:
                total_income[main_party] += units.number

    actual_ratio = calculate_shared_ratio(total_income)
    if not provided_ratio:
        errors.append(
            IncorrectSharedRatio(
                src,
                "Shared ratio is not provided. "
                "Provide the shared ratio using the custom autobean.share.policy directive.",
                None,
            )
        )
    elif provided_ratio != actual_ratio:
        actual_ratio_str = {k: str(v) for k, v in actual_ratio.items()}
        provided_ratio_str = {k: str(v) for k, v in provided_ratio.items()}
        errors.append(
            IncorrectSharedRatio(
                src,
                f"Shared ratio is incorrect. Actual: {actual_ratio_str}, Provided: {provided_ratio_str}",
                None,
            )
        )

    return entries, errors
