"""
ITA Scrapper - A Python library for scraping ITA travel website.
"""

__version__ = "0.1.3"
__author__ = "ITA Scrapper Contributors"

from .exceptions import (
    ITAScrapperError,
    ITATimeoutError,
    NavigationError,
    ParseError,
)
from .models import (
    Airport,
    CabinClass,
    Flight,
    FlightResult,
    PriceCalendar,
    SearchParams,
    TripType,
)
from .scrapper import ITAScrapper
from .utils import (
    FlightDataParser,
    format_duration,
    get_date_range,
    is_valid_date_range,
    parse_duration,
    parse_price,
    parse_time,
    validate_airport_code,
)

__all__ = [
    "Airport",
    "CabinClass",
    "Flight",
    "FlightDataParser",
    "FlightResult",
    "ITAScrapper",
    "ITAScrapperError",
    "ITATimeoutError",
    "NavigationError",
    "ParseError",
    "PriceCalendar",
    "SearchParams",
    "TripType",
    "format_duration",
    "get_date_range",
    "is_valid_date_range",
    "parse_duration",
    "parse_price",
    "parse_time",
    "validate_airport_code",
]
