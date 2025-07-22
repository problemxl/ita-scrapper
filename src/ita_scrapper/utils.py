import logging
import re
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Optional

from .exceptions import ValidationError

logger = logging.getLogger(__name__)


# Standalone utility functions for backward compatibility
def parse_price(price_text: str) -> Optional[Decimal]:
    """Parse price from various text formats."""
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
    """Parse duration text to minutes."""
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
    """Parse time text to datetime object."""
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
    """Validate and normalize airport code."""
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
    """Format duration in minutes to human readable string."""
    if minutes < 0:
        return "0m"

    hours = minutes // 60
    mins = minutes % 60

    if hours > 0:
        return f"{hours}h {mins}m" if mins > 0 else f"{hours}h"
    return f"{mins}m"


def get_date_range(start_date: date, days: int) -> list[date]:
    """Get a range of dates starting from start_date."""
    return [start_date + timedelta(days=i) for i in range(days)]


def is_valid_date_range(start_date: date, end_date: Optional[date] = None) -> bool:
    """Check if date range is valid."""
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
    """Enhanced parser for flight data from different sources."""

    @staticmethod
    def parse_price(price_text: str) -> Optional[Decimal]:
        """Parse price from various text formats."""
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
        """Parse airline text to extract code and name."""
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
        """Parse flight number from text."""
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
