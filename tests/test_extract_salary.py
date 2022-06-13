from extract import extract_salary


def test_salary_range_delimiters():
    delimiters = [
        " - ",
        "-",
        " до ",
        "до",
        " — ",
        "—"
    ]
    for delimiter in delimiters:
        salary_text = f"Зарплата 100000{delimiter}200000 рублей"
        assert extract_salary(salary_text) == (100000.0, 200000.0, "rub"),\
            f"Incorrect work with delimiter: '{delimiter}'"


def test_slary_range_numbers_splited_in_the_midle():
    delimiters = [
        ".",
        ",",
        "'",
        "’",
        "`",
        " "
    ]
    for delimiter in delimiters:
        test_numbers = {
            (100000.0, 200000.0, "rub"):
                f"от 100{delimiter}000 до 200{delimiter}000 руб.",
            (50000.0, 100000.0, "rub"):
                f"от 50{delimiter}000 до 100{delimiter}000 руб.",
            (1000.0, 20000.0, "rub"):
                f"от 1{delimiter}000 до 20{delimiter}000 руб.",
            (1000.0, 2000.0, "usd"):
                f"от 1{delimiter}000 до 2{delimiter}000 usd"
        }
        for result, test_string in test_numbers.items():
            assert extract_salary(test_string) == result,\
                f"Incorrent behavior with delimiter: '{delimiter}'"
