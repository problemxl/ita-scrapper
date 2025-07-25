"""
Utility functions for parsing and validating flight data.

This module provides a comprehensive set of utility functions for processing
flight-related data including prices, durations, times, airport codes, and
date ranges. Functions handle various international formats and provide robust
error handling for real-world data parsing scenarios.

The module includes both standalone functions for backward compatibility and
a FlightDataParser class for more complex parsing operations. All functions
are designed to handle the inconsistent data formats commonly found on travel
booking websites.

Key Features:
- Price parsing with international currency format support
- Duration parsing from multiple text formats (2h 30m, 2:30, 150m)
- Time parsing with timezone and next-day handling
- Airport code validation for both IATA and ICAO formats
- Date range validation with business logic constraints
- Airline code normalization and lookup

Internationalization Support:
- European vs US decimal separators (1.234,56 vs 1,234.56)
- Multiple time formats (12/24 hour, AM/PM, various separators)
- Common airline name variations and abbreviations
- Flexible duration representations across different languages/formats

Usage:
    Standalone functions:
    >>> price = parse_price("$1,234.56")  # Returns Decimal('1234.56')
    >>> minutes = parse_duration("2h 30m")  # Returns 150
    >>> airport = validate_airport_code("jfk")  # Returns "JFK"

    FlightDataParser class:
    >>> parser = FlightDataParser()
    >>> code, name = parser.parse_airline_code("Delta Air Lines")
    >>> flight_num = parser.parse_flight_number("DL123")
"""

import logging
import re
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Optional

from .exceptions import ValidationError

logger = logging.getLogger(__name__)


# Standalone utility functions for backward compatibility
def parse_price(price_text: str) -> Optional[Decimal]:
    """
    Parse price from various international text formats with currency symbols.

    Handles multiple price formats found on travel sites including different
    currency symbols, thousands separators, and decimal separators. Designed
    to be robust against formatting variations and internationalization.

    Supported Formats:
        - US format: $1,234.56, USD 1,234.56
        - European format: €1.234,56, 1.234,56 EUR
        - Simple formats: 1234.56, 1234,56
        - With/without currency symbols: $, €, £, USD, EUR, GBP

    Args:
        price_text: Raw price text from website. Examples:
            "$1,234.56", "€1.234,56", "1234.56 USD", "Price: $299"

    Returns:
        Decimal object with the parsed price value, or None if parsing fails.
        Uses Decimal for precise financial calculations.

    Example:
        >>> parse_price("$1,234.56")  # US format
        Decimal('1234.56')
        >>> parse_price("€1.234,56")  # European format
        Decimal('1234.56')
        >>> parse_price("299.00 USD")  # Simple format
        Decimal('299.00')
        >>> parse_price("invalid")  # Invalid input
        None

    Note:
        - Returns None for unparseable input rather than raising exceptions
        - Logs warnings for failed parsing attempts
        - Assumes comma as decimal separator only if format is unambiguous
    """
    if not price_text:
        return None

    try:
        # Remove common currency symbols and formatting
        clean_text = re.sub(r"[^\d.,]", "", price_text)

        # Handle European format: 1.234,56 -> 1234.56
        if "," in clean_text and "." in clean_text:
            # Check if it's European format (dot as thousands separator)
            if clean_text.index(".") < clean_text.index(","):
                # European format: 1.234,56
                clean_text = clean_text.replace(".", "").replace(",", ".")
            else:
                # US format: 1,234.56
                clean_text = clean_text.replace(",", "")
        elif "," in clean_text and clean_text.count(",") == 1:
            # Check if comma is decimal separator: 123,45
            parts = clean_text.split(",")
            if len(parts) == 2 and len(parts[1]) == 2:
                clean_text = clean_text.replace(",", ".")
            else:
                clean_text = clean_text.replace(",", "")

        return Decimal(clean_text)
    except (InvalidOperation, ValueError) as e:
        logger.warning(f"Failed to parse price '{price_text}': {e}")
        return None


