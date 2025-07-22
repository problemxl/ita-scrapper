"""
Tests for utility functions.
"""

from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest

from ita_scrapper.exceptions import ValidationError
from ita_scrapper.utils import (
    format_duration,
    get_date_range,
    is_valid_date_range,
    parse_duration,
    parse_price,
    parse_time,
    validate_airport_code,
)


class TestParsePrice:
    """Test price parsing function."""

    def test_simple_dollar_price(self):
        """Test simple dollar price parsing."""
        assert parse_price("$299") == Decimal("299")
        assert parse_price("$1,234.56") == Decimal("1234.56")

    def test_euro_price(self):
        """Test euro price parsing."""
        assert parse_price("€150.50") == Decimal("150.50")
        assert parse_price("€1.234,56") == Decimal("1234.56")  # European format

    def test_price_with_currency_code(self):
        """Test price with currency code."""
        assert parse_price("299 USD") == Decimal("299")
        assert parse_price("1,234 EUR") == Decimal("1234")

    def test_invalid_price(self):
        """Test invalid price returns None."""
        assert parse_price("") is None
        assert parse_price("invalid") is None
        assert parse_price("$$$") is None


class TestParseDuration:
    """Test duration parsing function."""

    def test_hours_and_minutes(self):
        """Test parsing hours and minutes."""
        assert parse_duration("2h 30m") == 150
        assert parse_duration("1hr 45min") == 105
        assert parse_duration("3 hours 15 minutes") == 195

    def test_hours_only(self):
        """Test parsing hours only."""
        assert parse_duration("2h") == 120
        assert parse_duration("1 hour") == 60

    def test_minutes_only(self):
        """Test parsing minutes only."""
        assert parse_duration("90m") == 90
        assert parse_duration("45 minutes") == 45

    def test_invalid_duration(self):
        """Test invalid duration returns None."""
        assert parse_duration("") is None
        assert parse_duration("invalid") is None


class TestParseTime:
    """Test time parsing function."""

    def test_24_hour_format(self):
        """Test 24-hour time format."""
        ref_date = date(2024, 6, 15)
        result = parse_time("14:30", ref_date)

        assert result == datetime(2024, 6, 15, 14, 30)

    def test_12_hour_format(self):
        """Test 12-hour time format."""
        ref_date = date(2024, 6, 15)
        result = parse_time("2:30 PM", ref_date)

        assert result == datetime(2024, 6, 15, 14, 30)

    def test_next_day_indicator(self):
        """Test next day indicator."""
        ref_date = date(2024, 6, 15)
        result = parse_time("2:30 AM+1", ref_date)

        assert result == datetime(2024, 6, 16, 2, 30)

    def test_invalid_time(self):
        """Test invalid time returns None."""
        ref_date = date(2024, 6, 15)
        assert parse_time("", ref_date) is None
        assert parse_time("invalid", ref_date) is None
        assert parse_time("25:00", ref_date) is None


class TestValidateAirportCode:
    """Test airport code validation."""

    def test_valid_codes(self):
        """Test valid airport codes."""
        assert validate_airport_code("jfk") == "JFK"
        assert validate_airport_code("LAX") == "LAX"
        assert validate_airport_code(" sfo ") == "SFO"

    def test_invalid_codes(self):
        """Test invalid airport codes raise errors."""
        with pytest.raises(ValidationError):
            validate_airport_code("")

        with pytest.raises(ValidationError):
            validate_airport_code("INVALID")

        with pytest.raises(ValidationError):
            validate_airport_code("12A")


class TestFormatDuration:
    """Test duration formatting function."""

    def test_minutes_only(self):
        """Test formatting minutes only."""
        assert format_duration(45) == "45m"

    def test_hours_only(self):
        """Test formatting hours only."""
        assert format_duration(120) == "2h"
        assert format_duration(60) == "1h"

    def test_hours_and_minutes(self):
        """Test formatting hours and minutes."""
        assert format_duration(150) == "2h 30m"
        assert format_duration(75) == "1h 15m"


class TestGetDateRange:
    """Test date range generation."""

    def test_date_range(self):
        """Test generating date range."""
        start = date(2024, 6, 15)
        dates = get_date_range(start, 3)

        expected = [
            date(2024, 6, 15),
            date(2024, 6, 16),
            date(2024, 6, 17),
        ]

        assert dates == expected


class TestIsValidDateRange:
    """Test date range validation."""

    def test_valid_future_date(self):
        """Test valid future date."""
        future_date = date.today() + timedelta(days=30)
        assert is_valid_date_range(future_date) is True

    def test_valid_round_trip(self):
        """Test valid round trip dates."""
        departure = date.today() + timedelta(days=30)
        return_date = departure + timedelta(days=7)
        assert is_valid_date_range(departure, return_date) is True

    def test_past_departure_date(self):
        """Test past departure date is invalid."""
        past_date = date.today() - timedelta(days=1)
        assert is_valid_date_range(past_date) is False

    def test_return_before_departure(self):
        """Test return date before departure is invalid."""
        departure = date.today() + timedelta(days=30)
        return_date = departure - timedelta(days=1)
        assert is_valid_date_range(departure, return_date) is False

    def test_too_far_future(self):
        """Test dates too far in future are invalid."""
        far_future = date.today() + timedelta(days=400)
        assert is_valid_date_range(far_future) is False
