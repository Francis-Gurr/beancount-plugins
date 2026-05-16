"""Validate that the autobean shared-ratio policy matches the actual income split."""

from typing import NamedTuple

from beancount.core import account, data

__plugins__ = ("validate_shared_ratio",)


class IncorrectSharedRatio(NamedTuple):
    source: data.Meta | None
    message: str
    entry: data.Directive | None


parties: dict[str, dict[str, str | int]] = {
    "Francis": {
        "from": "Income:Francis:GrossPay",
        "to": "Assets:Francis:Bank",
        "total_income": 0,
    },
    "Leyna": {
        "from": "Income:Leyna:GrossPay",
        "to": "Assets:Leyna:Bank",
        "total_income": 0,
    },
}


def calculate_shared_ratio() -> dict[str, float]:
    francis_total_income = parties["Francis"]["total_income"]
    leyna_total_income = parties["Leyna"]["total_income"]

    max_income = max(francis_total_income, leyna_total_income)

    return {"Francis": francis_total_income / max_income, "Leyna": leyna_total_income / max_income}


def validate_shared_ratio(
    entries: data.Entries, _unused_options_map: data.Options
) -> tuple[data.Entries, list[IncorrectSharedRatio]]:
    errors: list[IncorrectSharedRatio] = []
    main_party = ""
    main_account = ""
    provided_ratio: dict[str, object] = {}

    for entry in entries:
        is_income_entry = (
            isinstance(entry, data.Transaction)
            and main_party in parties
            and main_account.startswith(parties[main_party]["to"])
            and data.has_entry_account_component(entry, parties[main_party]["from"])
        )

        if (
            isinstance(entry, data.Custom)
            and entry.type == "autobean.share.policy"
            and entry.values[0].value == "shared"
        ):
            provided_ratio = {
                "Francis": entry.meta["share-Francis"],
                "Leyna": entry.meta["share-Leyna"],
            }
        elif isinstance(entry, data.Custom) and entry.type == "journal account name":
            main_account = entry.values[0].value
            main_party = account.split(main_account)[1]
        elif is_income_entry:
            parties[main_party]["total_income"] += entry.postings[0].units.number

    actual_ratio = calculate_shared_ratio()
    if provided_ratio == {}:
        errors.append(
            IncorrectSharedRatio(
                None,
                "Shared ratio is not provided. "
                "Provide the shared ratio using the custom autobean.share.policy directive.",
                None,
            )
        )
    elif provided_ratio != actual_ratio:
        actual_ratio_str = {
            "Francis": str(actual_ratio["Francis"]),
            "Leyna": str(actual_ratio["Leyna"]),
        }
        provided_ratio_str = {
            "Francis": str(provided_ratio["Francis"]),
            "Leyna": str(provided_ratio["Leyna"]),
        }
        errors.append(
            IncorrectSharedRatio(
                None,
                f"Shared ratio is incorrect. Actual: {actual_ratio_str}, Provided: {provided_ratio_str}",
                None,
            )
        )

    return entries, errors