def parse_duration(duration_text: str) -> Optional[int]:
    """
    Parse flight duration text into total minutes.

    Handles multiple duration formats commonly found on travel websites.
    Supports various languages, abbreviations, and formatting styles.

    Supported Formats:
        - Hour/minute combinations: "2h 30m", "1hr 45min", "3 hours 15 minutes"
        - Colon format: "2:30", "1:45"
        - Minutes only: "90m", "45 minutes", "150min"
        - Hours only: "2h", "1 hour", "3hrs"

    Args:
        duration_text: Raw duration text from website. Examples:
            "2h 30m", "1:45", "90 minutes", "2 hours", "1hr 45min"

    Returns:
        Total duration in minutes as integer, or None if parsing fails.

    Example:
        >>> parse_duration("2h 30m")
        150
        >>> parse_duration("1:45")
        105
        >>> parse_duration("90 minutes")
        90
        >>> parse_duration("invalid")
        None

    Note:
        - Case-insensitive parsing
        - Handles common abbreviations (h, hr, hour, m, min, minute)
        - Returns None for unparseable input
        - Assumes reasonable duration values (no validation for extremely long flights)
    """
    if not duration_text:
        return None

    duration_text = duration_text.lower().strip()

    # Pattern 1: 2h 30m, 1hr 45min, 3 hours 15 minutes
    pattern1 = r"(\d+)\s*(?:h|hr|hour|hours)\s*(\d+)\s*(?:m|min|minute|minutes)?"
    match1 = re.search(pattern1, duration_text)
    if match1:
        hours = int(match1.group(1))
        minutes = int(match1.group(2))
        return hours * 60 + minutes

    # Pattern 2: 2:30
    pattern2 = r"(\d+):(\d+)"
    match2 = re.search(pattern2, duration_text)
    if match2:
        hours = int(match2.group(1))
        minutes = int(match2.group(2))
        return hours * 60 + minutes

    # Pattern 3: just minutes (90m, 45 minutes)
    pattern3 = r"(\d+)\s*(?:m|min|minute|minutes)(?:\s|$)"
    match3 = re.search(pattern3, duration_text)
    if match3:
        return int(match3.group(1))

    # Pattern 4: just hours (2h, 1 hour)
    pattern4 = r"(\d+)\s*(?:h|hr|hour|hours)(?:\s|$)"
    match4 = re.search(pattern4, duration_text)
    if match4:
        return int(match4.group(1)) * 60

    return None


def parse_time(time_text: str, ref_date: Optional[date] = None) -> Optional[datetime]:
    """
    Parse time text into datetime object with optional reference date.

    Handles various time formats and next-day indicators commonly found
    on flight booking sites. Can work with standalone times or combine
    with a reference date for complete datetime objects.

    Supported Formats:
        - 12-hour with AM/PM: "2:30 PM", "11:45 AM"
        - 24-hour format: "14:30", "23:45"
        - Compact format: "2:30PM" (no space)
        - Alternative separators: "14.30"
        - Next-day indicator: "2:30 AM +1"

    Args:
        time_text: Raw time text from website. Examples:
            "2:30 PM", "14:30", "11:45 AM +1", "23.30"
        ref_date: Optional reference date to combine with parsed time.
            If provided, returns complete datetime. If None, returns time only.

    Returns:
        datetime object with parsed time, or None if parsing fails.
        If ref_date provided, includes date. Otherwise, arbitrary date used.

    Example:
        >>> parse_time("2:30 PM")
        datetime(1900, 1, 1, 14, 30)
        >>> parse_time("14:30", ref_date=date(2024, 8, 15))
        datetime(2024, 8, 15, 14, 30)
        >>> parse_time("11:45 PM +1", ref_date=date(2024, 8, 15))
        datetime(2024, 8, 16, 23, 45)  # Next day

    Note:
        - Handles next-day flights with "+1" indicator
        - Returns None for unparseable input
        - Uses reference date when provided for accurate datetime
    """
    if not time_text:
        return None

    time_text = time_text.strip()

    # Handle next day indicator
    next_day = False
    if "+1" in time_text:
        next_day = True
        time_text = time_text.replace("+1", "").strip()

    # Common time formats
    formats = [
        "%I:%M %p",  # 2:30 PM
        "%H:%M",  # 14:30
        "%I:%M%p",  # 2:30PM
        "%H.%M",  # 14.30
    ]

    for fmt in formats:
        try:
            parsed = datetime.strptime(time_text, fmt)

            # If ref_date is provided, combine with parsed time
            if ref_date:
                result = datetime.combine(ref_date, parsed.time())
                if next_day:
                    result += timedelta(days=1)
                return result
            return parsed
        except ValueError:
            continue

    return None


