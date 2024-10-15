import csv
import pytest


with open("sql/imperativo.csv") as csv_file:
    csv_db = list(csv.reader(csv_file))


def test_headers() -> None:
    """
    Test that database has headers.
    """
    assert csv_db[0] == ['verb','tense','subject','form','example']


@pytest.mark.parametrize("row", csv_db)
def test_csv_db_for_duplicates(row) -> None:
    """ 
    Test that there is no duplicates.
    """
    assert csv_db.count(row) == 1


@pytest.mark.parametrize("row", csv_db)
def test_all_fields_are_present(row) -> None:
    """ 
    Check that there is no empy fields in new database.
    """
    for field in row:
        assert len(field) > 0


@pytest.mark.parametrize("row", csv_db)
def test_all_rows_are_length_5(row) -> None:
    """ 
    Check that all fields in rows are present.
    """
    assert len(row) == 5