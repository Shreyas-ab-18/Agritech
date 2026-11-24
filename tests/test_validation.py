import pytest
from decimal import Decimal
from app import positive_decimal, valid_date


def test_positive_decimal_accepts_positive_value():
    assert str(positive_decimal("2.50", "Area")) == "2.50"


@pytest.mark.parametrize("value", ["0", "-1", "abc", "NaN", "Infinity"])
def test_positive_decimal_rejects_invalid_values(value):
    with pytest.raises(ValueError):
        positive_decimal(value, "Area")


def test_optional_decimal_accepts_blank():
    assert positive_decimal("", "Yield", optional=True) is None


def test_valid_date_accepts_iso_date():
    assert valid_date("2024-01-15", "Sowing date").isoformat() == "2024-01-15"


def test_valid_date_rejects_invalid_date():
    with pytest.raises(ValueError):
        valid_date("not-a-date", "Sowing date")

def test_positive_decimal_rejects_database_overflow():
    with pytest.raises(ValueError):
        positive_decimal("10000.00", "Area", max_value=Decimal("9999.99"))


def test_positive_decimal_rejects_more_than_two_decimal_places():
    with pytest.raises(ValueError):
        positive_decimal("1.234", "Area")


def test_valid_date_rejects_future_date():
    from datetime import date, timedelta
    future = (date.today() + timedelta(days=1)).isoformat()
    with pytest.raises(ValueError):
        valid_date(future, "Sowing date")