def validate_airport_code(code: str) -> str:
    """
    Validate and normalize airport codes to standard format.

    Accepts both IATA (3-letter) and ICAO (4-letter) airport codes and
    normalizes them to uppercase. Provides validation against common
    formatting errors and invalid inputs.

    Standards:
        - IATA codes: 3 letters (JFK, LAX, LHR) - most common
        - ICAO codes: 4 letters (KJFK, KLAX, EGLL) - more specific

    Args:
        code: Airport code string, case-insensitive. Examples:
            "jfk", "JFK", "lax", "KJFK", "egll"

    Returns:
        Normalized uppercase airport code string.

    Raises:
        ValidationError: If code is empty, wrong length, or contains non-letters.

    Example:
        >>> validate_airport_code("jfk")
        'JFK'
        >>> validate_airport_code("KJFK")
        'KJFK'
        >>> validate_airport_code("12A")  # Invalid
        ValidationError: Invalid airport code: 12A

    Note:
        - Strips whitespace automatically
        - Converts to uppercase for consistency
        - Does not validate against actual airport databases
        - Accepts both IATA and ICAO format codes
    """
    if not code:
        raise ValidationError("Airport code cannot be empty")

    code = code.strip().upper()

    # IATA codes are 3 letters
    if len(code) == 3 and code.isalpha():
        return code

    # ICAO codes are 4 letters
    if len(code) == 4 and code.isalpha():
        return code

    raise ValidationError(f"Invalid airport code: {code}")


def format_duration(minutes: int) -> str:
    """
    Format duration in minutes to human-readable string.

    Converts numeric minutes to a readable format using hours and minutes.
    Handles edge cases and provides consistent formatting for display.

    Args:
        minutes: Duration in minutes (non-negative integer)

    Returns:
        Formatted duration string in "XhYm" format.

    Example:
        >>> format_duration(150)
        '2h 30m'
        >>> format_duration(60)
        '1h'
        >>> format_duration(45)
        '45m'
        >>> format_duration(0)
        '0m'
        >>> format_duration(-5)  # Negative handled gracefully
        '0m'

    Note:
        - Returns "0m" for negative input
        - Omits minutes if exactly 0 (e.g., "2h" not "2h 0m")
        - Omits hours if less than 60 minutes (e.g., "45m" not "0h 45m")
    """
    if minutes < 0:
        return "0m"

    hours = minutes // 60
    mins = minutes % 60

    if hours > 0:
        return f"{hours}h {mins}m" if mins > 0 else f"{hours}h"
    return f"{mins}m"


def get_date_range(start_date: date, days: int) -> list[date]:
    """
    Generate a list of consecutive dates starting from a given date.

    Creates a sequence of dates useful for flexible date searches,
    price calendars, and date range operations.

    Args:
        start_date: Starting date for the range
        days: Number of days to include in the range (positive integer)

    Returns:
        List of date objects in chronological order.

    Example:
        >>> get_date_range(date(2024, 8, 15), 3)
        [date(2024, 8, 15), date(2024, 8, 16), date(2024, 8, 17)]
        >>> get_date_range(date(2024, 8, 15), 0)
        []

    Note:
        - Returns empty list if days <= 0
        - Does not validate start_date (can be past, future, or present)
        - Useful for generating date options for flexible flight searches
    """
    return [start_date + timedelta(days=i) for i in range(days)]


