from __future__ import annotations

import io
from typing import TYPE_CHECKING

import pytest
from beancount.loader import load_string
from beancount.parser import printer

if TYPE_CHECKING:
    from collections.abc import Callable

    from beancount.core import data


@pytest.fixture
def load_doc() -> Callable[[str], tuple[data.Entries, data.Options]]:
    def _load(source: str) -> tuple[data.Entries, data.Options]:
        entries, errors, options_map = load_string(source, dedent=True)
        if errors:
            buf = io.StringIO()
            printer.print_errors(errors, file=buf)
            pytest.fail(f"Unexpected parser errors in test source:\n{buf.getvalue()}")
        return entries, options_map

    return _load
