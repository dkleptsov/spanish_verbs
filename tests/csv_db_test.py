""" Tests for CSV database """

import csv
import pytest

# Load CSV data into a list of rows
with open("sql/imperativo.csv", newline='', encoding='utf-8') as csv_file:
    csv_data = list(csv.reader(csv_file))

def test_headers() -> None:
    """
    Test that the database has headers.
    """
    assert csv_data[0] == ['verb', 'tense', 'subject', 'form', 'example']

@pytest.mark.parametrize("row", csv_data[1:])  # Exclude headers for duplicate check
def test_csv_db_for_duplicates(row) -> None:
    """ 
    Test that there are no duplicates in the database.
    """
    assert csv_data.count(row) == 1

@pytest.mark.parametrize("row", csv_data[1:])  # Exclude headers for field check
def test_all_fields_are_present(row) -> None:
    """ 
    Check that there are no empty fields in each row of the database.
    """
    for field in row:
        assert len(field) > 0, "Field is empty."

@pytest.mark.parametrize("row", csv_data[1:])  # Exclude headers for length check
def test_all_rows_are_length_5(row) -> None:
    """ 
    Check that all rows contain exactly 5 fields.
    """
    assert len(row) == 5, f"Row does not have length 5: {row}"