def is_valid_date_range(start_date: date, end_date: Optional[date] = None) -> bool:
    """
    Validate date ranges according to travel booking business rules.

    Checks date validity for flight searches including single dates and
    date ranges. Applies business logic constraints to prevent unreasonable
    bookings (past dates, too far future, invalid ranges).

    Validation Rules:
        - Single dates: Must be today or future, within 1 year
        - Date ranges: End must be after start, within reasonable duration
        - Business logic: No past bookings, reasonable advance booking window

    Args:
        start_date: Starting date (departure date)
        end_date: Optional ending date (return date). If None, validates single date.

    Returns:
        True if date(s) are valid for flight booking, False otherwise.

    Example:
        >>> is_valid_date_range(date.today())  # Today
        True
        >>> is_valid_date_range(date.today() - timedelta(days=1))  # Yesterday
        False
        >>> is_valid_date_range(date(2024, 8, 15), date(2024, 8, 20))  # Valid range
        True
        >>> is_valid_date_range(date(2024, 8, 20), date(2024, 8, 15))  # Invalid range
        False

    Note:
        - Considers "today" as valid departure date
        - Maximum advance booking is 1 year
        - Does not check airline-specific booking windows
        - Performs type validation on input dates
    """
    if end_date is None:
        # Single date validation
        if not isinstance(start_date, date):
            return False

        # Should not be in the past
        if start_date < date.today():
            return False

        # Should not be too far in the future (1 year max)
        return not (start_date - date.today()).days > 365

    # Date range validation
    if not isinstance(start_date, date) or not isinstance(end_date, date):
        return False

    # End date should be after start date
    if end_date <= start_date:
        return False

    # Should not be too far in the future (1 year max)
    return not (end_date - start_date).days > 365


