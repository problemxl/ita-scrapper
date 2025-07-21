"""
ITA Scrapper - A Python library for scraping ITA travel website.
"""

__version__ = "0.1.0"
__author__ = "ITA Scrapper Contributors"

from .scrapper import ITAScrapper
from .models import (
    Flight,
    FlightResult,
    Airport,
    PriceCalendar,
    SearchParams,
    TripType,
    CabinClass,
)
from .exceptions import (
    ITAScrapperError,
    NavigationError,
    ParseError,
    TimeoutError,
)
from .utils import (
    parse_price,
    parse_duration,
    parse_time,
    validate_airport_code,
    format_duration,
    get_date_range,
    is_valid_date_range,
    FlightDataParser,
)

__all__ = [
    "ITAScrapper",
    "Flight",
    "FlightResult", 
    "Airport",
    "PriceCalendar",
    "SearchParams",
    "TripType",
    "CabinClass",
    "ITAScrapperError",
    "NavigationError",
    "ParseError",
    "TimeoutError",
    "parse_price",
    "parse_duration",
    "parse_time", 
    "validate_airport_code",
    "format_duration",
    "get_date_range",
    "is_valid_date_range",
    "FlightDataParser",
]
