"""
Parse telegram messages with vacancy proposal and create 3 columns in
dataframe: salary_from, salary_to, currency.

Could be mistakes with hour rates.
"""

import pandas
import re
import numpy as np
from typing import Tuple


# For salary strings with currency marker at the end
PATTERN_1 = re.compile(
    (
        r"(?<!\d)"
        r"(\d{1,3}\ ?[.,'’`]?\d{1,3}?"
        r"\ ?[eEuUrR]?[sSuU]?[rRdDbB]?\$?т?\.?р?у?б?[кКkK]?\.?\ ?[-—д]о?\ ?\$?" # noqa
        r"\d{1,3}\ ?[,.'’`]?\d{1,3}?|\d{1,3}\ ?[.,'’`]?\d{1,3})"
        r"(\ ?[кКkK]{1,2}\W|\ ?тыс|\ ?т\.?р\.?|\ ?[тТ]\W|\ ?р\W|\ ?ру\б?|\ ?₽"
        r"|\ ?[rR][uU][bB]|\ ?\$|\ ?[uU][sS][dD]|\ ?gross|\ ? грос|\ ?net"
        r"|\ ?нет|\ ?на рук|\ ? до вычет|\ ?\€|\ ?euro|\ ?евро\.?|\ ?EUR)"
    )
)
# For salary strings with currency marker at the beginning
PATTERN_2 = re.compile(
    (
        r"(\$|\💰|\€|\₽|EUR|евро\.?|\s?[uU][sS][dD]|Вилка.\ ?|~\ )"
        r"(.?\d{1,3}\ ?[.,'’`]?\d{1,3}"
        r"\ ?\$?т?\.?р?у?б?[кКkK]?\.?\ ?[-—д]о?\ ?[eEuUrR]?[sSuU]?[rRdDbB]?\$?\ ?" # noqa
        r"\d{1,3}\ ?[,.'’`]?\d{1,3}"
        r"|\d{1,3}\ ?[.,'’`]?\d{1,3})"
    )
)
# For salary without currency marker
PATTERN_3 = re.compile(
    (
        r"(?<!\d|\/)"
        r"(\d{2,3}[.,'’` ]?\d{1,3}"
        r"\ ?[eEuUrR]?[sSuU]?[rRdDbB]?\$?т?\.?р?у?б?[кКkK]?\.?\ ?[-—д]о?\ ?\$?"
        r"\d{1,3}\ ?[,.'’`]?\d{1,3}"
        r"|\d{1,3}\ ?[.,'’`]?\d{1,3})(\n)"
    )
)
DIGIT_PATTERN = re.compile(r"\d{1,}[,.'’`]?\d*")
CURRENCY_MAP = (
    ("usd", re.compile(r"\ ?[uU][sS][dD]|\ ?доллар|\ ?\$")),
    ("eur", re.compile(r"\ ?\€|\ ?euro|\ ?евро\.?|EUR")),
    ("rub", re.compile(r".?[р₽т]|\ ?[rR][uU][bB]"))
)


def get_currency(salary_from: float,
                 salary_to: float,
                 match: str) -> str:
    """Return currency name."""
    # In case when currency is explicit
    for curr in CURRENCY_MAP:
        if re.search(curr[1], match):
            return curr[0]
    # For other cases
    length_of_salary_numbers = [
        len(x) for x in list(map(str, [salary_from, salary_to]))
    ]
    if length_of_salary_numbers[0] == 4 or length_of_salary_numbers[1] == 4:
        return "usd"
    return "rub"


def is_float(num: str) -> bool:
    return len(num) <= 3


def clean_numbers(row_salary_range: str) -> Tuple[float, float]:
    """Return tuple with salary range (from/to)."""
    substitution_map = {
        True: ".",
        False: ""
    }
    row_salary_range = row_salary_range.strip()
    row_salary_range = row_salary_range.replace(" ", "")
    salary_range = re.findall(DIGIT_PATTERN, row_salary_range)
    if not salary_range:
        return (np.nan, np.nan)
    for i in range(0, len(salary_range)):
        substitute_to = substitution_map[is_float(salary_range[i])]
        salary_range[i] = re.sub("[.,'’`]", substitute_to, salary_range[i])
    salary_range = list(map(float, salary_range))
    if len(salary_range) < 2:
        return (salary_range[0], np.nan)
    return (salary_range[0], salary_range[1])


def format_short_nubbers(salary_value: float, currency: str) -> float:
    """Return new salary in case of salary_value is shortened."""
    if salary_value and currency == "rub" and salary_value < 1000:
        return salary_value * 1000
    elif salary_value and salary_value < 10:
        return salary_value * 1000
    return salary_value


def drop_irrelevant(salary_from: float,
                    salary_to: float,
                    currency: str):
    """Drop irrelevant values"""
    if currency == "rub" and salary_from < 20000:
        if salary_to is np.nan or salary_to < 20000:
            return (np.nan, np.nan, np.nan)
    if salary_from < 150:
        return (np.nan, np.nan, np.nan)
    return (salary_from, salary_to, currency)


def extract_salary(text: str) -> Tuple[float, float, float]:
    """Return tuple with range of salary and its currency."""
    match = None
    for pattern in [PATTERN_1, PATTERN_2, PATTERN_3]:
        match = re.search(pattern, text)
        if match:
            break
    if not match:
        return (np.nan, np.nan, np.nan)
    salary_from, salary_to = clean_numbers(match.group(0))
    if salary_from > salary_to or salary_from > 800000 or salary_from <= 0:
        return (np.nan, np.nan, np.nan)
    currency = get_currency(salary_from, salary_to, match.group(0))
    salary_from = format_short_nubbers(salary_from, currency)
    salary_to = format_short_nubbers(salary_to, currency)
    return drop_irrelevant(salary_from, salary_to, currency)


def load_and_extract(path: str,
                     delimiter: str = ",",
                     write_to_file: bool = False) -> pandas.DataFrame:
    """
    Load data from csv file and extract salary information.

    Return pandas.DataFrame by default. Use write_to_file = True to save
    result to csv file in current directory.
    """
    df = pandas.read_csv(path, delimiter=delimiter)
    df["salary_from"], df["salary_to"], df["currency"] = zip(
        *df["text"].map(extract_salary)
    )
    if write_to_file:
        df.to_csv("extracted.csv")
    return df


if __name__ == "__main__":
    path = ""  # fill the path to csv file
    df = load_and_extract(path, delimiter=";", write_to_file=True)
    if df is not None:
        found_num = df["Index"].count() - df["currency"].isna().sum()
        print(f"Extracted {found_num} salaries.")