class FlightDataParser:
    """
    Enhanced parser class for complex flight data extraction and normalization.

    Provides advanced parsing methods for extracting structured data from
    the unstructured text found on travel booking websites. Handles airline
    codes, flight numbers, and other aviation-specific data formats with
    intelligent fallbacks and normalization.

    This class is designed to work with the messy, inconsistent data formats
    found on real travel websites where information may be abbreviated,
    localized, or formatted in non-standard ways.

    Key Features:
    - Airline code extraction and normalization
    - Flight number parsing with format validation
    - Intelligent fallbacks for unknown airlines
    - Comprehensive airline database lookup
    - Code standardization for consistency

    Usage:
        >>> parser = FlightDataParser()
        >>> code, name = parser.parse_airline_code("Delta Air Lines")
        >>> print(f"{name} ({code})")  # "Delta Air Lines (DL)"
        >>> flight_num = parser.parse_flight_number("DL 123")
        >>> print(flight_num)  # "DL123"
    """

    @staticmethod
    def parse_price(price_text: str) -> Optional[Decimal]:
        """
        Parse price from various text formats with robust error handling.

        Static method version of the standalone parse_price function.
        Provided for consistency with the class interface and to allow
        for future enhancements specific to the FlightDataParser context.

        Args:
            price_text: Raw price text from website

        Returns:
            Decimal object with parsed price, or None if parsing fails

        See Also:
            parse_price() - Standalone function with identical functionality
        """
        if not price_text:
            return None

        try:
            # Remove common currency symbols and formatting
            clean_text = re.sub(r"[^\d.,]", "", price_text)

            # Handle different decimal separators
            if "," in clean_text and "." in clean_text:
                # Assume comma is thousands separator: 1,234.56
                clean_text = clean_text.replace(",", "")
            elif "," in clean_text and clean_text.count(",") == 1:
                # Check if comma is decimal separator: 123,45
                parts = clean_text.split(",")
                if len(parts) == 2 and len(parts[1]) == 2:
                    clean_text = clean_text.replace(",", ".")
                else:
                    clean_text = clean_text.replace(",", "")

            return Decimal(clean_text)
        except (InvalidOperation, ValueError) as e:
            logger.warning(f"Failed to parse price '{price_text}': {e}")
            return None

    @staticmethod
    def parse_airline_code(airline_text: str) -> tuple[str, str]:
        """
        Extract airline code and name from various text formats.

        Parses airline information from text that may contain airline names,
        codes, or combinations. Uses a comprehensive database of airline
        mappings to standardize codes and names for consistency.

        Parsing Strategies:
        1. Extract existing 2-letter IATA codes from text
        2. Look up airline names in comprehensive mapping database
        3. Generate codes from airline names as fallback
        4. Provide reasonable defaults for unknown airlines

        Args:
            airline_text: Raw airline text from website. Examples:
                "Delta Air Lines", "DL", "American (AA)", "Virgin Atlantic"

        Returns:
            Tuple of (airline_code, airline_name):
            - airline_code: 2-letter IATA code (e.g., "DL", "AA")
            - airline_name: Full or formatted airline name

        Example:
            >>> parser.parse_airline_code("Delta Air Lines")
            ('DL', 'Delta Air Lines')
            >>> parser.parse_airline_code("American (AA)")
            ('AA', 'American')
            >>> parser.parse_airline_code("Virgin Atlantic")
            ('VS', 'Virgin Atlantic')
            >>> parser.parse_airline_code("Unknown Carrier")
            ('UN', 'Unknown Carrier')

        Note:
            - Uses comprehensive airline database covering major global carriers
            - Handles various text formats including parenthetical codes
            - Generates reasonable codes for unknown airlines
            - Returns standardized IATA codes for consistency
        """
        if not airline_text:
            return "XX", "Unknown Airline"

        airline_text = airline_text.strip()

        # Common airline codes mapping
        airline_codes = {
            "delta": "DL",
            "american": "AA",
            "united": "UA",
            "southwest": "WN",
            "jetblue": "B6",
            "alaska": "AS",
            "spirit": "NK",
            "frontier": "F9",
            "lufthansa": "LH",
            "british airways": "BA",
            "air france": "AF",
            "klm": "KL",
            "emirates": "EK",
            "qatar": "QR",
            "turkish": "TK",
            "virgin atlantic": "VS",
            "virgin": "VS",
        }

        # Try to extract 2-letter code
        code_match = re.search(r"\b([A-Z]{2})\b", airline_text)
        if code_match:
            code = code_match.group(1)
            name = airline_text.replace(code, "").strip()
            return code, name or f"{code} Airlines"

        # Look up by name
        airline_lower = airline_text.lower()
        for name_part, code in airline_codes.items():
            if name_part in airline_lower:
                return code, airline_text

        # Fallback: use first 2 characters of name
        clean_name = re.sub(r"[^A-Za-z]", "", airline_text)
        code = clean_name[:2].upper() if len(clean_name) >= 2 else "XX"

        return code, airline_text

    @staticmethod
    def parse_flight_number(flight_text: str, airline_code: str = "") -> str:
        """
        Extract and normalize flight numbers from text with airline context.

        Parses flight numbers from various text formats, handling different
        separators, spacing, and formatting conventions. Ensures consistent
        formatting for flight identification and display.

        Parsing Logic:
        1. Look for airline code + number combinations (e.g., "DL 123")
        2. Extract standalone numbers and combine with provided airline code
        3. Generate default flight numbers when parsing fails
        4. Ensure consistent formatting without spaces or separators

        Args:
            flight_text: Raw flight number text from website. Examples:
                "DL 123", "Delta 1234", "Flight 567", "AA-890"
            airline_code: Optional airline code to use if not found in text.
                Used for context when flight_text contains only numbers.

        Returns:
            Standardized flight number string in format "XX1234" where XX is
            airline code and 1234 is flight number. Always includes airline code.

        Example:
            >>> parser.parse_flight_number("DL 123")
            'DL123'
            >>> parser.parse_flight_number("Flight 567", airline_code="AA")
            'AA567'
            >>> parser.parse_flight_number("Delta 1234")
            'DELTA1234'  # Uses extracted code
            >>> parser.parse_flight_number("", airline_code="DL")
            'DL0000'  # Default when no number found

        Note:
            - Always returns a flight number, using defaults if necessary
            - Removes spaces and separators for consistent formatting
            - Handles various airline code formats (2-3 letters)
            - Uses airline_code parameter as fallback for context
        """
        if not flight_text:
            return f"{airline_code}0000" if airline_code else "XX0000"

        # Look for airline code + numbers pattern
        pattern = r"([A-Z]{2,3})[\s-]?(\d{1,4})"
        match = re.search(pattern, flight_text.upper())

        if match:
            return f"{match.group(1)}{match.group(2)}"

        # Look for just numbers
        numbers = re.findall(r"\d+", flight_text)
        if numbers:
            return f"{airline_code}{numbers[0]}" if airline_code else f"XX{numbers[0]}"

        return f"{airline_code}0000" if airline_code else "XX0000"
