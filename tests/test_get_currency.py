import numpy as np
import pytest

from extract import get_currency


def data_for_currency_recognition():
    currency_map = {
        "rub": ("RUB", "rub", "Rub", "₽", "р", "р.", "т.р.", "тр", "тр."),
        "usd": ("USD", "usd", "Usd", "$"),
        "eur": ("EUR", "euro", "евро", "евро.", "€")
    }
    test_cases = []
    for currency, currency_markers_array in currency_map.items():
        for currency_marker in currency_markers_array:
            test_arguments = [
                [currency, 100000, np.nan, f"100000{currency_marker}"],
                [currency, 10000, np.nan, f"10000 {currency_marker}"],
                [currency, 100000, 200000, f"100000-200000 {currency_marker}"],
                [currency, 1000, 2000, f"1000-2000{currency_marker}"]
            ]
            test_cases.extend(test_arguments)
    test_cases.extend([
        ["usd", 300, 1000, "300-1000"],
        ["usd", 6000, 10000, "6000-10000 gross"]
    ])
    for currency, salary_from, salary_to, test_string in test_cases:
        yield (
            currency,
            get_currency(salary_from, salary_to, test_string),
            test_string
        )


@pytest.mark.parametrize("expected, result, test_string",
                         data_for_currency_recognition())
def test_currency_recognition(expected, result, test_string):
    assert expected == result,\
        f"Currency recognition failed on '{test_string}'"
