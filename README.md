# get_salaries_from_tg_messages
Extract salary from TG messages with vacancy proposal to three columns: salary_from, salary_to and currency.
Сsv file with column "text" which contains telegram messages is expected.

## Usage:
1. Prepare virtual environment:
```sh
python3 -m venv venv
. /venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```
2. Enter the path to csv file - line 153 of extract.py
3. Run the script:
```sh
python extract.py
```
Result will be written to extracted.csv in current directory
