"""This plugin validates that there are no unused accounts.
"""

import collections

from beancount.core import data
from beancount.core import getters
from beancount.core import account

from math import gcd

__plugins__ = ("validate_shared_ratio",)

IncorrectSharedRatio = collections.namedtuple("IncorrectSharedRatio", "source message entry")

parties = {
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


def calculate_shared_ratio(entries, unused_options_map):
    francis_total_income = parties["Francis"]["total_income"]
    leyna_total_income = parties["Leyna"]["total_income"]

    max_income = max(francis_total_income, leyna_total_income)

    return {"Francis": francis_total_income / max_income, "Leyna": leyna_total_income / max_income}


def validate_shared_ratio(entries, unused_options_map):
    errors = []
    main_party = ""
    main_account = ""
    sharePolicyEntry = None
    provided_ratio = {}

    for entry in entries:
        # check if the entry has #payslip
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
            print("custom", entry, entry.values[0].value)
            sharePolicyEntry = entry
            provided_ratio = {
                "Francis": entry.meta["share-Francis"],
                "Leyna": entry.meta["share-Leyna"],
            }
        elif isinstance(entry, data.Custom) and entry.type == "journal account name":
            main_account = entry.values[0].value
            main_party = account.split(main_account)[1]
        elif is_income_entry:
            parties[main_party]["total_income"] += entry.postings[0].units.number

    actual_ratio = calculate_shared_ratio(entries, unused_options_map)
    if provided_ratio == {}:
        errors.append(
            IncorrectSharedRatio(
                sharePolicyEntry.meta,
                "Shared ratio is not provided. Provide the shared ratio using the custom autobean.share.policy directive.",
                sharePolicyEntry,
            )
        )
    elif provided_ratio != actual_ratio:
        print("here")
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
                sharePolicyEntry.meta,
                f"Shared ratio is incorrect. Actual: {actual_ratio_str}, Provided: {provided_ratio_str}",
                sharePolicyEntry,
            )
        )

    return entries, errors
